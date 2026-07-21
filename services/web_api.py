#!/usr/bin/env python3
"""Minimal test web UI — talks to the persistent mpv instances over IPC."""
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from mpv_ipc import MpvIPC, MpvIPCError

MEDIA_DIR = Path(__file__).resolve().parent.parent / "media"
SOCKETS = {"video": "/tmp/vtg-video.sock", "audio": "/tmp/vtg-audio.sock"}
MEDIA_FOLDERS = {"video": MEDIA_DIR / "video", "audio": MEDIA_DIR / "audio"}

app = Flask(__name__, static_folder=str(Path(__file__).resolve().parent / "static"))

def get_mpv(target):
    if target not in SOCKETS:
        raise ValueError(f"Unknown target: {target}")
    return MpvIPC(SOCKETS[target])

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/media/<target>")
def list_media(target):
    folder = MEDIA_FOLDERS.get(target)
    files = sorted(f.name for f in folder.iterdir() if f.is_file()) if folder and folder.exists() else []
    return jsonify({"success": True, "files": files})

@app.route("/api/status/<target>")
def status(target):
    try:
        mpv = get_mpv(target)
        data = mpv.status()
        mpv.close()
        return jsonify({"success": True, "status": data})
    except MpvIPCError as e:
        return jsonify({"success": False, "message": str(e)}), 503

@app.route("/api/load/<target>", methods=["POST"])
def load(target):
    folder = MEDIA_FOLDERS.get(target)
    if not folder:
        return jsonify({"success": False, "message": "Unknown target"}), 400
    try:
        mpv = get_mpv(target)
        files = sorted(f for f in folder.iterdir() if f.is_file())
        mpv.load_playlist([str(f) for f in files])
        mpv.close()
        return jsonify({"success": True})
    except MpvIPCError as e:
        return jsonify({"success": False, "message": str(e)}), 503

@app.route("/api/control/<target>/<action>", methods=["POST"])
def control(target, action):
    actions = {"play": "play", "pause": "pause", "toggle": "toggle_pause",
               "stop": "stop", "next": "next", "prev": "prev"}
    if action not in actions:
        return jsonify({"success": False, "message": f"Unknown action: {action}"}), 400
    try:
        mpv = get_mpv(target)
        getattr(mpv, actions[action])()
        mpv.close()
        return jsonify({"success": True})
    except MpvIPCError as e:
        return jsonify({"success": False, "message": str(e)}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)