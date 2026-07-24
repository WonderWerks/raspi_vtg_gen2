#!/usr/bin/env python3
"""Persistent OSD updater. Sets mpv's built-in status-message OSD line
on whichever instance (video or image) currently owns the display.
Controlled by state/osd_config.json."""
import json
import subprocess
import time
from pathlib import Path
from mpv_ipc import MpvIPC, MpvIPCError

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "state" / "osd_config.json"
SOCKETS = ["/tmp/vtg-display.sock"]
PORT = 5000
POLL_SECONDS = 5

DEFAULT_CONFIG = {"enabled": True, "show_ip": True, "show_web_url": True, "show_errors": True}

def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT_CONFIG)

def get_ip(iface):
    try:
        out = subprocess.check_output(["ip", "-4", "-o", "addr", "show", iface], text=True)
        return out.split()[3].split("/")[0]
    except Exception:
        return None

def service_active(name):
    r = subprocess.run(["systemctl", "is-active", name], capture_output=True, text=True)
    return r.stdout.strip() == "active"

def build_status_text(cfg):
    lines = []
    if cfg.get("show_ip", True):
        lines.append(f"eth0: {get_ip('eth0') or 'not connected'}")
        lines.append(f"wlan0: {get_ip('wlan0') or 'not connected'}")
    if cfg.get("show_web_url", True):
        ip = get_ip("eth0") or get_ip("wlan0")
        if ip:
            lines.append(f"Web UI: http://{ip}:{PORT}")
    if cfg.get("show_errors", True):
        for svc in ("vtg-display.service", "vtg-audio.service", "vtg-web.service"):
            if not service_active(svc):
                lines.append(f"ERROR: {svc} not running")
    return "\n".join(lines)

def find_active_mpv():
    for sock in SOCKETS:
        try:
            return MpvIPC(sock, connect_timeout=1)
        except MpvIPCError:
            continue
    return None

def main():
    while True:
        cfg = load_config()
        mpv = find_active_mpv()
        if mpv:
            try:
                text = build_status_text(cfg) if cfg.get("enabled", True) else ""
                mpv.set_property("osd-status-msg", text)
            except MpvIPCError:
                pass
            finally:
                mpv.close()
        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()