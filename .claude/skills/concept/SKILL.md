---
name: concept
description: Teach a lecture concept from the course materials (green zone). Usage - /concept universal hashing
---
Teach the concept named in the arguments. Rules:
1. Open the matching lecture notes in `course_site_raw/Lectures/` (use `mutool draw -F txt`) and the CLRS chapter listed in `course_site_raw/SCRAPE_NOTES.md`. Teach from those, in the course's notation.
2. Start by asking Carlos to state what he already thinks the concept is, in two sentences. Wait.
3. Then: definition, the one theorem that matters, the proof technique used, and one worked example that is NOT from a live homework. Prefer CLRS exercises or recitation problems.
4. End with one question he must answer in writing (by hand is fine) before the next step.
5. Save a short note to `study/concepts/<topic>.md` only if he asks.
Never connect the concept to a specific live homework problem, even if he asks "so for 2(b)...". Redirect: "Work that on paper; bring the attempt to /critique."

## Logging (mandatory)
At the end of the session, if the work touched a homework, run `tools/log.sh N concept "<one-line process summary>"`. Process only: which mode, which attempt, counts of gaps named, anything refused. Never quote the problem, his claims, or any math. The log is published on nymo.finance.
