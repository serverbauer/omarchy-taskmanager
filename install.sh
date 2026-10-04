#!/usr/bin/env bash
# Installer for Omarchy Task Manager

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
PLUGIN_DIR="$HOME/.config/omarchy/plugins/io.github.serverbauer.taskmanager"

echo "==> Installing binaries to $BIN_DIR..."
mkdir -p "$BIN_DIR"
cp "$DIR/omarchy-taskmanager.sh" "$BIN_DIR/"
cp "$DIR/omarchy-taskmanager-ui.py" "$BIN_DIR/"
chmod +x "$BIN_DIR/omarchy-taskmanager.sh" "$BIN_DIR/omarchy-taskmanager-ui.py"

echo "==> Registering Omarchy Plugin..."
mkdir -p "$PLUGIN_DIR"
cp "$DIR/manifest.json" "$PLUGIN_DIR/"
cp "$DIR/BarWidget.qml" "$PLUGIN_DIR/"

# Ensure keybinding in hyprland bindings.lua if present
BINDINGS_LUA="$HOME/.config/hypr/bindings.lua"
if [ -f "$BINDINGS_LUA" ]; then
    if ! grep -q "omarchy-taskmanager.sh" "$BINDINGS_LUA"; then
        echo "==> Adding keybindings to $BINDINGS_LUA..."
        echo 'o.bind("CTRL + SHIFT + ESCAPE", "Task Manager", "~/.local/bin/omarchy-taskmanager.sh")' >> "$BINDINGS_LUA"
        echo 'o.bind("SUPER + SHIFT + ESCAPE", "Kill active window", "~/.local/bin/omarchy-taskmanager.sh kill-active")' >> "$BINDINGS_LUA"
    fi
fi

echo "==> Validating plugin..."
if command -v omarchy >/dev/null 2>&1; then
    omarchy plugin validate "$PLUGIN_DIR" || true
fi

echo "==> Done! You can launch the Task Manager with Ctrl+Shift+Esc or via the Omarchy bar widget."
