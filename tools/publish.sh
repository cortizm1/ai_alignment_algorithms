#!/usr/bin/env bash
# Build and rsync the transparency site to the VPS. Fill in site/deploy.env first.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$root/tools/publish.py"
env="$root/site/deploy.env"
[ -f "$env" ] || { echo "create $env with: VPS_HOST=user@host  VPS_PATH=/var/www/nymo.finance/algorithms"; exit 1; }
# shellcheck disable=SC1090
. "$env"
rsync -avz --delete --exclude deploy.env "$root/site/" "$VPS_HOST:$VPS_PATH/"
echo "deployed -> https://nymo.finance/algorithms/"
