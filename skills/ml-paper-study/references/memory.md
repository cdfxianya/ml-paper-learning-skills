# Persistent memory and resumption

## Location and access

Keep runtime memory outside the installed skill so updates do not erase it. Use an explicitly configured memory root if provided. If no root is configured, resolve the current user's Documents/Codex directory and use its `ml-paper-study-memory` subdirectory when available; otherwise choose an accessible, user-owned persistent location outside the installed skill. Tell the user the resolved location, record it in the task checkpoint, and reuse it on resume. Do not reuse a path belonging to another person or create a second store when an existing configured store is available. Obtain required filesystem permission before writes outside permitted roots. If persistence is blocked, save a portable checkpoint in the workspace and report the limitation.

Only learn from this skill's interactions and records the user supplies or explicitly authorizes. Do not search unrelated chats or user files for a profile. Store concise relevant evidence, not entire conversations or sensitive incidental details. User requests to inspect, correct, export, or delete these records must be supported; resolve and verify exact paths before removal.

## Minimal structure, created only as needed

- `profile.json`: shared preferences, habitual audiences/durations, and topic index.
- `topics/<topic-id>.json`: capabilities with specific scope and evidence; unresolved prerequisite gaps.
- `papers/<paper-id>/session.json`: source identity/version, this talk's context, progress, issue ledger, learning checks, next action, and handoff file locations.
- Paper-specific user-facing reading/handoff files: store in the task's deliverable directory; record absolute locations in the session. Do not duplicate paper binaries by default.

Use a stable DOI/arXiv identifier with filesystem-safe punctuation, or a short title plus year. Preserve the version in the source record. Reuse the same paper record on resume; if source version changes, flag affected prior conclusions for recheck. Never silently blend different papers or versions.

## Record conventions

JSON is UTF-8 with `schema_version: 2` and an integer `revision`. Existing version 1 files remain readable and migrate only on successful writes; missing historical assistance stays unknown. Keep absent facts absent or null. Each profile fact has `key`, `value`, `origin` (explicit/inferred), `evidence`, `updated_at`, and `scope`. Inferences are provisional; a one-off request is scoped to its paper and must not become a durable preference automatically. Explicit corrections supersede older conflicting facts.

Each topic capability has a stable `id`, `concept`, `capability`, `context`, `status` (self_reported/explained_unverified/demonstrated_here/needs_repair/needs_review), `evidence`, `paper_id`, and `updated_at`; link `check_id` and preserve `assistance` when assessed. Store separate capabilities for intuitive explanation, interpreting evidence, derivation, and implementation when relevant. One correct answer is not proof of durable general mastery; familiar concepts in a new demanding context may need a small check. Before trusting a capability, inspect pending correction repairs in its source paper session, loading only relevant records.

A session records:

- Paper identity, version, source path/URL and locator convention.
- Audience/time/goals, distinguishing explicit settings from working assumptions.
- Current phase, completed source work and rounds, issue ledger, outstanding evidence needs.
- Concepts supplemented, learner checks and scoped outcomes, readiness status and evidence.
- Precise next action, pending user question if any, and artifact locations.
- `interaction`: learner-facing stage, `awaiting_answer`, `pending_question`, and per-area checkpoint status/evidence. Keep this separate from completed agent debate rounds. Read it on resume; unanswered questions remain pending, not implicitly skipped. `summary` includes it.

Read the profile plus this session first, then relevant topic entries only. Resume from the checkpoint; do not redo completed rounds. Agent IDs from an old process may be invalid: recreate roles only as needed with a compact checkpoint, without claiming their old state survived.

## Safe updates

Only the main agent writes shared memory. Use `scripts/memory.py` with a Python 3.9+ runtime; it uses only the standard library. It validates and merges under a root lock, checks revisions, validates a temporary file and atomically replaces the destination. Corrupt existing files, conflicts and occupied locks fail without replacing the record. Input patch files remain available for retry; do not report failed writes as saved. Do not delete another process's lock because it appears old. Do not create empty topic or paper records before a paper is supplied.

Examples (replace the explicit paths and record IDs; use PowerShell `&` before a quoted Python executable):

```text
python <skill-dir>/scripts/memory.py --root <memory-root> load profile.json
python <skill-dir>/scripts/memory.py --root <memory-root> summary papers/<paper-id>/session.json
python <skill-dir>/scripts/memory.py --root <memory-root> update papers/<paper-id>/session.json --input <workspace>/patch.json --expected-revision 0
python <skill-dir>/scripts/memory.py --root <memory-root> correct papers/<paper-id>/session.json --input <workspace>/correction.json --expected-revision 3
```

Read before writing; use the returned revision, or 0 for a new/version-1 record. Never blindly retry a conflict with a new revision: reload and reconcile the proposed changes. `facts` merge by `(key, scope)`; `claims`, `checks`, `artifacts`, `capabilities`, `corrections` and `repair_tasks` merge by stable `id`. Empty keyed lists do not erase records. Other arrays are intentionally replaced, so include their full intended contents. Null is an explicit value, not deletion. Preserve IDs across edits and use IDs unique across session collections for dependency tracking. The tool does not expose deletion; when the user requests removal, inspect the exact target and perform a deliberate scoped edit or deletion.

Register central claims with `id`, `text`, `source`, and `depends_on`. Register report/slide artifacts with `id`, `path`, `depends_on` and `status`. Checks follow [assessment fields](assessment.md). A correction input contains `id`, `claim_id`, `replacement`, `source`, and `reason`. `correct` records the previous claim, flags transitive dependencies, invalidates readiness and queues a repair task. The agent must finish cross-file repairs; the script never claims to have rewritten an external document. Read the session's pending repairs before loading potentially stale topic records or continuing presentation work.

Write at meaningful milestones, not every utterance. A failed write is not saved memory. Briefly expose material new memories so the user can correct them. If the user skips a check, retain unverified status rather than upgrading mastery. Never invent a preferred audience, duration, expertise level, or slide style from this skill's defaults.
