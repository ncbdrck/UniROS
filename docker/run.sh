#!/usr/bin/env bash
#
# run.sh — start the UniROS container, headless.
#
# Drops you into bash as the non-root uniros user (UID/GID matching
# whatever build.sh used) with the workspace already sourced. Use
# this when you only need rospy / roscore / Gazebo's headless server
# / training scripts and don't want a graphical Gazebo or RViz
# window. For GUI use run_gui.sh.
#
# Linux hosts get --network=host so ROS_MASTER_URI works naturally with
# any remote rosmaster (Niryo Ned2, UR5e, MultiROS multi-rosmaster
# pattern from the paper). If nvidia-smi is available on the host,
# the script exposes all GPUs by default via Docker's NVIDIA runtime.
#
# GPU selection:
#   UNIROS_GPUS=all ./run.sh             # default; expose every GPU
#   UNIROS_GPUS='"device=0"' ./run.sh    # expose only GPU 0
#   UNIROS_GPUS='"device=0,2"' ./run.sh  # expose GPUs 0 and 2
#   ./run.sh --no-gpu                   # disable GPU passthrough
#
# USAGE:
#   ./run.sh                        # uniros:noetic, scratch container
#   ./run.sh -t mytag               # different image tag
#   ./run.sh -w ~/uniros_ws_host    # bind-mount your host workspace
#                                   # over /home/uniros/uniros_ws
#                                   # (active dev)
#   ./run.sh --no-gpu               # do not pass --gpus to docker
#   ./run.sh -h                     # help

set -euo pipefail

TAG="uniros:noetic"
MOUNT_WS=""
USE_GPU=true
GPU_DEVICES="${UNIROS_GPUS:-all}"

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

DOCKER_ARGS=(
    --rm -it
    --name uniros
    --network=host                   # ROS multicast / arbitrary rosmaster port
    --ipc=host                       # shared-memory transport for Gazebo
)

if $USE_GPU; then
    if command -v nvidia-smi >/dev/null 2>&1; then
        DOCKER_ARGS+=( --gpus "$GPU_DEVICES" )
        DOCKER_ARGS+=( -e NVIDIA_VISIBLE_DEVICES="$GPU_DEVICES" )
        DOCKER_ARGS+=( -e NVIDIA_DRIVER_CAPABILITIES=all )
        echo "NVIDIA GPU passthrough enabled: UNIROS_GPUS=$GPU_DEVICES"
    else
        echo "Note: nvidia-smi not found on host; running without --gpus."
        echo "      Install NVIDIA drivers + NVIDIA Container Toolkit for GPU use."
        echo "      Pass --no-gpu to silence this message."
    fi
fi

if [[ -n "$MOUNT_WS" ]]; then
    MOUNT_WS_ABS="$(cd "$MOUNT_WS" && pwd)"
    DOCKER_ARGS+=( -v "$MOUNT_WS_ABS:/home/uniros/uniros_ws" )
    echo "Mounting host workspace $MOUNT_WS_ABS at /home/uniros/uniros_ws"
fi

# Hardware passthrough — uncomment what you need.
#
#   # Interbotix arms (RX200, VX300S) over U2D2:
#   DOCKER_ARGS+=( --device=/dev/ttyDXL:/dev/ttyDXL )
#
#   # Generic USB serial robot:
#   DOCKER_ARGS+=( --device=/dev/ttyUSB0:/dev/ttyUSB0 )
#
#   # Full host device access (last resort; convenient for bring-up):
#   DOCKER_ARGS+=( --privileged )

docker run "${DOCKER_ARGS[@]}" "$TAG"
