# Omarchy Task Manager ⚡

A lightning-fast, keyboard-driven Task Manager and Window Killer plugin for **[Omarchy](https://github.com/omarchy)** & **Hyprland**.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Omarchy%20%7C%20Hyprland-purple.svg)

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

### Method 1: Using `omarchy plugin add`
```bash
omarchy plugin add https://github.com/serverbauer/omarchy-taskmanager
```

### Method 2: Manual Installation
```bash
git clone https://github.com/serverbauer/omarchy-taskmanager.git
cd omarchy-taskmanager
./install.sh
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
