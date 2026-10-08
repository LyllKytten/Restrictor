#!/usr/bin/env python3
"""Hard blocker: kills games and blocks sites during study hours.

Usage:
  blocker.py run      keep running, check every 15 seconds (needs root/admin)
  blocker.py once     check one time (needs root/admin)
  blocker.py status   show if blocking is on and what you should be doing now
  blocker.py today    show today's plan
  blocker.py edit     edit the config (needs root/admin). Changes start working after 24 hours
  blocker.py clear    remove the site block from the hosts file (used by uninstall)

Lock mode: config changes wait 24 hours before they apply, so you can't
weaken the blocker "just for tonight".
"""
import datetime
import hashlib
import json
import shutil
import os
import subprocess
import sys
import time

import psutil

HERE = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")
IS_WINDOWS = os.name == "nt"
HOSTS_PATH = (r"C:\Windows\System32\drivers\etc\hosts" if IS_WINDOWS else "/etc/hosts")
BEGIN = "# >>> hard-blocker >>>"
END = "# <<< hard-blocker <<<"
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
CHECK_EVERY = 15
CHANGE_DELAY = 24 * 60 * 60
STATE_DIR = (r"C:\ProgramData\HardBlocker\state" if IS_WINDOWS else "/var/lib/hard-blocker")
ACTIVE_PATH = os.path.join(STATE_DIR, "active.json")
PENDING_PATH = os.path.join(STATE_DIR, "pending.json")


# ---------- protected files ----------

def set_immutable(path, on):
    """Linux: chattr +i makes a file impossible to edit or delete, even for root, until chattr -i."""
    if IS_WINDOWS or not shutil.which("chattr") or not os.path.exists(path):
        return
    subprocess.run(["chattr", "+i" if on else "-i", path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def write_protected(path, text):
    set_immutable(path, False)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    set_immutable(path, True)


def read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None


# ---------- config with 24h delay ----------

def config_status():
    """Returns (active config text, pending change info or None) without changing anything."""
    wanted = read_text(CONFIG_PATH)
    active = read_text(ACTIVE_PATH)
    if active is None or active == wanted:
        return wanted, None
    pending = json.loads(read_text(PENDING_PATH) or "{}")
    if pending.get("hash") != hashlib.sha256(wanted.encode()).hexdigest():
        pending = {"since": time.time()}
    return active, {"applies_at": pending["since"] + CHANGE_DELAY}


def load_config():
    """Loads the active config. A new config.json only becomes active 24 hours after the last edit."""
    wanted = read_text(CONFIG_PATH)
    json.loads(wanted)  # fail loudly on broken JSON instead of using it
    if not os.access(STATE_DIR, os.W_OK):  # normal user: just look, don't change state
        return json.loads(config_status()[0])
    active = read_text(ACTIVE_PATH)
    if active is None:  # first run after install
        write_protected(ACTIVE_PATH, wanted)
        return json.loads(wanted)
    if active == wanted:
        return json.loads(active)
    digest = hashlib.sha256(wanted.encode()).hexdigest()
    pending = json.loads(read_text(PENDING_PATH) or "{}")
    if pending.get("hash") != digest:
        write_protected(PENDING_PATH, json.dumps({"hash": digest, "since": time.time()}))
    elif time.time() - pending["since"] >= CHANGE_DELAY:
        write_protected(ACTIVE_PATH, wanted)
        return json.loads(wanted)
    return json.loads(active)


# ---------- watchdog ----------

def ensure_guard():
    """The service and the guard timer restart each other, so stopping one is not enough."""
    if IS_WINDOWS:
        cmd = ["schtasks", "/change", "/tn", "HardBlockerGuard", "/enable"]
    else:
        cmd = ["systemctl", "start", "hard-blocker-guard.timer"]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
    except (OSError, subprocess.SubprocessError):
        pass


def to_minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def is_blocked_now(config, now=None):
    now = now or datetime.datetime.now()
    minute = now.hour * 60 + now.minute
    ranges = config["block_hours"].get(DAYS[now.weekday()], [])
    return any(to_minutes(a) <= minute < to_minutes(b) for a, b in ranges)


def todays_plan(config, now=None):
    now = now or datetime.datetime.now()
    return config["plan"]["weekend" if now.weekday() >= 5 else "weekday"]


def current_task(config, now=None):
    now = now or datetime.datetime.now()
    minute = now.hour * 60 + now.minute
    for start, end, task in todays_plan(config, now):
        if to_minutes(start) <= minute < to_minutes(end):
            return start, end, task
    return None


# ---------- processes ----------

def process_names(proc):
    """All names a process might be known by, lowercase, without .exe."""
    names = set()
    name = proc.info.get("name") or ""
    cmdline = proc.info.get("cmdline") or []
    for n in [name] + cmdline[:1]:
        n = os.path.basename(n.replace("\\", "/")).lower()
        if n.endswith(".exe"):
            n = n[:-4]
        if n:
            names.add(n)
    return names


def should_kill(proc, config):
    names = process_names(proc)
    if names & {n.lower() for n in config["kill_process_names"]}:
        return True
    haystack = " ".join([proc.info.get("exe") or ""] + (proc.info.get("cmdline") or [])).lower()
    haystack = haystack.replace("\\", "/")
    return any(k.lower() in haystack for k in config["kill_if_path_contains"])


def kill_games(config):
    me = {os.getpid(), os.getppid()}
    killed = []
    for proc in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
        try:
            if proc.pid in me or not should_kill(proc, config):
                continue
            proc.kill()
            killed.append(proc.info.get("name") or str(proc.pid))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return killed


# ---------- hosts file ----------

def read_hosts():
    with open(HOSTS_PATH, encoding="utf-8", errors="replace") as f:
        return f.read()


def strip_block(text):
    if BEGIN not in text:
        return text
    before, rest = text.split(BEGIN, 1)
    after = rest.split(END, 1)[1] if END in rest else ""
    return before.rstrip("\n") + "\n" + after.lstrip("\n")


def make_block(sites):
    lines = [BEGIN]
    for site in sites:
        site = site.strip().lower()
        hosts = [site] if site.startswith("www.") else [site, "www." + site]
        for h in hosts:
            lines.append(f"0.0.0.0 {h}")
            lines.append(f":: {h}")
    lines.append(END)
    return "\n".join(lines) + "\n"


def flush_dns():
    cmd = ["ipconfig", "/flushdns"] if IS_WINDOWS else ["resolvectl", "flush-caches"]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
    except (OSError, subprocess.SubprocessError):
        pass


def set_sites_blocked(config, blocked):
    text = read_hosts()
    new = strip_block(text)
    if blocked:
        new = new.rstrip("\n") + "\n\n" + make_block(config["blocked_sites"])
    if new != text:
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.write(new)
        flush_dns()


# ---------- commands ----------

def check_once():
    config = load_config()
    blocked = is_blocked_now(config)
    set_sites_blocked(config, blocked)
    if blocked:
        killed = kill_games(config)
        if killed:
            print(f"[{datetime.datetime.now():%H:%M:%S}] killed: {', '.join(killed)}", flush=True)


def run_forever():
    os.makedirs(STATE_DIR, exist_ok=True)
    while True:
        try:
            ensure_guard()
            check_once()
        except Exception as e:  # keep going no matter what
            print(f"error: {e}", file=sys.stderr, flush=True)
        time.sleep(CHECK_EVERY)


def print_status():
    config = load_config()
    blocked = is_blocked_now(config)
    print("Blocking: ON - games and sites are blocked" if blocked else "Blocking: OFF - free time")
    pending = config_status()[1]
    if pending:
        when = datetime.datetime.fromtimestamp(pending["applies_at"])
        print(f"Config change waiting, starts working at {when:%d.%m %H:%M}")
    task = current_task(config)
    if task:
        print(f"Right now ({task[0]}-{task[1]}): {task[2]}")
    else:
        print("Nothing planned right now.")


def print_today():
    config = load_config()
    now = datetime.datetime.now()
    current = current_task(config, now)
    print(f"Plan for {now:%A %d.%m}:")
    for start, end, task in todays_plan(config, now):
        mark = " <-- now" if current and current[0] == start else ""
        print(f"  {start}-{end}  {task}{mark}")


def edit_config():
    if IS_WINDOWS:
        subprocess.run(["notepad", CONFIG_PATH])
    else:
        set_immutable(CONFIG_PATH, False)
        try:
            subprocess.run([os.environ.get("EDITOR", "nano"), CONFIG_PATH])
        finally:
            set_immutable(CONFIG_PATH, True)
    try:
        json.loads(read_text(CONFIG_PATH))
    except ValueError as e:
        print(f"WARNING: config.json is broken ({e}). Fix it with: study edit")
        return
    print("Saved. Changes start working in 24 hours (study status shows when).")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "run":
        run_forever()
    elif cmd == "once":
        check_once()
    elif cmd == "status":
        print_status()
    elif cmd == "today":
        print_today()
    elif cmd == "edit":
        edit_config()
    elif cmd == "clear":
        set_sites_blocked(load_config(), False)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
