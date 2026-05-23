#!/usr/bin/env bash
#
# build.sh — build the UniROS Docker image.
#
# Stages a copy of the parent dir's install_uniros_stack.sh into the
# build context so it's the single source of truth (no duplicate
# installer maintained inside docker/). The staged copy is deleted on
# exit even if the build fails.
#
# USAGE:
#   ./build.sh                  # builds tag 'uniros:noetic'
#   ./build.sh -t myname:tag    # custom tag
#   ./build.sh -h               # help

set -euo pipefail

TAG="uniros:noetic"

usage() {
    sed -n '2,/^$/p' "$0"
    exit "${1:-0}"
}

while getopts 'ht:' opt; do
    case "$opt" in
        h) usage 0;;
        t) TAG="$OPTARG";;
        *) usage 1;;
    esac
done

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

echo "Building $TAG from $HERE ..."
docker build -t "$TAG" "$HERE"

echo
echo "Built: $TAG"
echo "Run headless:   $HERE/run.sh"
echo "Run with GUI:   $HERE/run_gui.sh"
