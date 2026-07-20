#!/bin/bash
# Persistent video mpv instance, controlled entirely via IPC socket.
# Bound to HDMI1 audio -- adjust the CARD number if your field
# display ends up wired to the other port.

SOCKET=/tmp/vtg-video.sock
rm -f "$SOCKET"

exec mpv --idle=yes \
    --keep-open=yes \
    --input-ipc-server="$SOCKET" \
    --fullscreen \
    --no-osc \
    --no-osd-bar \
    --hwdec=auto \
    --vo=gpu \
    --profile=gpu-hq \
    --scale=bilinear \
    --cscale=bilinear \
    --dscale=bilinear \
    --video-sync=display-resample \
    --audio-device=alsa/hdmi:CARD=vc4hdmi1,DEV=0 \
    --quiet \
    --msg-level=vo=error
