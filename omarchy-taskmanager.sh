#!/usr/bin/env bash
# Wrapper for Omarchy Task Manager

ACTION="$1"

if [ "$ACTION" = "kill-active" ]; then
    PID=$(hyprctl activewindow -j 2>/dev/null | jq -r '.pid // empty')
    CLASS=$(hyprctl activewindow -j 2>/dev/null | jq -r '.class // empty')
    if [ -n "$PID" ] && [ "$PID" -gt 0 ]; then
        kill -9 "$PID"
        notify-send -u normal -i process-stop "App beendet" "$CLASS (PID: $PID) wurde sofort gestoppt."
    fi
    exit 0
fi

# Launch floating terminal with Python task manager
exec omarchy-launch-floating-terminal-with-presentation "/home/finn/.local/bin/omarchy-taskmanager-ui.py"
