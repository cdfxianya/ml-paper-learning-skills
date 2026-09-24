---
name: ml-paper-study
metadata:
  version: "2.2.0"
description: Help users learn ML papers deeply enough to present and defend their ideas through evidence-grounded reviewer/author subagent debate, targeted prerequisite teaching, understanding checks, persistent learning memory, and a presentation handoff. Use for guided ML paper reading and study; not for a quick summary, generic ML questions, or slide production alone.
---

# ML paper study

## Outcome and priorities

Help the learner explain the problem, mechanism, evidence, and limitations in their own words and answer substantive follow-up questions. Debate is a teaching instrument, not the deliverable's centerpiece. Spend resources where they improve understanding; remove repeated summaries and performative disagreement rather than imposing rigid token or round limits.

Use the user's language. Do not assume their expertise, audience, talk duration, or visual preferences. This skill is self-contained: do not load or imitate a teacher skill by default. If a genuine teaching-design uncertainty remains, first present three alternatives, then consult only the relevant local teacher instructions if available, preserving this workflow and the user's choices.

## Start or resume

1. Read [memory protocol](references/memory.md). Load the small shared profile and the current paper checkpoint; load topic records only as needed. Existing user facts should not be asked again. State relevant assumptions briefly; ask only for missing information that changes the next step.
2. Identify the paper and version. If missing, request its file, title, or link; do not fabricate a paper. Obtain accessible full text and figure/table evidence before making specific claims. If access is partial, label the scope and defer unsupported judgments. Use suitable document tools for extraction and inspect relevant figures rather than relying solely on extracted captions.
3. Establish a shared source file/index once: title, version, section/page convention, figures, tables, equations, and accessible supplement. Prefer the original text plus a small locator index over a long duplicated summary. Distinguish printed pages from PDF page indices. Agents may inspect the source independently as needed.
4. Give the learner a short logic map: problem → prior bottleneck → design → proposed mechanism → evidence → boundary. Mark uncertain links. This is an initial map, not a final verdict. Lightly clarify audience/time when needed; if unknown, use a provisional roughly 10-minute technical peer presentation without saving that assumption as a preference.

## Evidence-grounded debate

Read [debate protocol](references/debate.md). Spawn exactly two persistent subagents when available: reviewer and author-perspective interpreter, with no inherited conversation context (`fork_turns="none"` where supported). This skill explicitly requests their delegation; no further subagents are needed. Give each the minimum task context, source location, and necessary excerpts, not the full chat or full user memory. On their first pass, withhold the main agent's interpretation and the other agent's conclusions: each independently supplies a few claims, evidence locators, and uncertainties before cross-examination. While they inspect evidence, the main agent prepares the source map, learner-facing reading path, or understanding checks.

Default to three distinct rounds: (1) problem/motivation, (2) mechanism/design, (3) evidence/limits. A round means reviewer challenge, author response, and main-agent adjudication. Reuse the agents across rounds. Merge resolved topics; add a fourth or further focused round when a consequential unresolved issue can benefit from new evidence or reasoning. Do not continue when the paper cannot answer or discussion adds no information.

The main agent checks key claims against source evidence; agreement is not proof. On a consequential disagreement, explain the prerequisite and invite learner engagement without requiring them to choose a side. Show compact dispute summaries by default; save concise claims/evidence/outcomes, not a verbose theatrical transcript or hidden reasoning.

If subagents are unavailable, disclose that constraint and use clearly labeled sequential perspectives, retaining source verification. Never claim independent-agent review in this fallback.

## Teach at the point of need

### Ongoing learner interaction

Guided study is a multi-turn learning conversation, not an opening question followed by an uninterrupted report. Read [assessment and correction](references/assessment.md) before teaching, not only when a prerequisite gap appears. Background/audience questions do not count as understanding checks; subagent questions and answers do not count as learner participation.

Track learning checkpoints for problem/motivation, mechanism/design, evidence/limits, and final teach-back. Before advancing the learner-facing explanation beyond each of the first three areas, use one meaningful paper-specific question unless the learner has already demonstrated that understanding in their own contribution or explicitly waived that checkpoint. This applies even when no remedial supplement was needed. Questions may be merged when one genuine answer covers multiple areas; do not repeat a check merely to satisfy a count. A correct answer in one area does not waive later areas.

Explain one coherent learning segment, then ask one substantive question in the final response and end the turn to let the learner answer. Do not immediately provide its answer, invent a learner reply, or continue through later learning checkpoints in that response. On the next turn, address the actual reply, repair gaps if needed, then move to the next segment and its checkpoint. Independent source inspection and subagent debate may proceed before yielding; their completion does not advance the learner's progress. If the user requests a direct explanation, give it, and assess later with a fresh application rather than withholding it.

Distinguish interaction state from mastery. Save `interaction` with `stage`, `awaiting_answer`, `pending_question`, and `checkpoints` keyed by area, each recording `status` (pending/answered/demonstrated_in_dialogue/waived), `evidence`, and `check_id` when assessed. Silence means pending, not waiver or completion. “Continue” with a pending question may waive that question only; a global no-questions mode requires an explicit request. Resume the pending learning position without repeating completed background questions. Finish with the teach-back invitation and wait unless it was explicitly waived; a draft report can be supplied earlier but must not be presented as completed learning.

Before the paper map, supply only prerequisites essential to understanding the overall problem. During reading, supply missing concepts immediately before the formula, design, or experiment that needs them. Before exposing a difficult dispute, supply the concepts needed to understand it. During teach-back, repair gaps as they appear.

Consult memory as provisional evidence, not a verdict. If a gap is uncertain, ask one relevant low-pressure question; allow “unfamiliar.” Teach with intuition, a concrete example, and a derivation only where useful. Return explicitly to the paper: what does this concept let us understand here? Agent research does not automatically become a lesson for the user.

After a substantive supplement, usually use one short application check: explain the role in their own words, predict a changed design's effect with reasons, or locate supporting experimental evidence. Read [assessment and correction](references/assessment.md) for checks and when a learner disputes an explanation. Before asking, identify two or three observable criteria and relevant misconceptions, grounded in the paper. Choose a fresh formulation rather than asking for verbatim repetition. Accept reasonable alternative predictions, distinguishing hypotheses from observed results. Do not ask all checks mechanically. Record actual answer evidence, assistance level and transfer context; a correct answer after key hints does not demonstrate independent presentation ability. Do not produce arbitrary numerical mastery scores.

- Accurate explanation tied to this paper: continue and record the narrow demonstrated capability.
- Correct result but unclear reasoning: repair the specific gap and briefly recheck.
- Cannot explain: change representation or step back one prerequisite.
- Repeated difficulty: avoid endless testing; offer a workable intuitive account and mark unresolved depth and its downstream consequence.
- Explicitly skipped check: record the scoped waiver and unverified mastery, then continue. Silence or an unanswered check remains pending: yield rather than auto-advance the lesson. Independent source work may continue without declaring learner progress. Save a checkpoint if the interaction ends.

## Reading and reporting outputs

Read [handoff specification](references/handoff.md) when preparing synthesis or presentation materials. Deliver the user's four questions with paper-specific evidence:

1. What precisely is the problem, including inputs/outputs, setting, and prior bottleneck?
2. What are the core innovations? Separate author claims, demonstrated contribution, and novelty not independently verified.
3. What can reviewers challenge? Pair each substantive challenge with the strongest source-supported reply and residual gap.
4. What deserves close reading, skimming, or conditional skipping? Point to actual sections/equations/figures and say what the learner should gain and when to revisit skipped material.

Also explain mechanism via bottleneck → design → expected effect → evidence. Adapt to theory, method, and empirical papers. Do not default to “skip related work”; it may establish the central distinction.

Invite a roughly 3–5 minute learner explanation or equivalent short chunks. Assess the coherent problem–method–evidence chain, one key design/formula, one important result, and a limitation. Ask only the most informative follow-ups, often two or three initially; repair observed gaps. Default completion means the learner can explain design choices and handle substantive questions, not reproduce experiments or memorize a script. If teach-back is skipped, deliver materials with readiness unverified.

Update memory and checkpoint at meaningful milestones and on interruption using the bundled memory script. Give a compact summary of new persistent facts without seeking routine reconfirmation. Do not imply memory was saved unless the write succeeded. Resolve pending correction repairs before reusing affected topic assessments or presentation content; a detected error requires checking downstream records, not merely revising the current reply.

## After learning: research opportunities

After the learning workflow is complete (or the user explicitly waives remaining checks), read the research-opportunity section in [handoff specification](references/handoff.md) and propose a few concrete directions for a potential follow-up paper. Do not interrupt a pending learning question with this expansion. When checks were waived, retain unverified readiness and label the analysis as based on paper evidence rather than demonstrated learner mastery. Use the paper's limits, unresolved disputes and the learner's expressed interests or resources. Default to three meaningfully different directions; prefer fewer strong ideas to padded suggestions. Identify testable hypotheses, smallest useful experiments, novelty uncertainty and failure conditions. These are research candidates, not publication guarantees. Save them with the paper's handoff and a concise `research_directions` session entry so later work can resume without repeating ideation. Do not automatically run experiments or launch a broad literature review.

## Cost and scope controls

Use a small shared issue ledger and source index; pass deltas and unresolved questions between rounds. Do not repeat whole-paper summaries, recreate agents each round, or load every memory file. Suggested question counts are starting points, never ceilings on useful learning. Research supplements, pivotal citations, or official code when a core judgment needs them; label their provenance separately. Do not run experiments, conduct a broad literature review, or generate a deck by default. Report actual usage only when available; do not estimate total token usage from output length. Check learning value rather than minimizing tokens at any cost.
