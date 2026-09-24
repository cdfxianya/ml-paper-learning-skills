# ML Paper Learning Skills

两个面向机器学习论文学习的 Codex skill，分别支持互动研读与连贯讲授，帮助使用者理解论文中的问题、设计、推理与证据。

## 选择哪一个

| Skill | 适合的需求 | 学习方式 |
|---|---|---|
| [ml-paper-study](skills/ml-paper-study/SKILL.md) | 读懂论文并准备自主汇报、回答追问 | 作者视角与审稿人视角的子代理辩论，主代理核查证据、按需补讲，与使用者进行理解检查和试讲 |
| [model-deconstruction](skills/model-deconstruction/SKILL.md) | 从基础理解复杂模型，尽量少被问答打断 | 沿理解依赖寻找有效简化形态，用贯穿例子逐步恢复模型，把关键概念与推理展开讲清 |

论文研读模式会回答问题、创新点、可被质疑之处和精读路线，并在学习完成后提出有条件的研究方向。拆解模式分别保存教学路线与文献依据图，不把教学中间态伪装成真实历史前身。

两者都要求结论有依据；讲义完整、代理达成一致或代码检查通过，都不代表使用者已经掌握。两者可独立安装，也可先用拆解模式补足模型理解，再进入论文研读。

## 安装

本仓库保留完整 skill 目录，包括 `SKILL.md`、参考材料、脚本和界面配置。[OpenAI 官方说明](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use)支持使用 `$skill-installer` 从其他仓库安装 skill。

在 Codex 中输入下面这段话，将“本仓库的 GitHub 地址”替换为实际地址：

```text
使用 $skill-installer，从【本仓库的 GitHub 地址】安装两个 skill：
skills/ml-paper-study
skills/model-deconstruction
```

也可以只安装其中一个。安装后在技能列表中选择它；若尚未出现，按所用版本的提示刷新或重新启动 Codex。

## 使用示例

提供论文 PDF、论文链接或足够明确的论文信息，然后输入：

```text
使用 $ml-paper-study 帮我学习这篇 ML 论文。
我希望能自主汇报问题、方法、证据和局限，并回答追问。
```

```text
使用 $model-deconstruction，以拆解模式讲懂这个模型。
从容易理解的简化形态开始，用同一个例子逐步讲回完整模型。
把关键概念和推理讲透，尽量连贯讲授，保留文献依据图。
```

对某处不理解时，可以直接指出“这一步到下一步还没有跟上”；已熟悉的部分也可以要求压缩。

## 运行条件与学习记录

- 适用于能读取文件、执行本地脚本并检索论文来源的 Codex 环境。论文或工具不可访问时，skill 会说明限制。
- 附带脚本使用 Python 3.9+ 标准库，不需要额外 Python 依赖。
- `ml-paper-study` 在可用时调用两个子代理；缺少子代理能力时应说明并采用顺序视角分析，不能声称完成了独立代理审核。
- `model-deconstruction` 默认由主代理连贯讲授，不要求反复作答。
- 持久化学习记录存于安装目录之外，优先复用使用者指定的位置；没有配置时按当前用户环境选择并告知实际目录。仓库不包含个人档案或论文学习记录。
- 如果在此仓库中试用，将生成的讲义、图谱等放在 `outputs/`，临时材料放在 `work/`；这些目录已在 `.gitignore` 中排除。论文 PDF 与个人记录也应留在仓库之外。

## 维护

目录结构：

```text
skills/
  ml-paper-study/
    SKILL.md
    agents/
    references/
    scripts/
  model-deconstruction/
    SKILL.md
    agents/
    references/
    scripts/
```

从仓库根目录可运行现有脚本测试：

```text
python -B -m unittest discover -s skills/ml-paper-study/scripts -p test_memory.py
python -B -m unittest discover -s skills/model-deconstruction/scripts -p test_graph.py
```

这些测试检查记录处理与图谱结构，不检验教学效果或论文事实。首次发布副本基于 `ml-paper-study` 2.2.0 与 `model-deconstruction` 1.1.0，已将原安装中的个人绝对路径改为按使用者环境解析。

## 许可证

此发布副本尚未指定许可证，由仓库维护者在发布时选择并添加 `LICENSE`。
