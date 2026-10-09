#!/usr/bin/env bash
# Printed into context at the start of every session in this project.
cd "$(dirname "$0")/../.."
echo "=== 601.433 harness: policy reminder ==="
echo "LLMs allowed for understanding concepts only. Never answers/hints/proof text for live homework. Transcription is verbatim."
for s in hw/hw*/STATUS; do [ -f "$s" ] && echo "$(dirname "$s"): $(cat "$s")"; done
echo "Today: $(date +%Y-%m-%d). Deadlines: HW4 Oct15, HW5 Oct22, HW6 Oct29, HW7 Nov5, HW8 Nov12, MT2 Nov19, HW9 Dec3, HW10 Dec10, Final Dec15."
