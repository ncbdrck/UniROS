#!/usr/bin/env bash
#
# run_gui.sh — start the UniROS container with X11 + (optional) GPU
# passthrough so Gazebo and RViz windows render on the host display.
#
# Uses rocker (https://github.com/osrf/rocker). rocker is a thin wrapper
# around `docker run` that handles the messy X11 / GPU / user-UID
# plumbing for you. It's the same tool the TIAGo / PAL Robotics tutorials
# recommend.
#
# Install rocker once on the host:
#     sudo apt install python3-rocker            # Ubuntu 20.04 / 22.04
#     # or: pip3 install --user rocker
#
# The container is built with a non-root uniros user; rocker's --user
# flag layers a runtime user matching your *current* host UID over the
# baked one, so file ownership stays clean even if you didn't rebuild
# the image when your UID changed.
#
# USAGE:
#   ./run_gui.sh                     # X11; auto-detects NVIDIA
#   ./run_gui.sh -t mytag            # different image tag
#   ./run_gui.sh -w ~/uniros_ws_host # bind-mount host workspace
#   ./run_gui.sh --no-gpu            # skip NVIDIA passthrough (Intel/AMD/llvmpipe)
#   ./run_gui.sh -h                  # help

set -euo pipefail

TAG="uniros:noetic"
MOUNT_WS=""
USE_GPU=true

usage() {
    sed -n '2,/^$/p' "$0"
    exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) usage 0;;
        -t) TAG="$2"; shift 2;;
        -w) MOUNT_WS="$2"; shift 2;;
        --no-gpu) USE_GPU=false; shift;;
        *) echo "Unknown arg: $1" >&2; usage 1;;
    esac
done

if ! command -v rocker >/dev/null 2>&1; then
    cat >&2 <<'EOF'
ERROR: rocker is not installed.

Install it (one of):
    sudo apt install python3-rocker
    pip3 install --user rocker

Then re-run this script. Alternatively, run the container manually
with run.sh and forward X11 yourself.
EOF
    exit 1
fi

ROCKER_ARGS=( --x11 --user --network=host --ipc=host --name uniros-gui )

if $USE_GPU; then
    if command -v nvidia-smi >/dev/null 2>&1; then
        ROCKER_ARGS+=( --nvidia )
    else
        echo "Note: nvidia-smi not found on host; running without --nvidia."
        echo "      Gazebo/RViz will use software rendering (slower)."
        echo "      Pass --no-gpu to silence this message."
    fi
fi

if [[ -n "$MOUNT_WS" ]]; then
    MOUNT_WS_ABS="$(cd "$MOUNT_WS" && pwd)"
    ROCKER_ARGS+=( --volume "$MOUNT_WS_ABS:/home/uniros/uniros_ws" )
    echo "Mounting host workspace $MOUNT_WS_ABS at /home/uniros/uniros_ws"
fi

# Hardware passthrough — add what you need. rocker forwards extra
# `--devices` / `--privileged` arguments straight through to docker run.
#
#   ROCKER_ARGS+=( --devices /dev/ttyDXL )      # Interbotix U2D2
#   ROCKER_ARGS+=( --devices /dev/ttyUSB0 )     # generic USB serial

echo "Starting rocker: rocker ${ROCKER_ARGS[*]} -- $TAG"
exec rocker "${ROCKER_ARGS[@]}" -- "$TAG"
