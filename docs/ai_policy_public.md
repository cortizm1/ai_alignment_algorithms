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

The logs are published encrypted, commitment-style. At submission time the log is frozen,
its SHA-256 is published here and printed in the header of the submitted PDF together with
the decryption key. Only someone holding the PDF (the graders) can read the report, and
the published hash proves the report was fixed before the deadline and not edited after.
Cipher: AES-256-GCM, key derived from the printed passphrase with PBKDF2-SHA256. Decryption
happens in your browser; nothing is sent anywhere. The full session transcripts (every message, every tool call, the
model's reasoning) are exported, redacted of credentials, and published under the same
encryption and the same opening as the report. They are never public in plaintext because
they quote problem statements and my own attempts, which the syllabus forbids publishing.
