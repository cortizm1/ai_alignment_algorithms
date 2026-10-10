#!/usr/bin/env bash
# Sync to the VPS. Usage: tools/deploy_server.sh config|cert|app|data|status
set -euo pipefail
H=root@93.95.231.30; R="$(cd "$(dirname "$0")/.." && pwd)/deploy"
case "${1:-status}" in
  config)
    rsync -az "$R/anubis/jhu.env" "$H:/etc/anubis/jhu.env"
    rsync -az "$R/nginx/upstream-anubis.conf" "$H:/etc/nginx/conf.d/upstream-anubis.conf"
    rsync -az "$R/nginx/jhu-backend" "$H:/etc/nginx/sites-available/jhu-backend"
    if ssh "$H" test -f /etc/letsencrypt/live/jhu.nymo.finance/fullchain.pem; then
      rsync -az "$R/nginx/jhu.nymo.finance" "$H:/etc/nginx/sites-available/jhu.nymo.finance"
    else
      rsync -az "$R/nginx/jhu.nymo.finance.http" "$H:/etc/nginx/sites-available/jhu.nymo.finance"
    fi
    ssh "$H" 'mkdir -p /srv/jhu/placeholder' && rsync -az "$R/placeholder.html" "$H:/srv/jhu/placeholder/index.html"
    ssh "$H" 'test -f /etc/anubis/jhu.key || openssl rand -hex 32 > /etc/anubis/jhu.key; chmod 600 /etc/anubis/jhu.key
      grep -q ED25519_PRIVATE_KEY_HEX= /etc/anubis/jhu.env || echo "ED25519_PRIVATE_KEY_HEX=$(cat /etc/anubis/jhu.key)" >> /etc/anubis/jhu.env
      test -f /etc/anubis/jhu.botPolicies.yaml || cp /usr/share/doc/anubis/botPolicies.yaml /etc/anubis/jhu.botPolicies.yaml
      rm -f /etc/nginx/sites-enabled/default
      ln -sf /etc/nginx/sites-available/jhu-backend /etc/nginx/sites-enabled/jhu-backend
      ln -sf /etc/nginx/sites-available/jhu.nymo.finance /etc/nginx/sites-enabled/jhu.nymo.finance
      nginx -t && systemctl reload nginx && systemctl enable --now anubis@jhu.service && systemctl restart anubis@jhu.service
      echo "nginx: $(systemctl is-active nginx)  anubis@jhu: $(systemctl is-active anubis@jhu)"' ;;
  cert)
    ssh "$H" 'certbot certonly --webroot -w /var/www/html -d jhu.nymo.finance --non-interactive --agree-tos -m caomdeo@gmail.com && ls /etc/letsencrypt/live/jhu.nymo.finance/' ;;
  app)
    # code -> /srv/jhu/app (owned by the unprivileged jhu user), deps via uv, systemd unit, nginx backend handed over
    ssh "$H" 'id -u jhu >/dev/null 2>&1 || useradd -r -m -d /srv/jhu/home -s /usr/sbin/nologin jhu; mkdir -p /srv/jhu/app /srv/jhu/data; chown -R jhu:jhu /srv/jhu'
    rsync -az --delete --exclude .venv --exclude __pycache__ --exclude '*.pyc' \
      "$R/../web" "$R/../transparency" "$R/../pyproject.toml" "$R/../uv.lock" "$R/../docs/ai_policy_public.md" "$R/../docs/manifesto_onepager.pdf" "$H:/srv/jhu/app/"
    ssh "$H" 'mkdir -p /srv/jhu/app/docs && mv -f /srv/jhu/app/ai_policy_public.md /srv/jhu/app/manifesto_onepager.pdf /srv/jhu/app/docs/ && chown -R jhu:jhu /srv/jhu/app
      install -m755 /root/.local/bin/uv /usr/local/bin/uv; dpkg -s libsodium23 >/dev/null 2>&1 || apt-get install -y -qq libsodium23 >/dev/null
      sudo -u jhu -H bash -c "cd /srv/jhu/app && uv sync --frozen --no-dev --python 3.12 -q" 2>&1 | tail -2'
    rsync -az "$R/jhu-web.service" "$H:/etc/systemd/system/jhu-web.service"
    ssh "$H" 'systemctl daemon-reload && systemctl enable --now jhu-web.service && systemctl restart jhu-web.service
      rm -f /etc/nginx/sites-enabled/jhu-backend; nginx -t >/dev/null 2>&1 && systemctl reload nginx
      sleep 2; systemctl is-active jhu-web; curl -s -o /dev/null -w "app on :8010 -> %{http_code}\n" http://127.0.0.1:8010/' ;;
  data)
    python3 -I "$R/../tools/publish_data.py" >/dev/null
    rsync -az --delete "$R/../data/" "$H:/srv/jhu/data/" && ssh "$H" 'chown -R jhu:jhu /srv/jhu/data; ls /srv/jhu/data' ;;
  status)
    ssh "$H" 'systemctl is-active nginx anubis@jhu; ss -tlnp | grep -E ":(80|443|8010|8923) " | awk "{print \$4}"; curl -s -o /dev/null -w "local backend: %{http_code}\n" http://127.0.0.1:8010/; curl -s -o /dev/null -w "via anubis: %{http_code}\n" http://127.0.0.1:8923/' ;;
esac
