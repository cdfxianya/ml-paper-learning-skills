"""Validate and export teaching/provenance graphs. No semantic or online verification."""
import argparse
import html
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit


class GraphError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise GraphError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def texts(record, fields, location):
    require(isinstance(record, dict), location + " must be an object")
    for field in fields:
        require(nonempty(record.get(field)), location + "." + field + " must be nonempty text")


def choice(value, values, location):
    require(value in values, location + " has an unsupported value")


def indexed(items, location):
    require(isinstance(items, list), location + " must be an array")
    result = {}
    for item in items:
        texts(item, ("id",), location)
        key = item["id"]
        require(re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", key), "Use simple ASCII IDs: " + key)
        require(key not in result, "Duplicate ID: " + key)
        result[key] = item
    return result


def references(value, papers, location, required=False):
    require(isinstance(value, list), location + " must be an array")
    require(all(isinstance(x, str) and x in papers for x in value), location + " has an unknown source")
    require(not required or bool(value), location + " requires a source")


def readable(paper):
    return paper["access"] in ("full_text", "partial")


def validate(data):
    require(isinstance(data, dict) and data.get("schema_version") == 1, "Expected schema_version 1")
    target = data.get("target")
    texts(target, ("title", "scope", "status"), "target")
    choice(target["status"], ("partial", "complete"), "target.status")
    papers = indexed(data.get("papers"), "papers")
    stages = indexed(data.get("stages"), "stages")
    relations = indexed(data.get("relations"), "relations")
    require(not set(papers).intersection(stages), "Paper and stage IDs must be distinct")
    references(target.get("source_ids"), papers, "target.source_ids")
    for key, paper in papers.items():
        texts(paper, ("title", "version", "access", "expansion"), key)
        choice(paper["access"], ("full_text", "partial", "metadata_only", "unavailable"), key + ".access")
        choice(paper["expansion"], ("expanded", "frontier", "blocked", "not_needed"), key + ".expansion")
        if paper["expansion"] != "expanded":
            texts(paper, ("stop_reason",), key)
        url = paper.get("url")
        require(url is None or url == "" or (isinstance(url, str) and urlsplit(url).scheme in ("http", "https") and bool(urlsplit(url).netloc)), key + ".url must be an HTTP(S) URL or empty")
    for key, edge in relations.items():
        texts(edge, ("from", "to", "type", "status", "detail"), key)
        require(edge["from"] in papers and edge["to"] in papers, key + " references an unknown paper")
        require(edge["from"] != edge["to"], key + " cannot cite itself")
        choice(edge["type"], ("cites", "inherits", "uses_component", "compares", "background", "related"), key + ".type")
        choice(edge["status"], ("verified", "unverified"), key + ".status")
        evidence = edge.get("evidence")
        require(isinstance(evidence, list), key + ".evidence must be an array")
        witnesses = set()
        for item in evidence:
            texts(item, ("paper_id", "locator", "note"), key + ".evidence")
            require(item["paper_id"] in papers, key + " evidence source missing")
            witnesses.add(item["paper_id"])
        if edge["status"] == "verified":
            required = {edge["from"]}
            if edge["type"] in ("inherits", "uses_component", "related"):
                required.add(edge["to"])
            require(required <= witnesses, key + " lacks endpoint evidence")
            require(all(readable(papers[x]) for x in required), key + " cannot be verified from metadata alone")
    for key, stage in stages.items():
        texts(stage, ("title", "kind", "input", "output", "operation", "training_note", "limitations"), key)
        choice(stage["kind"], ("pedagogical", "documented", "target"), key + ".kind")
        references(stage.get("source_ids"), papers, key + ".source_ids", stage["kind"] != "pedagogical")
    transitions = data.get("transitions")
    restoration = data.get("restoration")
    require(isinstance(transitions, list), "transitions must be an array")
    require(isinstance(restoration, list), "restoration must be an array")
    adjacency = {key: [] for key in stages}
    indegree = dict.fromkeys(stages, 0)
    pairs = set()
    for edge in transitions:
        texts(edge, ("from", "to", "change", "reason", "basis"), "transition")
        require(edge["from"] in stages and edge["to"] in stages, "Transition references an unknown stage")
        pair = edge["from"], edge["to"]
        require(pair not in pairs, "Duplicate transition")
        pairs.add(pair)
        choice(edge["basis"], ("paper", "derivation", "teaching_choice"), "transition.basis")
        references(edge.get("source_ids"), papers, "transition.source_ids", edge["basis"] != "teaching_choice")
        adjacency[edge["from"]].append(edge["to"])
        indegree[edge["to"]] += 1
    queue = [key for key, count in indegree.items() if count == 0]
    visited = 0
    while queue:
        node = queue.pop()
        visited += 1
        for child in adjacency[node]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    require(visited == len(stages), "Teaching route has a cycle")
    for item in restoration:
        texts(item, ("item", "status", "note"), "restoration")
        require(type(item.get("critical")) is bool, "Restoration critical must be boolean")
        choice(item["status"], ("restored", "deferred", "not_applicable"), "restoration.status")
        require(item.get("stage_id") is None or item["stage_id"] in stages, "Restoration stage missing")
        if item["status"] == "restored":
            require(item.get("stage_id") in stages, "Restored item needs its restoration stage")
    if target["status"] == "complete":
        targets = {key for key, stage in stages.items() if stage["kind"] == "target"}
        require(targets, "Complete route needs a target stage")
        reaches_target = set(targets)
        while True:
            extended = reaches_target | {key for key, children in adjacency.items() if set(children).intersection(reaches_target)}
            if extended == reaches_target:
                break
            reaches_target = extended
        require(reaches_target == set(stages), "Complete route has a stage disconnected from its target")
        require(restoration, "Complete route needs a restoration checklist")
        require(not any(x["critical"] and x["status"] != "restored" for x in restoration), "Critical mechanism has not been restored")
        require(target["source_ids"] and all(readable(papers[x]) for x in target["source_ids"]), "Complete route requires accessible target text")
    return data


def cell(value):
    return html.escape(str(value), quote=True).replace("|", "&#124;").replace("\r", " ").replace("\n", " ")


def label(value):
    return cell(value).replace("\\", "&#92;")[:180]


def render(data):
    validate(data)
    pids = {paper["id"]: "p" + str(i) for i, paper in enumerate(data["papers"])}
    sids = {stage["id"]: "s" + str(i) for i, stage in enumerate(data["stages"])}
    status = {"verified": "已核验", "unverified": "未核验"}
    kind = {"pedagogical": "教学简化", "documented": "文献模型", "target": "目标范围"}
    expansion = {"expanded": "已展开", "frontier": "待展开", "blocked": "受阻", "not_needed": "无需展开"}
    types = {"cites": "引用", "inherits": "继承", "uses_component": "采用机制", "compares": "比较", "background": "背景", "related": "补充关联"}
    lines = ["# " + cell(data["target"]["title"]), "", "范围：" + cell(data["target"]["scope"]), "", "路线状态：" + ("完成" if data["target"]["status"] == "complete" else "部分完成"), "", "## 教学路线", "", "箭头表示讲解中的变化顺序，不表示真实研发历史。", "", "```mermaid", "flowchart LR"]
    for stage in data["stages"]:
        lines.append(f'  {sids[stage["id"]]}["{label(stage["title"])} · {kind[stage["kind"]]}"]')
    if not data["stages"]:
        lines.append('  empty["尚未形成可支持的教学路线"]')
    for edge in data["transitions"]:
        lines.append(f'  {sids[edge["from"]]} -->|"{label(edge["change"])}"| {sids[edge["to"]]}')
    lines += ["```", "", "| 阶段 | 输入 → 输出 | 操作与训练说明 | 局限 | 来源 |", "|---|---|---|---|---|"]
    for stage in data["stages"]:
        lines.append("| " + " | ".join(cell(x) for x in (stage["id"] + ": " + stage["title"], stage["input"] + " → " + stage["output"], stage["operation"] + "；" + stage["training_note"], stage["limitations"], ", ".join(stage["source_ids"]))) + " |")
    lines += ["", "## 文献依据图", "", "箭头从引用方/后继指向来源；补充关联不表示直接引用。这里只记录本次追溯范围。核验状态由阅读证据支持，导图工具不核验论文内容。", "", "```mermaid", "flowchart TD"]
    for paper in data["papers"]:
        lines.append(f'  {pids[paper["id"]]}["{label(paper["title"])} · {expansion[paper["expansion"]]}"]')
    if not data["papers"]:
        lines.append('  empty["尚未取得可登记的来源"]')
    for edge in data["relations"]:
        connector = "-->" if edge["status"] == "verified" else "-.->"
        lines.append(f'  {pids[edge["from"]]} {connector}|"{types[edge["type"]]} · {status[edge["status"]]}"| {pids[edge["to"]]}')
    lines += ["```", "", "| ID | 来源 / 版本 | 可访问范围 | 展开情况及原因 |", "|---|---|---|---|"]
    for paper in data["papers"]:
        title = cell(paper["title"])
        if paper.get("url"):
            safe_url = paper["url"].replace("<", "%3C").replace(">", "%3E").replace("\n", "").replace("\r", "")
            title = f'[{title.replace("[", "&#91;").replace("]", "&#93;")}](<{safe_url}>)'
        lines.append(f'| {cell(paper["id"])} | {title} / {cell(paper["version"])} | {cell(paper["access"])} | {expansion[paper["expansion"]]}：{cell(paper.get("stop_reason", ""))} |')
    lines += ["", "| 关系 | 类型 / 状态 | 说明 | 原文依据 |", "|---|---|---|---|"]
    for edge in data["relations"]:
        evidence = "；".join(item["paper_id"] + " " + item["locator"] + ": " + item["note"] for item in edge["evidence"])
        lines.append("| " + " | ".join(cell(x) for x in (edge["from"] + " → " + edge["to"], types[edge["type"]] + " / " + status[edge["status"]], edge["detail"], evidence or "待核验")) + " |")
    lines += ["", "## 恢复核对", "", "| 简化项 | 关键项 | 状态 | 恢复阶段 | 说明 |", "|---|---|---|---|---|"]
    for item in data["restoration"]:
        lines.append("| " + " | ".join(cell(x) for x in (item["item"], "是" if item["critical"] else "否", item["status"], item.get("stage_id") or "", item["note"])) + " |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "render"))
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        with args.input.open(encoding="utf-8-sig") as stream:
            data = json.load(stream)
        validate(data)
        if args.action == "render":
            require(args.output is not None and args.output.suffix.lower() == ".md", "Provide --output maps.md")
            require(args.output.resolve() != args.input.resolve(), "Output cannot overwrite graph input")
            content = render(data)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(dir=args.output.parent, prefix=".graph-", suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as stream:
                    stream.write(content)
                os.replace(temporary, args.output)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        print(json.dumps({"valid_structure": True, "semantic_verification": "agent_required", "output": str(args.output) if args.action == "render" else None}, ensure_ascii=False))
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({"valid_structure": False, "error": str(error)}, ensure_ascii=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
