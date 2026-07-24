#!/usr/bin/env python3
"""Thin wrapper around cec-ctl for HDMI-CEC control, per HDMI port."""
import shlex
import subprocess

CEC_DEVICES = {"hdmi1": "/dev/cec0", "hdmi2": "/dev/cec1"}

def run_cec(device_key, args):
    device_path = CEC_DEVICES.get(device_key)
    if not device_path:
        return False, f"Unknown device: {device_key}"
    cmd = ["cec-ctl", "-d", device_path] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return result.returncode == 0, result.stdout + result.stderr

def power_on(device_key):
    return run_cec(device_key, ["--to", "0", "--image-view-on"])

def power_off(device_key):
    return run_cec(device_key, ["--to", "0", "--standby"])

def custom(device_key, command_string):
    return run_cec(device_key, shlex.split(command_string))