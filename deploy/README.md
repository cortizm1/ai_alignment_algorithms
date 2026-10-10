# Server layout (93.95.231.30, Ubuntu 22.04, 1 vCPU / 1 GB)
browser -> nginx :443 (TLS, certbot) -> Anubis 127.0.0.1:8923 -> backend 127.0.0.1:8010
Backend is the nginx placeholder now; the FastHTML app takes over :8010 when deployed.
Sync: `tools/deploy_server.sh config` copies this folder into place and reloads.
