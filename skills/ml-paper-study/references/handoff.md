# Learning report and presentation handoff

## Reading report

Lead with the problem and a short explanation of the full argument. Answer the four required questions in SKILL.md and explicitly show the mechanism and evidence links. Cite precise paper locations for substantive claims. Distinguish authors' claims, what results support, interpretation, and unknowns. Supply only disputes that matter to understanding or presenting; full conversational logs are not required.

Use a reading route whose entries contain: source locator, priority (close read/skim/defer), question to answer, and revisit condition for deferred material. Select it based on this paper and the learner's goal, not a universal section ranking.

End with readiness supported by learner behavior, remaining gaps, and the next useful action. Distinguish independent explanations from performance after hints or a complete worked answer. If no learner checks occurred, say presentation readiness is unverified. A polished generated script is not evidence that the learner can deliver it. Register generated artifacts and their claim dependencies in session memory; resolve pending correction repairs before describing these files as current or the learner as ready.

## Reusable presentation packet

Create a compact, editable handoff alongside the report; combine them if that avoids duplication. Read current style preferences and this paper's settings. Unknown preferences remain unknown; use labeled working defaults without making the learner repeat already known information.

Include:

- Paper citation/version, audience, duration, language, and applied style preferences with their provenance.
- Narrative sequence linking problem, gap, design, evidence, limits, and implications.
- For each proposed slide: main claim, source section/figure/table, necessary visual or equation, explanation notes, and likely question with supported answer. Adapt slide count to the actual content and time; do not prescribe one universally.
- Figure/table provenance and accessible asset locations when available; never invent saved image paths or numerical results. Indicate assets still needing extraction.
- Known learner difficulties, important transitions, unresolved scientific issues, and material to place in backup slides.
- What has been checked through learner explanation versus only prepared by the agent.

Do not render a deck during reading unless requested. When later asked to generate PPT, use an available presentation skill, pass this packet and the profile, and ask only for missing or conflicting decisions. Preserve distinction between study readiness and deck completion.

## Research opportunities after completion

Once teaching and teach-back are complete, or their remaining checks have explicitly been waived, append a concise research-opportunity section. If a learner answer is still pending, defer this section; do not substitute research ideation for learning. Read the final issue ledger and evidence first. Reuse facts already established instead of having both agents reread the paper or running another full debate.

Default to three substantively different candidates. Each should contain:

1. A precise research question and its motivation in this paper, with a section, figure, assumption or unresolved issue as the anchor.
2. A testable hypothesis and the proposed change or investigation. Distinguish an observed limitation from a conjecture; missing experiments alone do not establish a publishable problem.
3. A minimum useful test: appropriate baseline, data or evaluation setting, key metric or diagnostic, and the ablation/control needed to distinguish competing explanations. Adapt this to theoretical or empirical work; do not force an architecture tweak onto every paper.
4. What supporting and disconfirming outcomes would look like. Explain what result would justify deeper work and when to stop or rethink.
5. The possible contribution, closest known related work, and novelty status. If making current novelty claims, perform a focused search using primary sources and cite the relevant work. Otherwise explicitly mark novelty as unchecked and identify search terms/comparisons for later validation. Never promise acceptance or assume no prior art merely because this paper omits it.
6. Main risks and a qualitative resource estimate with assumptions. Use known learner constraints; do not invent available GPUs, data access or expertise, and do not interrupt completion with a long questionnaire.

Rank candidates briefly by likely learning/research value, feasibility and evidence strength; recommend the most useful first experiment rather than assigning fake acceptance probabilities. Surface overlapping directions as one candidate. A negative result or evaluation study may be more meaningful than adding another module. Offer fewer ideas if the evidence supports fewer, explaining the limit.

Store direction IDs, source claim IDs, hypothesis, first test, novelty status and next action in the session's `research_directions` list. This is an ordinary array in the memory tool: include the full intended list when updating. Add the handoff artifact's claim dependencies so corrections also flag affected research suggestions for review. Actual experiments, extensive literature work and paper drafting start only when requested.
