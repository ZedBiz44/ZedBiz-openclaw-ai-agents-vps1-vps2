#!/bin/sh
# Keep each native agent on its existing private GOG credential store.
# No credentials are embedded or copied between agents.
set -eu
REAL=/usr/local/libexec/gog-0.45.0
case "${HOME:-}" in
  /root/.openclaw-frank|/root/.openclaw-harry|/root/.openclaw-suzy)
    STORE="$HOME/.config/gogcli"
    if [ -r "$STORE/keyring.env" ]; then
      set -a
      . "$STORE/keyring.env"
      set +a
    fi
    if [ -r "$STORE/email-mode" ] && [ "$(tr -d '\r\n' < "$STORE/email-mode")" = "draft_only" ]; then
      set -- --gmail-no-send "$@"
    fi
    # Preserve an explicitly selected home; ordinary calls use this agent's store.
    for arg in "$@"; do
      case "$arg" in --home|--home=*) exec "$REAL" "$@" ;; esac
    done
    exec "$REAL" --home "$STORE" "$@"
    ;;
  *) exec "$REAL" "$@" ;;
esac
