# Omarchy Task Manager ⚡

A lightning-fast, keyboard-driven Task Manager and Window Killer plugin for **[Omarchy](https://github.com/omarchy)** & **Hyprland**.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Omarchy%20%7C%20Hyprland-purple.svg)
![Views](https://komarev.com/ghpvc/?username=serverbauer-omarchy-taskmanager&label=Views&color=0e75b6&style=flat)

---

## Features

- **Interactive Search & Kill:** Instant process and window list powered by `fzf`.
- **Hyprland Aware:** Distinguishes between open windows (with window class & title) and background processes.
- **Instant Kill (`SIGKILL`):** Terminate hanging processes or unresponsive games/apps with a single keypress.
- **Process Restart:** Press `ALT + R` to kill and immediately restart an application through `uwsm-app`.
- **Top Bar Widget:** Adds a clean status bar widget to the Omarchy top bar (Left-click: open Task Manager, Right-click: kill active window).
- **Global Keybindings:** Preconfigured for seamless muscle memory (`CTRL + SHIFT + ESC`).

---

## Keybindings

| Shortcut | Action |
| :--- | :--- |
| `CTRL + SHIFT + ESC` | Open Interactive Task Manager (Floating Window) |
| `SUPER + SHIFT + ESC` | Kill the currently focused window immediately |
| `ENTER` *(inside menu)* | Kill selected process (`SIGKILL`) |
| `ALT + R` *(inside menu)* | Restart selected process |
| `ESC` *(inside menu)* | Close Task Manager |

---

## Installation

### 1-Click / Marketplace Installation (Recommended)
You can install the plugin with a single click from the **[Omarchy Plugin Marketplace](https://omarchyplugins.com/plugin.html?id=io.github.serverbauer.taskmanager)** or run:
```bash
omarchy plugin add io.github.serverbauer.taskmanager
```
The bar widget is self-contained, launches immediately on click, and requires no manual setup.

### Optional: Global Keybindings
To also launch the Task Manager via keyboard shortcut (`CTRL + SHIFT + ESC`), add the following to `~/.config/hypr/bindings.lua`:
```lua
o.bind("CTRL + SHIFT + ESCAPE", "Task Manager", "~/.config/omarchy/plugins/io.github.serverbauer.taskmanager/omarchy-taskmanager.sh")
o.bind("SUPER + SHIFT + ESCAPE", "Kill active window", "~/.config/omarchy/plugins/io.github.serverbauer.taskmanager/omarchy-taskmanager.sh kill-active")
```

---

## Requirements

- `fzf`
- `hyprland` (`hyprctl`)
- `python3`
- `libnotify` (`notify-send`)

---

## License

MIT © [serverbauer](https://github.com/serverbauer)
