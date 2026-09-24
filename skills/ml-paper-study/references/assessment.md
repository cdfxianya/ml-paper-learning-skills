# Assessment evidence and correction

## Short, fair checks

Before posing an important check, identify two or three observable criteria tied to the source and likely misconceptions. Keep this a compact rubric, not a hidden numerical score. Distinguish factual requirements from questions permitting multiple defensible predictions. If a question or its expected answer is ambiguous, repair it before assessing the learner. Do not record a defective question as learner failure.

Give targeted feedback on the answer's reasoning and evidence, not fluency or terminology. Usually one meaningful check per learning area suffices, not one check for the entire paper; deepen where the reply reveals a consequential gap. Check motivation, mechanism, and evidence as the learner reaches each area even if no prerequisite teaching was needed. A substantive spontaneous learner explanation may satisfy the corresponding checkpoint, with its evidence recorded; “understood” alone does not. Permit consultation of the paper. Record whether an answer used independent reasoning, a light hint, a key-step hint or a full explanation. Independent means no answer-specific hint for this check; reading the paper is allowed. A check immediately after a lesson can show local understanding but not durable retention.

An unanswered question is an open interaction, not a completed assessment. Ask in the final response and yield; never answer it yourself as if the learner responded. On return, respond to the learner's reasoning before asking the next question. If the user asks a clarification, answer it and keep the relevant checkpoint open, changing the question if necessary. Avoid rapid-fire questioning or repeating every question after a clarification. User control takes precedence: an explicit local skip waives only that check, while an explicit request for uninterrupted explanation can waive checks for its stated scope. Final teach-back remains pending unless covered by that scope or separately waived.

Use a hint, different example, worked step, or direct explanation as needed. Honor requests for direct explanation; do not require repeated failure or refuse answers as a teaching doctrine. A skip is unverified, not a failure. When later checking independent performance, change the example or let it arise naturally in a later teach-back rather than administering repetitive quizzes.

Each saved check has a stable `id`, `question`, `criteria`, concise `answer_evidence`, `result`, `assistance`, `transfer`, and `depends_on` claim IDs. Allowed values:

- `result`: pass, partial, needs_repair, unverified, needs_reassessment.
- `assistance`: independent, light_hint, key_step_hint, full_explanation, unknown.
- `transfer`: same_example, new_application, later_recall, not_checked.

Include criterion-level findings in optional `findings` and misconceptions in `gaps`. Do not save unnecessary verbatim conversation. A pass with help must retain that qualification in the topic record and handoff. Topic capabilities may reference `check_id` and `assistance`; do not collapse mixed performance into a global ability label.

## Correction workflow

1. When challenged or when new evidence conflicts, inspect the relevant source and distinguish factual error, misleading analogy, ambiguous question, and different user intent. Acknowledge the concern without automatically declaring either party correct.
2. For a confirmed factual error, state the old claim, corrected claim, source and reason briefly. Use the memory tool's `correct` action with a unique correction ID and the central claim ID. The script preserves the old claim and transitively marks linked checks/claims/artifacts for review; it creates a durable repair task and invalidates readiness. It does not rewrite prose or grade the learner.
3. Inspect the returned affected IDs plus any undeclared dependencies in the text. Repair relevant debate conclusions, reading notes, and slide content. Reconsider learner judgments: a learner who correctly objected must not retain a failure caused by the tutor's mistake.
4. Inspect linked topic files using the paper's topic index/check references, update only affected capabilities through the memory tool, and preserve unrelated demonstrated abilities. External topic records and Markdown files are not updated automatically. Pending repair tasks must be checked on resume before those records are trusted.
5. Record the verified repair locations and evidence in the task, and set its status to `done` only when all necessary updates succeeded. Reassess readiness from surviving or new learner evidence; marking a repair done alone does not demonstrate mastery. If interrupted, keep the task pending and identify stale outputs to the learner.

For an unsuitable analogy or changed learning goal with no false factual claim, adjust teaching and record only consequential changes; avoid inventing a factual correction event. This workflow repairs real errors without turning each ordinary clarification into a large audit.
