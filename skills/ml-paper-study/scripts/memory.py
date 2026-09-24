"""Small standard-library memory store. Never grades a learner's answer."""
import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import time
import hashlib


class MemoryError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    with open(path, encoding="utf-8-sig") as stream:
        return json.load(stream)


def target(root, relative):
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise MemoryError("Use a relative path within the memory root")
    result = (root / relative).resolve()
    if not result.is_relative_to(root.resolve()) or result.suffix != ".json":
        raise MemoryError("Target must be a JSON file within memory root")
    parts = relative.parts
    if not (parts == ("profile.json",) or
            (len(parts) == 2 and parts[0] == "topics") or
            (len(parts) == 3 and parts[0] == "papers" and parts[2] == "session.json")):
        raise MemoryError("Unsupported memory record path")
    return result


def validate(data):
    if not isinstance(data, dict) or data.get("schema_version") not in (1, 2):
        raise MemoryError("Expected an object with schema_version 1 or 2")
    revision = data.get("revision", 0)
    if type(revision) is not int or revision < 0:
        raise MemoryError("Invalid revision")
    graph_ids = set()
    for field in ("facts", "capabilities", "checks", "claims", "artifacts", "corrections", "repair_tasks"):
        if field not in data:
            continue
        entries = data[field]
        if not isinstance(entries, list):
            raise MemoryError(field + " must be a list")
        seen = set()
        for entry in entries:
            if not isinstance(entry, dict):
                raise MemoryError(field + " entries must be objects")
            if data["schema_version"] == 1 and field != "facts" and not entry.get("id"):
                continue  # Legacy records receive deterministic IDs on successful migration.
            key = (entry.get("key"), entry.get("scope")) if field == "facts" else entry.get("id")
            if (field == "facts" and (not all(isinstance(x, str) and x for x in key))) or (field != "facts" and (not isinstance(key, str) or not key)):
                raise MemoryError(field + " entries need stable identifiers")
            if key in seen:
                raise MemoryError("Duplicate identifier in " + field)
            seen.add(key)
            if field in ("claims", "checks", "artifacts", "capabilities"):
                if key in graph_ids:
                    raise MemoryError("Dependency IDs must be unique across collections")
                graph_ids.add(key)
            if "depends_on" in entry and (not isinstance(entry["depends_on"], list) or not all(isinstance(x, str) for x in entry["depends_on"])):
                raise MemoryError("depends_on must contain IDs")
            if field == "checks" and data["schema_version"] == 2:
                required = ("question", "criteria", "answer_evidence", "result", "assistance", "transfer", "depends_on")
                if any(name not in entry for name in required):
                    raise MemoryError("Check is missing assessment evidence fields")
                if entry["assistance"] not in ("independent", "light_hint", "key_step_hint", "full_explanation", "unknown"):
                    raise MemoryError("Invalid assistance level")
                if entry["result"] not in ("pass", "partial", "needs_repair", "unverified", "needs_reassessment"):
                    raise MemoryError("Invalid check result")
                if entry["transfer"] not in ("same_example", "new_application", "later_recall", "not_checked"):
                    raise MemoryError("Invalid transfer evidence")
                if not isinstance(entry["criteria"], list) or not entry["criteria"]:
                    raise MemoryError("Checks need explicit criteria")
                if entry["result"] == "pass" and not entry["answer_evidence"]:
                    raise MemoryError("A passed check requires answer evidence")


KEYED = {"facts", "capabilities", "checks", "claims", "artifacts", "corrections", "repair_tasks"}


def merge(old, patch):
    if not isinstance(patch, dict):
        raise MemoryError("Patch must be a JSON object")
    result = deepcopy(old)
    for key, value in patch.items():
        if key in KEYED:
            if not isinstance(value, list):
                raise MemoryError(key + " must be a list")
            entries = deepcopy(result.get(key, []))
            def identity(item):
                return (item.get("key"), item.get("scope")) if key == "facts" else item.get("id")
            for item in value:
                if not isinstance(item, dict):
                    raise MemoryError("Expected object entry")
                index = next((i for i, existing in enumerate(entries) if identity(existing) == identity(item)), None)
                if index is None:
                    entries.append(deepcopy(item))
                else:
                    entries[index] = merge(entries[index], item)
            result[key] = entries
        elif isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


@contextmanager
def locked(root, timeout=2):
    root.mkdir(parents=True, exist_ok=True)
    lock = root / ".memory.lock"
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise MemoryError("Memory is locked; input remains unapplied. Retry later; do not delete another session's lock.")
            time.sleep(0.05)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump({"pid": os.getpid(), "created_at": now()}, stream)
        yield
    finally:
        lock.unlink()


def atomic_write(path, data):
    validate(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, filename = tempfile.mkstemp(dir=path.parent, prefix=".pending-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        validate(read_json(filename))
        os.replace(filename, path)
    finally:
        if os.path.exists(filename):
            os.unlink(filename)


def correct(data, correction):
    required = ("id", "claim_id", "replacement", "source", "reason")
    if any(not correction.get(key) for key in required):
        raise MemoryError("Correction needs id, claim_id, replacement, source, reason")
    if any(c["id"] == correction["id"] for c in data.get("corrections", [])):
        raise MemoryError("Correction ID already exists")
    claim = next((c for c in data.get("claims", []) if c["id"] == correction["claim_id"]), None)
    if claim is None:
        raise MemoryError("Unknown claim ID")
    previous = deepcopy(claim)
    claim.update(text=correction["replacement"], source=correction["source"], status="corrected")
    affected = {claim["id"]}
    entries = [(field, entry) for field in ("claims", "checks", "artifacts", "capabilities") for entry in data.get(field, [])]
    changed = True
    while changed:
        changed = False
        for field, entry in entries:
            if entry["id"] not in affected and affected.intersection(entry.get("depends_on", [])):
                affected.add(entry["id"])
                entry["result" if field == "checks" else "status"] = "needs_reassessment" if field == "checks" else "needs_review"
                changed = True
    event = dict(correction, previous=previous, affected_ids=sorted(affected), updated_at=now())
    data.setdefault("corrections", []).append(event)
    data.setdefault("repair_tasks", []).append({"id": correction["id"] + ":repair", "status": "pending", "affected_ids": sorted(affected), "instruction": "Review referenced topic memories, learner judgments and report/slide artifacts; repair content before marking complete."})
    data["readiness"] = {"status": "needs_reassessment", "reason": correction["id"]}
    return data


def update(root, relative, patch, expected_revision, correction=False):
    path = target(root, relative)
    with locked(root):
        old = read_json(path) if path.exists() else {"schema_version": 2, "revision": 0}
        validate(old)
        if old.get("revision", 0) != expected_revision:
            raise MemoryError("Revision conflict; reload and merge intentionally")
        # Migrate only on successful write. Preserve all original fields.
        data = deepcopy(old)
        if data["schema_version"] == 1:
            if "readiness" in data:
                data["legacy_readiness"] = deepcopy(data["readiness"])
                data["readiness"] = {"status": "needs_reassessment", "reason": "Legacy assistance and readiness evidence need review"}
            for field in KEYED - {"facts"}:
                for index, entry in enumerate(data.get(field, [])):
                    fingerprint = hashlib.sha256(json.dumps(entry, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]
                    entry.setdefault("id", f"legacy-{field}-{index}-{fingerprint}")
            for capability in data.get("capabilities", []):
                if capability.get("status") in ("mastered", "demonstrated_here") and "assistance" not in capability:
                    capability["legacy_status"] = capability["status"]
                    capability["status"] = "needs_review"
                    capability["assistance"] = "unknown"
            for check in data.get("checks", []):
                check.setdefault("assistance", "unknown")
                check.setdefault("transfer", "not_checked")
                check.setdefault("criteria", ["Legacy assessment; criteria not recorded"])
                check.setdefault("answer_evidence", "")
                check.setdefault("question", "Legacy check")
                check.setdefault("depends_on", [])
                if not check["answer_evidence"] and check.get("result") not in ("needs_repair", "needs_reassessment"):
                    check["result"] = "unverified"
        data = correct(data, patch) if correction else merge(data, patch)
        data.update(schema_version=2, revision=expected_revision + 1, updated_at=now())
        if any(task.get("status") != "done" for task in data.get("repair_tasks", [])):
            data["readiness"] = {"status": "needs_reassessment", "reason": "Pending correction repairs"}
        atomic_write(path, data)
        return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("action", choices=("load", "summary", "update", "correct"))
    parser.add_argument("record")
    parser.add_argument("--input", help="UTF-8 JSON patch/correction file; kept on failure")
    parser.add_argument("--expected-revision", type=int)
    args = parser.parse_args()
    try:
        root = Path(args.root).resolve()
        if args.action in ("update", "correct"):
            if args.input is None or args.expected_revision is None:
                raise MemoryError("Writes require --input and --expected-revision (0 for new/v1 records)")
            data = update(root, args.record, read_json(args.input), args.expected_revision, args.action == "correct")
            output = {"saved": True, "revision": data["revision"], "record": args.record, "repair_tasks": data.get("repair_tasks", [])}
        else:
            data = read_json(target(root, args.record))
            validate(data)
            output = data if args.action == "load" else {key: data[key] for key in ("schema_version", "revision", "paper", "phase", "next_action", "pending_question", "interaction", "readiness", "repair_tasks", "facts", "topic_index") if key in data}
        print(json.dumps(output, ensure_ascii=False))
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({"saved": False, "error": str(error)}, ensure_ascii=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
