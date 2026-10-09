---
name: critique
description: Review Carlos's handwritten attempt at a homework by rubric, naming gaps without filling them. Usage - /critique hw4 [attemptK]
---
Critique mode. Read `CLAUDE.md` hard rules 1 and 3 first.
1. Check `hw/hwN/STATUS`. If `live`: STRICT mode. If `graded`: use /postmortem instead.
2. Read the problem statement (`hw/hwN/hwN.pdf` via mutool) and the photos in `hw/hwN/attempts/attemptK/` (latest K unless given). Read images with the Read tool.
3. For each part, produce a report with exactly these headings:
   - **What you claimed** (restate his claim in one line; if the claim itself is unclear, say so)
   - **Structure**: is there a stated claim, a stated technique, a conclusion? Are all cases covered? Does the argument prove the claim as stated, or something weaker/different?
   - **Rigor gaps**: list steps that are asserted without justification, inequalities manipulated without checking sign/direction, specific numbers used where a general argument is required, quantifiers mishandled (∃ vs ∀), base cases missing. Quote the line. Do NOT say what the correct step is.
   - **Knowledge gaps**: concepts he seems not to have, phrased as questions he should take to lecture notes, CLRS, or Sorrell's office hours ("Do you know what a potential function needs to satisfy?"). Do not answer them here.
   - **Confidence**: your estimate of how much credit this part would get, and why.
4. Write the report to `hw/hwN/feedback/attemptK.md` and show it.
5. Then DISCUSS: he can ask about any concept, and you may teach the concept in general (as /concept would), with examples that are not this problem. If he asks for the fix, the direction, or "is it X?", decline in one sentence and point to the concept instead.
6. Tell him to attempt again on paper. Next attempt goes in attempt{K+1}.

## Logging (mandatory)
At the end of the session, if the work touched a homework, run `tools/log.sh N critique "<one-line process summary>"`. Process only: which mode, which attempt, counts of gaps named, anything refused. Never quote the problem, his claims, or any math. The log is published on nymo.finance.
