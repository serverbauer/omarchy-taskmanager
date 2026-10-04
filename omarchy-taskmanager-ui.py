#!/usr/bin/env python3
import json
import os
import signal
import subprocess
import sys

def get_window_list():
    lines = []
    try:
        raw = subprocess.check_output(['hyprctl', 'clients', '-j'], text=True)
        clients = json.loads(raw)
        for c in clients:
            if c.get('mapped') and c.get('pid'):
                pid = c.get('pid')
                clazz = c.get('class') or 'Unknown'
                title = (c.get('title') or '').replace('\n', ' ')[:50]
                lines.append(f"{pid:<7} | 🪟 {clazz:<18} | {title}")
    except Exception:
        pass
    return lines

def get_process_list():
    lines = []
    try:
        out = subprocess.check_output(
            ['ps', '-u', os.environ.get('USER', 'finn'), '-o', 'pid,%cpu,%mem,comm', '--sort=-%cpu'],
            text=True
        )
        procs = out.strip().splitlines()[1:25]
        for p in procs:
            parts = p.split(None, 3)
            if len(parts) == 4:
                pid, cpu, mem, comm = parts
                lines.append(f"{pid:<7} | ⚙️  CPU: {cpu:>4}% RAM: {mem:>4}% | {comm}")
    except Exception:
        pass
    return lines

def main():
    windows = get_window_list()
    processes = get_process_list()

    all_entries = windows + ["--------------------------------------------------------------------------------"] + processes
    input_text = "\n".join(all_entries)

    fzf_cmd = [
        'fzf',
        '--ansi',
        '--header=ENTER: Stoppen (Kill) | ALT+R: Neu starten | ESC: Abbrechen',
        '--prompt=App wählen > ',
        '--expect=alt-r'
    ]

    try:
        proc = subprocess.Popen(fzf_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        stdout, _ = proc.communicate(input=input_text)
    except Exception as e:
        sys.exit(1)

    lines = stdout.strip().splitlines()
    if not lines:
        sys.exit(0)

    key_pressed = lines[0] if len(lines) > 1 else ""
    selected_line = lines[1] if len(lines) > 1 else lines[0]

    if not selected_line or selected_line.startswith("---"):
        sys.exit(0)

    parts = selected_line.split('|')
    try:
        target_pid = int(parts[0].strip())
    except ValueError:
        sys.exit(0)

    app_name = parts[1].strip() if len(parts) > 1 else f"PID {target_pid}"

    # Get command for restart if ALT+R was pressed
    comm = ""
    if key_pressed == "alt-r":
        try:
            with open(f"/proc/{target_pid}/comm", "r") as f:
                comm = f.read().strip()
        except Exception:
            pass

    # Kill process
    try:
        os.kill(target_pid, signal.SIGKILL)
        subprocess.run(['notify-send', '-i', 'process-stop', 'Task Manager', f'{app_name} (PID {target_pid}) wurde beendet.'])
    except Exception as e:
        subprocess.run(['notify-send', '-u', 'critical', 'Task Manager', f'Fehler beim Beenden von PID {target_pid}: {e}'])

    # Restart if requested
    if key_pressed == "alt-r" and comm:
        import time
        time.sleep(0.5)
        subprocess.Popen(['uwsm-app', '--', comm])
        subprocess.run(['notify-send', '-i', 'view-refresh', 'Task Manager', f'{comm} wird neu gestartet...'])

if __name__ == '__main__':
    main()
