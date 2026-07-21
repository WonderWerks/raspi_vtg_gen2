#!/bin/bash
SOCKET=/tmp/vtg-image.sock
rm -f "$SOCKET"

exec mpv --idle=yes \
    --keep-open=yes \
    --input-ipc-server="$SOCKET" \
    --fullscreen \
    --no-osc \
    --no-osd-bar \
    --image-display-duration=5 \
    --loop-playlist=inf \
    --vo=gpu \
    --profile=gpu-hq \
    --quiet \
    --msg-level=vo=error \
    ~/vtg_gen2/media/images_1080p/*