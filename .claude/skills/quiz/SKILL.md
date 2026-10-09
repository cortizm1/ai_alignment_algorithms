---
name: quiz
description: Exam-style quiz on a topic, one question at a time, Socratic (green zone). Usage - /quiz amortized analysis
---
Run a quiz on the topic in the arguments.
1. Source questions from: practice midterm (`course_site_raw/PracticeExams/`), recitations, CLRS exercises, past GRADED homeworks (check `hw/hwN/STATUS`), lecture notes. Never from a live homework.
2. ONE question per message. Mix: definitions, true/false with justification, "prove this small lemma", "give a counterexample", "state the recurrence".
3. Do not reveal the answer until Carlos has committed to one. If he says "I don't know", ask a smaller sub-question instead of answering.
4. After he answers: grade it like a TA (correct / partially / wrong), say precisely what was missing in the justification, then give the model answer.
5. Keep a tally. At the end write `study/quizzes/<date>-<topic>.md` with the questions, his answers, and the gaps.

## Logging (mandatory)
At the end of the session, if the work touched a homework, run `tools/log.sh N quiz "<one-line process summary>"`. Process only: which mode, which attempt, counts of gaps named, anything refused. Never quote the problem, his claims, or any math. The log is published on nymo.finance.
