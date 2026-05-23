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
# pattern from the paper). Hardware passthrough flags are commented out
# below; uncomment the ones you need.
#
# USAGE:
#   ./run.sh                        # uniros:noetic, scratch container
#   ./run.sh -t mytag               # different image tag
#   ./run.sh -w ~/uniros_ws_host    # bind-mount your host workspace
#                                   # over /home/uniros/uniros_ws
#                                   # (active dev)
#   ./run.sh -h                     # help

set -euo pipefail

TAG="uniros:noetic"
MOUNT_WS=""

usage() {
    sed -n '2,/^$/p' "$0"
    exit "${1:-0}"
}

while getopts 'ht:w:' opt; do
    case "$opt" in
        h) usage 0;;
        t) TAG="$OPTARG";;
        w) MOUNT_WS="$OPTARG";;
        *) usage 1;;
    esac
done

DOCKER_ARGS=(
    --rm -it
    --name uniros
    --network=host                   # ROS multicast / arbitrary rosmaster port
    --ipc=host                       # shared-memory transport for Gazebo
)

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
#   # NVIDIA GPU (Gazebo HW rendering, ML inside container):
#   DOCKER_ARGS+=( --gpus all )
#
#   # Full host device access (last resort; convenient for bring-up):
#   DOCKER_ARGS+=( --privileged )

docker run "${DOCKER_ARGS[@]}" "$TAG"
