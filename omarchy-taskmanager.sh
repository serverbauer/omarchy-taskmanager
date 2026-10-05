#!/usr/bin/env bash
# Wrapper for Omarchy Task Manager

ACTION="$1"

# Language detection (German if de_* locale, otherwise English default)
LANG_PREFIX="${LANG:0:2}"
if [ "$LANG_PREFIX" = "de" ]; then
    MSG_STOPPED_TITLE="App beendet"
    MSG_STOPPED_BODY="%s (PID: %s) wurde sofort gestoppt."
else
    MSG_STOPPED_TITLE="App terminated"
    MSG_STOPPED_BODY="%s (PID: %s) was killed immediately."
fi

if [ "$ACTION" = "kill-active" ]; then
    PID=$(hyprctl activewindow -j 2>/dev/null | jq -r '.pid // empty')
    CLASS=$(hyprctl activewindow -j 2>/dev/null | jq -r '.class // empty' | tr -d '|\r\n')
    # Validate PID: must be positive integer and greater than 1
    if [[ "$PID" =~ ^[0-9]+$ ]] && [ "$PID" -gt 1 ]; then
        kill -9 "$PID"
        printf -v BODY "$MSG_STOPPED_BODY" "$CLASS" "$PID"
        notify-send -u normal -i process-stop "$MSG_STOPPED_TITLE" "$BODY"
    fi
    exit 0
fi

# Locate the Python script: check sibling path first, then ~/.local/bin
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/omarchy-taskmanager-ui.py" ]; then
    UI_SCRIPT="$SCRIPT_DIR/omarchy-taskmanager-ui.py"
elif [ -f "$HOME/.local/bin/omarchy-taskmanager-ui.py" ]; then
    UI_SCRIPT="$HOME/.local/bin/omarchy-taskmanager-ui.py"
else
    UI_SCRIPT="omarchy-taskmanager-ui.py"
fi

exec omarchy-launch-floating-terminal-with-presentation "$UI_SCRIPT"
