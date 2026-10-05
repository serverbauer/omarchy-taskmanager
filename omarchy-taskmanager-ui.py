#!/usr/bin/env python3
import json
import os
import signal
import subprocess
import sys

# Language detection: German if system locale starts with 'de', otherwise English default
lang_code = os.environ.get('LANG', '')[:2].lower()

STRINGS = {
    'en': {
        'header': 'ENTER: Kill process | ALT+R: Restart | ESC: Cancel',
        'prompt': 'Select app/process > ',
        'killed': '{name} (PID {pid}) was terminated.',
        'kill_error': 'Error terminating PID {pid}: {err}',
        'restarting': '{comm} is restarting...',
        'unknown': 'Unknown'
    },
    'de': {
        'header': 'ENTER: Stoppen (Kill) | ALT+R: Neu starten | ESC: Abbrechen',
        'prompt': 'App / Prozess wählen > ',
        'killed': '{name} (PID {pid}) wurde beendet.',
        'kill_error': 'Fehler beim Beenden von PID {pid}: {err}',
        'restarting': '{comm} wird neu gestartet...',
        'unknown': 'Unbekannt'
    }
}

T = STRINGS.get(lang_code, STRINGS['en'])

def sanitize_text(text):
    if not text:
        return ''
    # Strip newlines, carriage returns, null bytes, and delimiter pipes
    return ''.join(c if (c >= ' ' and c not in '|\r\n\0') else ' ' for c in str(text)).strip()

def get_window_entries():
    items = []
    try:
        raw = subprocess.check_output(['hyprctl', 'clients', '-j'], text=True)
        clients = json.loads(raw)
        for c in clients:
            if c.get('mapped') and c.get('pid'):
                pid = c.get('pid')
                if not isinstance(pid, int) or pid <= 1:
                    continue
                clazz = sanitize_text(c.get('class') or T['unknown'])[:25]
                title = sanitize_text(c.get('title') or '')[:50]
                label = f"{pid:<7} | 🪟 {clazz:<18} | {title}"
                items.append({
                    'pid': pid,
                    'name': clazz,
                    'label': label
                })
    except Exception:
        pass
    return items

def get_process_entries(known_pids):
    items = []
    try:
        out = subprocess.check_output(
            ['ps', '-u', os.environ.get('USER', 'finn'), '-o', 'pid,%cpu,%mem,comm', '--sort=-%cpu'],
            text=True
        )
        procs = out.strip().splitlines()[1:30]
        for p in procs:
            parts = p.split(None, 3)
            if len(parts) == 4:
                try:
                    pid = int(parts[0])
                except ValueError:
                    continue
                if pid <= 1 or pid in known_pids:
                    continue
                cpu = sanitize_text(parts[1])
                mem = sanitize_text(parts[2])
                comm = sanitize_text(parts[3])[:35]
                label = f"{pid:<7} | ⚙️  CPU: {cpu:>4}% RAM: {mem:>4}% | {comm}"
                items.append({
                    'pid': pid,
                    'name': comm,
                    'label': label
                })
    except Exception:
        pass
    return items

def main():
    windows = get_window_entries()
    win_pids = {w['pid'] for w in windows}
    processes = get_process_entries(win_pids)

    # Maintain an authoritative internal map from sanitized label to validated item
    registry = {}
    display_lines = []

    for w in windows:
        display_lines.append(w['label'])
        registry[w['label']] = w

    if display_lines and processes:
        display_lines.append("--------------------------------------------------------------------------------")

    for p in processes:
        display_lines.append(p['label'])
        registry[p['label']] = p

    input_text = "\n".join(display_lines)

    fzf_cmd = [
        'fzf',
        '--ansi',
        f'--header={T["header"]}',
        f'--prompt={T["prompt"]}',
        '--expect=alt-r'
    ]

    try:
        proc = subprocess.Popen(fzf_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        stdout, _ = proc.communicate(input=input_text)
    except Exception:
        sys.exit(1)

    lines = stdout.strip().splitlines()
    if not lines:
        sys.exit(0)

    key_pressed = lines[0] if len(lines) > 1 else ""
    selected_line = lines[1] if len(lines) > 1 else lines[0]

    # Validate against our authoritative internal registry
    if selected_line not in registry:
        sys.exit(0)

    target_item = registry[selected_line]
    target_pid = target_item['pid']

    # Strict defensive guard: never signal PID <= 1 or negative PIDs
    if not isinstance(target_pid, int) or target_pid <= 1:
        sys.exit(0)

    app_name = target_item['name'] or f"PID {target_pid}"

    # Get command for restart if ALT+R was pressed
    comm = ""
    if key_pressed == "alt-r":
        try:
            with open(f"/proc/{target_pid}/comm", "r") as f:
                comm = sanitize_text(f.read().strip())
        except Exception:
            pass

    # Kill process
    try:
        os.kill(target_pid, signal.SIGKILL)
        subprocess.run(['notify-send', '-i', 'process-stop', 'Task Manager', T['killed'].format(name=app_name, pid=target_pid)])
    except Exception as e:
        subprocess.run(['notify-send', '-u', 'critical', 'Task Manager', T['kill_error'].format(pid=target_pid, err=e)])

    # Restart if requested
    if key_pressed == "alt-r" and comm:
        import time
        time.sleep(0.5)
        subprocess.Popen(['uwsm-app', '--', comm])
        subprocess.run(['notify-send', '-i', 'view-refresh', 'Task Manager', T['restarting'].format(comm=comm)])

if __name__ == "__main__":
    main()
