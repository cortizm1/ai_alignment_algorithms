# Transparency site deployment — jhu.nymo.finance

STATUS 2026-10-10: LIVE. nginx 1.18 (TLS via certbot) -> Anubis v1.28.1 (127.0.0.1:8923) -> uvicorn jhu-web.service (127.0.0.1:8010, user jhu).
Config lives in `deploy/`; `tools/deploy_server.sh` syncs it. Anubis signing key is server-only (/etc/anubis/jhu.key).


## Pieces
- Static site built by `tools/publish.py` into `site/` (index + hwN.html; encrypted blobs inline).
- Served by nginx (or whatever already fronts nymo.finance) behind Anubis.
- Anubis (TecharoHQ) runs as a reverse proxy: browser -> Anubis (:8923) -> nginx static vhost (:3000-ish, localhost only).
  Carlos already runs Anubis on other subdomains, so reuse the same unit/compose pattern: one more
  Anubis instance (or one more route in the existing policy) + one more nginx vhost.
- TLS: certbot/acme for jhu.nymo.finance (or wildcard if one exists already).
- DNS: A/AAAA record `algorithms` -> VPS IP.

## Seal / submit flow (per homework)
1. `/transcribe hwN` finishes, PDF built, all TODOs resolved.
2. `tools/seal.py N` -> prints `\aireport{url}{KEY}{SHA256}`; paste into hwN.tex header; rebuild once.
3. `tools/publish.sh` -> site rebuilt and rsynced BEFORE submitting on Gradescope (so the commitment is public before the deadline).
4. Submit. `echo submitted > hw/hwN/STATUS`. Later sessions (postmortem) append to ai_log.md and show up in the "latest" blob on next publish, same key.

## DNS findings (2026-10-09)
- nymo.finance is served by OrangeWebsite's nameservers (siti/buffy.ns.orangewebsite.com).
  OrangeWebsite is a WHMCS client area; no public DNS API was found. Add the record by hand:
  `jhu  A  93.95.231.30` (the host that already serves rustdesk. and weus.).
  82.221.136.24 is the apex/mail host (shared hosting?), not the VPS.
- The 32-char token Carlos shared could not be matched to any OrangeWebsite API. Rotate it.

## Still needed from Carlos
- VPS: ssh host/user/port (the `nymo` entry in ~/.ssh/config times out), where the existing Anubis + nginx config lives.
- DNS: provider + API token or just add the A record manually.
- Confirm subdomain name: `jhu.nymo.finance` (used in seal.py URL; change there if different).
