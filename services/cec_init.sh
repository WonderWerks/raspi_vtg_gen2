#!/bin/bash
# Configure both CEC adapters as playback devices. Safe to run even
# if only one HDMI port is actually connected -- an unconnected
# adapter just has no one to talk to.
cec-ctl -d /dev/cec0 --playback
cec-ctl -d /dev/cec1 --playback