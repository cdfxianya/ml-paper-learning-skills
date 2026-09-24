# 来源追溯、图谱与续学

## 只沿有用的依赖递归

从目标论文与关键模块对应的引用上下文开始。先看引用原因，再读候选被引文献的相关定义、公式或方法段，必要时扩大阅读。正文无法支持继承时，仅保留引用关系。引用数据库可发现候选和元数据，但不能代替核验原文，也不能证明引用完整。

优先官方论文、作者材料和官方代码/文档。针对新颖性、历史来源或不确定技术事实按需检索原始来源；本 skill 不强制寻找最早优先权。博客可以帮助组织例子，但事实仍回溯到可信来源。区分论文定义与某实现变体。

每个待展开分支说明它将解决哪个理解问题。去重时优先 DOI/arXiv 标识，并保留版本；同一工作不同版本的关键差异不能静默合并。遇到已访问节点不再递归，保留图中的交叉边。若出现循环或版本异常，检查记录后保留实际关系，不强制伪造成树。

停止条件：足够解释当前依赖、基础已覆盖、与本次目标无关、证据不可访问，或进一步追溯不改变讲解。记录具体理由。被阻断不等于没有前身；未核验关系不得悄悄变为已核验。持续保存原文位置、来源版本和简短释义，避免只留下链接。

## 两类图

文献依据图的箭头从后继/引用方指向来源，关系类型明确区分 cites、inherits、uses_component、compares、background、related。related 是外部补充关联，不表示有直接引用。图谱允许多个父节点、交叉引用和多个起点。

教学路线的箭头从基础形态指向恢复后的形态，表示教学变化，不表示历史。阶段可以分支合并，但应无循环；反复迭代的模型可以讲清一个迭代单元及其展开，不用把教学图画成循环。pedagogical 节点直标教学简化，documented 节点是文献支持的模型，target 是指定范围下的目标。

## deconstruction.json 约定

使用 UTF-8 JSON，`schema_version: 1`。以下是字段说明，不是待填充的用户输出；没有资料的字段如实留空或标记未知，不杜撰示例论文。

| 顶层字段 | 内容 |
|---|---|
| target | title、scope、source_ids、status（partial 或 complete） |
| papers | id、title、url（可为空）、version、access（full_text/partial/metadata_only/unavailable）、expansion（expanded/frontier/blocked/not_needed）、stop_reason |
| relations | id、from、to、type、status（verified/unverified）、detail、evidence 数组 |
| stages | id、title、kind、input、output、operation、training_note、source_ids、limitations |
| transitions | from、to、change、reason、basis（paper/derivation/teaching_choice）、source_ids |
| restoration | item、critical（布尔）、status（restored/deferred/not_applicable）、stage_id（可为空）、note |

ID 使用简短稳定的 ASCII 标识，如 p1、s1、r1；教学节点与论文节点互不混用。relation.from/to 引用 paper ID；transition.from/to 引用 stage ID。每条 evidence 含 paper_id、locator 和 note（原文内容的简短释义，不是隐藏推理）。

verified 的关系必须有引用方可访问正文中的依据，不能只凭数据库或参考文献表断言继承。对于 inherits/uses_component，还要有被引方相关方法内容的核验，两个端点各有证据；短证据至少写清继承/使用了什么。cites 可用原文参考文献条目核验，不能因此升级成 inherits。全文不可访问时可用实际读到的相关段落（access=partial），但不能假装读过未获取的部分。

documented/target 阶段应引用相关来源；pedagogical 阶段可无来源，需明确教学操作和局限。transition 的 basis=paper 或 derivation 应有来源；teaching_choice 不声称实际作者做过此步骤。工具验证关联和字段，公式正确性与来源释义仍由主代理核对。

target.status=complete 要求存在 target 阶段，恢复清单非空且无关键 deferred 项，目标关键来源至少有可访问相关正文。不要通过空清单或把关键项标记为不适用规避恢复核对。partial 状态可以交付目前可支持的路线，并解释缺口。

## 文件操作

在工作区写新文件，确认 JSON 可读取并通过检查后再替换已有记录；保留未知字段与用户编辑。避免多个代理同时写同一记录。重复使用同一论文时加载当前图谱与版本信息，而非全量重建。

```text
python <skill-dir>/scripts/graph.py check <deconstruction.json>
python <skill-dir>/scripts/graph.py render <deconstruction.json> --output <maps.md>
```

生成 maps.md 包含两张图、关系证据表、阶段表和恢复表。引用边“已核验”仅表示主代理依据原文作出的标记，脚本不会联网核验。图中显示 frontier/blocked 等边界；图谱是本次有目的的追溯，不是完整引用数据库。文件过大时保留可读主图，将次要分支拆成附图并维持完整 JSON 记录，不删掉事实关系来美化图。

session.json 保存目标与版本、交付路径、已讲阶段 ID、讲解完成状态、下一步、被阻断来源和实际用户问题。讲解完成与掌握验证分开；新模型的学习状态不写入安装文件，也不修改其他 skill 的全局偏好。旧讲解被纠正时同步更改阶段、边证据、恢复表及 lesson.md，再导出图谱。
