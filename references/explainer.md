# Explainer blocks

Every message that asks you, the operator, to read and decide opens with an explainer block. Its
job is understanding: what is happening, what was found or built, and what you decide now. The
technical detail follows it, unchanged.

## The register switch

The register comes from one line in your `HOUSE_RULES.md`:

```
Explainer register: STE-80
```

Set it to `STE-80` or `plain-language`. When the line is missing, the register is STE-80. Every
workflow that reads this file follows it: `/atlas:research`, `/atlas:feature-workflow`, and
`/atlas:launch-supervisor` with the supervisor window it boots.

## The block

```
**Explainer (<register>)**
3–6 sentences: the situation, what was found or built, what you decide now, and the recommendation.

<optional diagram>

…the message's technical content, unchanged…
```

- **First in the message**, before any detail.
- **The label** names the register, so you can compare the two on your own runs. Text written for
  other people, such as PR descriptions or a ledger's summary for QA and product, carries no label.
- **Length:** 3–6 sentences. If it needs more, the decision is not clear yet.
- **Facts stay exact.** Work item ids, numbers, file names and `file:line` references survive; the
  register changes the sentences, never the facts.

## Register: STE-80

About 80% of the way to ASD-STE100, the Simplified Technical English standard written for
aerospace maintenance manuals:

- One idea per sentence.
- At most 20 words in an instruction, 25 in a description.
- Active voice in instructions. Imperative, simple present, simple past and simple future only.
- No progressive (-ing) verb forms, except as part of a technical name.
- Noun clusters of three words at most.
- A list for anything parallel; at most six sentences in a paragraph.
- Keep "the", "a" and "this"; do not drop small words to save space.
- Swap: ensure → make sure, utilize → use, prior to → before, commence → start,
  approximately → about, in order to → to, subsequently → then.
- Technical names (classes, flags, commands, product names) stay as they are. There is no
  dictionary check: that is the 20% relaxation.

## Register: plain-language

Jargon-free prose in product terms, the way you would explain it to a colleague who has not seen
the code. Same 3–6 sentence limit, without the STE word and verb restrictions.

## Diagrams

Add one only when a flow, a state change, a structure, or a screen is easier to see than to read.
Never diagram the message's own outline.

- **ASCII** in chat and in Markdown documents, under 80 columns where possible.
- **SVG** only inside a file that renders it.
- **Unsettled UI behaviour** (feature workflow, Phase 0): an ASCII wireframe of the assumed
  interaction, with its states side by side, for example collapsed and expanded.

## Gates

| Gate | Where | The explainer covers | Diagram |
|---|---|---|---|
| R1 | research: the document's Summary | the answer | where it lives and how it flows, when 2+ components |
| R2 | research: findings in chat | the answer, the scope, the recommended exit | — |
| K1 | feature workflow: Phase 0 scope questions | what research found, why each question matters | wireframe when a UI interaction is unsettled |
| K2 | feature workflow: Phase 4 plan gate | what will be built, what changes for users, the decision | the plan's Design diagram |
| K3 | feature workflow: READY FOR YOU | what changed, the verdict, what to smoke-test, whether the work item can close | — |
| K4 | feature workflow: feedback triage | what the reviewer asked, what will be applied | — |
| K5 | feature workflow: RUN COMPLETE | what shipped, what remains | — |
| K6 | feature workflow: any halt that needs a decision | why the run stopped, the choice | — |
| M1 | launch-supervisor: before-work decisions | each decision's evidence and recommendation | — |
| M2 | launch-supervisor: hand-off message | what the supervisor window does first | — |
| M3 | supervisor window: spec gate | what the spec commits to and leaves out | feature map |
| M4 | supervisor window: each slice's plan gate | what the slice builds, how it fits | the slice in the feature |
| M5 | supervisor window: each PR verdict | what the slice changed, the verdict, what to check | — |
| M6 | supervisor window: any halt that needs a decision | why it stopped, the choice | — |

Not included: one-line status notices (an agent started or finished, a PR opened) and
agent-to-agent artifacts such as plans, kickoff prompts and the dossier's RESUME BLOCK.
