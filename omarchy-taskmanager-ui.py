#!/usr/bin/env python3
import json
import os
import select
import signal
import subprocess
import sys
import time

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

def read_subprocess_output(cmd, timeout_sec=1.5, max_bytes=65536, chunk_size=4096):
    """
    Executes a command and reads up to max_bytes with an absolute monotonic deadline.
    Uses non-blocking OS pipe reads (os.read) to prevent stalls where a partial write
    followed by a stalled producer bypasses overall deadlines.
    Ensures bounded memory and unconditional process cleanup.
    """
    deadline = time.monotonic() + timeout_sec
    raw_data = bytearray()
    proc = None
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        fd = proc.stdout.fileno()
        os.set_blocking(fd, False)

        poll = select.poll()
        poll.register(fd, select.POLLIN | select.POLLHUP | select.POLLERR)

        while len(raw_data) < max_bytes:
            now = time.monotonic()
            if now >= deadline:
                break
            timeout_ms = max(1, int((deadline - now) * 1000))
            events = poll.poll(timeout_ms)
            if not events:
                break

            to_read = min(chunk_size, max_bytes - len(raw_data))
            try:
                chunk = os.read(fd, to_read)
            except (BlockingIOError, InterruptedError):
                continue
            except OSError:
                break

            if not chunk:  # EOF
                break
            raw_data.extend(chunk)

    except Exception:
        pass
    finally:
        if proc is not None:
            try:
                proc.stdout.close()
            except OSError:
                pass
            if proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=0.3)
                except (subprocess.TimeoutExpired, OSError):
                    try:
                        proc.kill()
                        proc.wait(timeout=0.2)
                    except OSError:
                        pass

    return raw_data.decode('utf-8', errors='replace')

def get_window_entries():
    items = []
    try:
        raw = read_subprocess_output(['hyprctl', 'clients', '-j'], timeout_sec=1.5, max_bytes=65536).strip()
        if raw:
            # If byte budget truncated mid-stream, repair array boundary
            if not raw.endswith(']'):
                last_brace = raw.rfind('}')
                if last_brace != -1:
                    raw = raw[:last_brace+1] + ']'
                else:
                    raw = '[]'
            clients = json.loads(raw)
            for c in clients:
                if len(items) >= 64:
                    break
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
    user = os.environ.get('USER', 'finn')
    try:
        raw = read_subprocess_output(
            ['ps', '-u', user, '-o', 'pid,%cpu,%mem,comm', '--sort=-%cpu'],
            timeout_sec=1.5,
            max_bytes=8192
        )
        for line in raw.splitlines():
            parts = line.split(None, 3)
            if len(parts) == 4:
                try:
                    pid = int(parts[0])
                except ValueError:
                    continue  # header or unparseable
                if pid <= 1 or pid in known_pids:
                    continue
                cpu = sanitize_text(parts[1])[:6]
                mem = sanitize_text(parts[2])[:6]
                comm = sanitize_text(parts[3])[:35]
                label = f"{pid:<7} | ⚙️  CPU: {cpu:>4}% RAM: {mem:>4}% | {comm}"
                items.append({
                    'pid': pid,
                    'name': comm,
                    'label': label
                })
                if len(items) >= 30:
                    break
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

    # Get command for restart if ALT+R was pressed (bounded read)
    comm = ""
    if key_pressed == "alt-r":
        try:
            with open(f"/proc/{target_pid}/comm", "r") as f:
                comm = sanitize_text(f.read(64).strip())
        except Exception:
            pass

    # Kill process
    try:
        os.kill(target_pid, signal.SIGKILL)
        subprocess.run(['notify-send', '-i', 'process-stop', 'Task Manager', T['killed'].format(name=app_name, pid=target_pid)], timeout=2.0)
    except Exception as e:
        subprocess.run(['notify-send', '-u', 'critical', 'Task Manager', T['kill_error'].format(pid=target_pid, err=e)], timeout=2.0)

    # Restart if requested
    if key_pressed == "alt-r" and comm:
        import time
        time.sleep(0.5)
        subprocess.Popen(['uwsm-app', '--', comm])
        subprocess.run(['notify-send', '-i', 'view-refresh', 'Task Manager', T['restarting'].format(comm=comm)], timeout=2.0)

if __name__ == "__main__":
    main()
