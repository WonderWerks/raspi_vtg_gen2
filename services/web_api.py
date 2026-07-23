#!/usr/bin/env python3
"""Minimal test web UI — talks to the persistent mpv instances over IPC."""
from pathlib import Path
import json
from flask import Flask, jsonify, request, send_from_directory
from mpv_ipc import MpvIPC, MpvIPCError

MEDIA_DIR = Path(__file__).resolve().parent.parent / "media"
SOCKETS = {"video": "/tmp/vtg-video.sock", "audio": "/tmp/vtg-audio.sock", "image": "/tmp/vtg-image.sock"}
MEDIA_FOLDERS = {"video": MEDIA_DIR / "video", "audio": MEDIA_DIR / "audio"}
IMAGE_FOLDERS = {
    "1080p": MEDIA_DIR / "images_1080p",
    "4k": MEDIA_DIR / "images_4k",
}

app = Flask(__name__, static_folder=str(Path(__file__).resolve().parent / "static"))

def get_mpv(target):
    if target not in SOCKETS:
        raise ValueError(f"Unknown target: {target}")
    return MpvIPC(SOCKETS[target])

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/status/<target>")
def status(target):
    try:
        mpv = get_mpv(target)
        data = mpv.status()
        mpv.close()
        return jsonify({"success": True, "status": data})
    except MpvIPCError as e:
        return jsonify({"success": False, "message": str(e)}), 503

@app.route("/api/media/<target>")
def list_media(target):
    if target == "image":
        folder = IMAGE_FOLDERS.get(request.args.get("resolution", "1080p"))
    else:
        folder = MEDIA_FOLDERS.get(target)
    files = sorted(f.name for f in folder.iterdir() if f.is_file()) if folder and folder.exists() else []
    return jsonify({"success": True, "files": files})

@app.route("/api/load/<target>", methods=["POST"])
def load(target):
    data = request.json or {}
    mode = data.get("mode", "folder")
    folder = IMAGE_FOLDERS.get(data.get("resolution", "1080p")) if target == "image" else MEDIA_FOLDERS.get(target)
    if not folder:
        return jsonify({"success": False, "message": "Unknown target/resolution"}), 400
    try:
        mpv = get_mpv(target)
        if mode == "single":
            filename = data.get("filename")
            if not filename:
                mpv.close()
                return jsonify({"success": False, "message": "No filename given"}), 400
            mpv.loadfile(str(folder / filename))
            mpv.close()
            return jsonify({"success": True})
        files = sorted(f for f in folder.iterdir() if f.is_file())
        mpv.load_playlist([str(f) for f in files])
        mpv.close()
        return jsonify({"success": True, "count": len(files)})
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

@app.route("/api/speed/image", methods=["POST"])
def set_image_speed():
    try:
        seconds = float((request.json or {}).get("seconds"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Invalid seconds value"}), 400
    try:
        mpv = get_mpv("image")
        mpv.set_property("image-display-duration", seconds)
        mpv.close()
        return jsonify({"success": True})
    except MpvIPCError as e:
        return jsonify({"success": False, "message": str(e)}), 503

STATE_DIR = MEDIA_DIR.parent / "state"
OSD_CONFIG_PATH = STATE_DIR / "osd_config.json"
OSD_DEFAULTS = {"enabled": True, "show_ip": True, "show_web_url": True, "show_errors": True}

@app.route("/api/osd/config", methods=["GET"])
def get_osd_config():
    try:
        with open(OSD_CONFIG_PATH) as f:
            cfg = {**OSD_DEFAULTS, **json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError):
        cfg = dict(OSD_DEFAULTS)
    return jsonify({"success": True, "config": cfg})

@app.route("/api/osd/config", methods=["POST"])
def set_osd_config():
    STATE_DIR.mkdir(exist_ok=True)
    cfg = {**OSD_DEFAULTS, **(request.json or {})}
    with open(OSD_CONFIG_PATH, "w") as f:
        json.dump(cfg, f)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)