# How AI is used in my 601.433 homework

Course rule (syllabus, Ethics §3): outside resources including LLMs may be used to understand
course material, never to get answers to homework questions. Writeups must be written entirely
by the student.

My contract with the tool (enforced by the harness in this repo, `CLAUDE.md`):

1. Every problem is attempted by hand, on paper, before any AI session touches it.
2. The tool reads my photographed attempt and names gaps (unjustified step, missing case,
   quantifier error). It never says how to fix them. I attempt again on paper.
3. The tool teaches concepts from the lecture notes and CLRS, using examples that are not
   homework problems. It quizzes me. It will not answer "so for problem 2(b)…".
4. The tool types my final handwritten pages into LaTeX verbatim. Math is not changed.
   Illegible or suspicious lines are flagged in red for me to resolve by hand.
5. Web search is disabled in the harness. The tool cannot look anything up.
6. After a homework is graded and official solutions are released, I use the tool freely
   to compare my writeup with the solutions and extract lessons.

Each homework page below holds the per-session log the tool is required to append to.
Entries record the mode, the attempt number, and counts. They never contain problem text,
my claims, or any math, because publishing solutions is itself forbidden (syllabus §4).

The logs are published encrypted, commitment-style. At submission time the log is frozen and
committed with a Pedersen commitment over ristretto255: C = m·G + r·H, where m is the SHA3-256
of the report and r a random blinding factor. C is published here before the deadline. The
report itself is published encrypted with ChaCha20-Poly1305 under a fresh 256-bit key, with C
as associated data. The opening (key and blinding factor) is printed in the header of the
submitted PDF, so only someone holding the submission can read the report, and anyone can check
that what they read is exactly what was committed to before the deadline. Pedersen rather than a
bare hash because the log is short and predictable: a hash alone would not hide it.

The full session transcripts (every message, every tool call, the model's reasoning) are
exported, redacted of credentials, and published as an attachment encrypted under the same key.
They are never public in plaintext because they quote problem statements and my own attempts,
which the syllabus forbids publishing. The instructors can request the transcripts in plaintext
at any time.
