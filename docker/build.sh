#!/usr/bin/env bash
#
# build.sh — build the UniROS Docker image.
#
# Stages a copy of the parent dir's install_uniros_stack.sh into the
# build context so it's the single source of truth (no duplicate
# installer maintained inside docker/). The staged copy is deleted on
# exit even if the build fails.
#
# The image bakes a non-root user with UID/GID matching the host by
# default (overridable via -u / -g) so that bind-mounted workspaces
# end up with correct host-side file ownership.
#
# TWO BUILD VARIANTS
#
#   Default (CUDA runtime, ~16 GB):
#     ./build.sh
#       FROM nvidia/cuda:12.9.2-runtime-ubuntu20.04
#       tag  uniros:noetic
#       PyTorch / TensorFlow / any CUDA-aware Python lib can use the
#       GPU from inside the container.
#
#   Slim (no CUDA in image, ~12 GB):
#     ./build.sh --slim
#       FROM osrf/ros:noetic-desktop-full-focal
#       tag  uniros:noetic-slim
#       Smaller download. No CUDA libs baked in; in-container training
#       falls back to CPU unless you bring your own GPU PyTorch wheel.
#       Picks up host NVIDIA driver libs via rocker --nvidia at runtime
#       (Gazebo / RViz still get hardware-accelerated GL).
#
# USAGE:
#   ./build.sh                          # default; tag 'uniros:noetic'
#   ./build.sh --slim                   # slim variant; tag 'uniros:noetic-slim'
#   ./build.sh --mujoco                 # also bake in the experimental MuJoCo backend
#   ./build.sh -t myname:tag            # custom tag (combine with --slim too)
#   ./build.sh -u 1001 -g 1001          # explicit UID/GID
#   ./build.sh -h                       # help

set -euo pipefail

# Image variants
DEFAULT_BASE="nvidia/cuda:12.9.2-runtime-ubuntu20.04"
SLIM_BASE="osrf/ros:noetic-desktop-full-focal"
DEFAULT_TAG="uniros:noetic"
SLIM_TAG="uniros:noetic-slim"

# Defaults
SLIM=false
TAG=""
USER_UID="$(id -u)"
USER_GID="$(id -g)"
CUSTOM_TAG=false
INSTALL_MUJOCO=false   # --mujoco bakes in the experimental MuJoCo backend

usage() {
    sed -n '2,/^$/p' "$0"
    exit "${1:-0}"
}

# Hand-rolled arg loop so we can support both short (-t -u -g -h)
# and long (--slim) flags.
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)  usage 0;;
        --slim)     SLIM=true; shift;;
        --mujoco)   INSTALL_MUJOCO=true; shift;;
        -t)         TAG="$2"; CUSTOM_TAG=true; shift 2;;
        -u)         USER_UID="$2"; shift 2;;
        -g)         USER_GID="$2"; shift 2;;
        --)         shift; break;;
        -*)         echo "Unknown flag: $1" >&2; usage 1;;
        *)          echo "Unexpected arg: $1" >&2; usage 1;;
    esac
done

if $SLIM; then
    BASE_IMAGE="$SLIM_BASE"
    [[ "$CUSTOM_TAG" == false ]] && TAG="$SLIM_TAG"
else
    BASE_IMAGE="$DEFAULT_BASE"
    [[ "$CUSTOM_TAG" == false ]] && TAG="$DEFAULT_TAG"
fi

HERE="$(cd "$(dirname "$0")" && pwd)"
PARENT="$(dirname "$HERE")"
INSTALLER_SRC="$PARENT/install_uniros_stack.sh"
INSTALLER_DST="$HERE/install_uniros_stack.sh"

if [[ ! -f "$INSTALLER_SRC" ]]; then
    echo "ERROR: $INSTALLER_SRC not found." >&2
    echo "       This script expects install_uniros_stack.sh in the parent" >&2
    echo "       directory (alongside the docker/ folder)." >&2
    exit 1
fi

cleanup() { rm -f "$INSTALLER_DST"; }
trap cleanup EXIT

cp "$INSTALLER_SRC" "$INSTALLER_DST"

echo "Building $TAG from $HERE"
echo "  BASE_IMAGE=$BASE_IMAGE"
echo "  USER_UID=$USER_UID  USER_GID=$USER_GID"
echo "  INSTALL_MUJOCO=$INSTALL_MUJOCO"
docker build \
    --build-arg "BASE_IMAGE=$BASE_IMAGE" \
    --build-arg "USER_UID=$USER_UID" \
    --build-arg "USER_GID=$USER_GID" \
    --build-arg "INSTALL_MUJOCO=$INSTALL_MUJOCO" \
    -t "$TAG" \
    "$HERE"

echo
echo "Built: $TAG"
echo "Run headless:   $HERE/run.sh -t $TAG"
echo "Run with GUI:   $HERE/run_gui.sh -t $TAG"
