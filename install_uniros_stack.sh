#!/usr/bin/env bash
#
# install_uniros_stack.sh
#
# One-shot installer for the UniROS RL stack: ROS Noetic, the UniROS
# framework (with MultiROS + RealROS as submodules), sb3_ros_support,
# rl_environments (with all 4 robots' vendor packages + supporting
# description-extras + rl_envs_cube_tracker), and rl_training_validation.
#
# Canonical copy lives in github.com/ncbdrck/UniROS. Identical copies
# are kept in the other 4 ecosystem repos (MultiROS, RealROS,
# sb3_ros_support, rl_environments, rl_training_validation) so users
# can run it from whichever repo they cloned first.
#
# USAGE:
#   ./install_uniros_stack.sh                 # interactive
#   ./install_uniros_stack.sh -y              # assume yes to every prompt
#   ./install_uniros_stack.sh -p ~/my_ws      # custom workspace path
#   ./install_uniros_stack.sh -h              # help
#
# REQUIREMENTS:
#   * Ubuntu 20.04 (Noetic only; the script refuses to run elsewhere).
#   * sudo privileges (apt + rosdep need root).
#   * Internet access (clones from github.com + ros.org).
#
# IDEMPOTENT:
#   * ROS install is skipped if `ros-noetic-desktop-full` is already
#     installed.
#   * Repo clones are skipped if the target directory already contains
#     a .git folder.
#   * pip installs let pip itself handle "already installed".
#

set -u                       # error on undefined vars

# ---------- colours --------------------------------------------------------
OFF='\033[0m'; RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[0;33m'
BLU='\033[0;34m'; BOLD=$(tput bold 2>/dev/null || echo ""); NORM=$(tput sgr0 2>/dev/null || echo "")

err()  { echo -e "${RED}${BOLD}[ERROR]${NORM}${OFF} $*" >&2; }
warn() { echo -e "${YLW}${BOLD}[WARN ]${NORM}${OFF} $*" >&2; }
info() { echo -e "${BLU}${BOLD}[INFO ]${NORM}${OFF} $*"; }
ok()   { echo -e "${GRN}${BOLD}[ OK  ]${NORM}${OFF} $*"; }
fail() { err "$*"; exit 1; }

# ---------- args -----------------------------------------------------------
ASSUME_YES=false
WORKSPACE_PATH=""
DEFAULT_WS_NAME="uniros_ws"

usage() {
    cat <<EOF
USAGE: $(basename "$0") [-h] [-p PATH] [-y]

Install the UniROS RL stack: ROS Noetic, UniROS (multiros + realros),
sb3_ros_support, rl_environments + 4-robot vendor packages,
rl_training_validation.

Options:
  -h          Show this help and quit.
  -p PATH     Workspace path (absolute or relative). Default: ~/$DEFAULT_WS_NAME
              Must end in '_ws/' or have a 'src/' subfolder, otherwise the
              script prompts to create the workspace or fall back to default.
  -y          Assume 'yes' to every prompt. Useful for CI / unattended runs.

Examples:
  $(basename "$0")                  Interactive install into ~/$DEFAULT_WS_NAME.
  $(basename "$0") -y               Non-interactive; install all components.
  $(basename "$0") -p ~/my_ws -y    All components into ~/my_ws (unattended).
EOF
}

while getopts 'hp:y' opt; do
    case "$opt" in
        h) usage; exit 0;;
        p) WORKSPACE_PATH=$OPTARG;;
        y) ASSUME_YES=true;;
        *) usage; exit 1;;
    esac
done

# ---------- helpers --------------------------------------------------------
confirm() {
    # confirm "question" [default_yes]   -> 0 if yes, 1 if no
    local q="$1"; local default_y="${2:-true}"
    if $ASSUME_YES; then return 0; fi
    local hint="[Y/n]"; [[ "$default_y" != "true" ]] && hint="[y/N]"
    local reply
    while true; do
        read -r -p "$(echo -e "${BLU}${BOLD}$q${NORM}${OFF} $hint ")" reply
        case "$reply" in
            "")     [[ "$default_y" == "true" ]] && return 0 || return 1;;
            y|Y|yes|YES) return 0;;
            n|N|no|NO)   return 1;;
            *) echo "Please answer y or n.";;
        esac
    done
}

clone_if_missing() {
    # clone_if_missing <url> <dest_dir> [extra git args, e.g. -b noetic]
    local url="$1"; local dest="$2"; shift 2
    if [[ -d "$dest/.git" ]]; then
        ok "Skip clone (already present): $dest"
        return 0
    fi
    info "git clone $url -> $dest"
    git clone "$@" "$url" "$dest" || fail "Failed to clone $url"
}

# ---------- OS check -------------------------------------------------------
check_os() {
    info "Checking OS compatibility..."
    if [[ ! -f /etc/os-release ]]; then
        fail "Cannot read /etc/os-release; this script supports Ubuntu 20.04 only."
    fi
    . /etc/os-release
    if [[ "$ID" != "ubuntu" ]]; then
        fail "Detected $PRETTY_NAME. This script supports Ubuntu 20.04 (focal) only — ROS Noetic does not officially support other distros."
    fi
    if [[ "$VERSION_ID" != "20.04" ]]; then
        fail "Detected Ubuntu $VERSION_ID. This script supports Ubuntu 20.04 (focal) only — ROS Noetic does not officially support other Ubuntu versions."
    fi
    ok "Detected $PRETTY_NAME (compatible)."
}

# ---------- workspace resolution ------------------------------------------
resolve_workspace() {
    # Sets WORKSPACE_PATH to an absolute path with src/ underneath.
    if [[ -z "$WORKSPACE_PATH" ]]; then
        if $ASSUME_YES; then
            WORKSPACE_PATH="$HOME/$DEFAULT_WS_NAME"
        else
            read -r -p "$(echo -e "${BLU}${BOLD}Workspace path${NORM}${OFF} [default: ~/$DEFAULT_WS_NAME] ")" reply
            WORKSPACE_PATH="${reply:-$HOME/$DEFAULT_WS_NAME}"
        fi
    fi
    # Expand ~ and convert to absolute.
    WORKSPACE_PATH="${WORKSPACE_PATH/#\~/$HOME}"
    [[ "$WORKSPACE_PATH" != /* ]] && WORKSPACE_PATH="$PWD/$WORKSPACE_PATH"

    # Strip trailing slash and trailing /src so the user can pass either.
    WORKSPACE_PATH="${WORKSPACE_PATH%/}"
    WORKSPACE_PATH="${WORKSPACE_PATH%/src}"

    # Sanity check the name.
    if [[ ! "$(basename "$WORKSPACE_PATH")" =~ _ws$ ]]; then
        warn "Workspace path '$WORKSPACE_PATH' doesn't end in '_ws' (convention)."
        if ! confirm "Use it anyway?" true; then
            WORKSPACE_PATH="$HOME/$DEFAULT_WS_NAME"
            info "Falling back to default: $WORKSPACE_PATH"
        fi
    fi

    # Ensure the src/ subfolder exists.
    if [[ ! -d "$WORKSPACE_PATH/src" ]]; then
        info "Workspace '$WORKSPACE_PATH/src' doesn't exist yet."
        if confirm "Create it?" true; then
            mkdir -p "$WORKSPACE_PATH/src" || fail "Failed to mkdir $WORKSPACE_PATH/src"
            ok "Created $WORKSPACE_PATH/src"
        else
            fail "No workspace directory; aborting."
        fi
    fi
    ok "Workspace: $WORKSPACE_PATH"
}

# ---------- step: install ROS Noetic --------------------------------------
install_ros_noetic() {
    info "[1/5] ROS Noetic..."
    if dpkg-query -W -f='${Status}' ros-noetic-desktop-full 2>/dev/null | grep -q "ok installed"; then
        ok "ros-noetic-desktop-full already installed."
        return 0
    fi
    sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list' \
        || fail "Failed to add ROS apt repo"
    sudo apt install -y curl gnupg2 || fail "Failed to install curl/gnupg2"
    curl -sSL 'https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc' | sudo apt-key add - \
        || fail "Failed to add ROS apt key"
    sudo apt update || fail "apt update failed"
    sudo apt install -y ros-noetic-desktop-full || fail "Failed to install ros-noetic-desktop-full"
    if ! grep -q "source /opt/ros/noetic/setup.bash" "$HOME/.bashrc"; then
        echo "source /opt/ros/noetic/setup.bash" >> "$HOME/.bashrc"
    fi
    # shellcheck disable=SC1091
    source /opt/ros/noetic/setup.bash
    sudo apt install -y python3-rosdep python3-rosinstall python3-rosinstall-generator \
                        python3-wstool python3-catkin-tools build-essential \
        || fail "Failed to install ROS build tools"
    if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
        sudo rosdep init || warn "rosdep init failed (already initialised?)"
    fi
    rosdep update || warn "rosdep update failed (network?)"
    ok "ROS Noetic installed."
}

# ---------- step: system dependencies -------------------------------------
install_system_deps() {
    info "Installing system dependencies (xterm, MoveIt, pykdl, ...)"
    sudo apt install -y \
        xterm \
        ros-noetic-moveit \
        python3-pykdl \
        ros-noetic-kdl-parser-py \
        ros-noetic-trac-ik \
        ros-noetic-urdf-parser-plugin \
        ros-noetic-urdfdom-py \
        ros-noetic-urdf-tutorial \
        ros-noetic-apriltag-ros \
        ros-noetic-tf2-ros \
        ros-noetic-tf2-geometry-msgs \
        ros-noetic-realsense2-camera \
        python3-pip \
        || fail "Failed to install system dependencies"
    pip3 install --user transforms3d modern_robotics \
        || warn "pip3 install transforms3d / modern_robotics failed"

    # pykdl_utils: source-build from ncbdrck/hrl-kdl (modified for Noetic).
    if [[ ! -d "$WORKSPACE_PATH/src/hrl-kdl/.git" ]]; then
        info "Source-building pykdl_utils + hrl_geom from ncbdrck/hrl-kdl ..."
        clone_if_missing "https://github.com/ncbdrck/hrl-kdl.git" "$WORKSPACE_PATH/src/hrl-kdl"
        (cd "$WORKSPACE_PATH/src/hrl-kdl/pykdl_utils" && python3 setup.py build && sudo python3 setup.py install) \
            || fail "Failed to install pykdl_utils"
        (cd "$WORKSPACE_PATH/src/hrl-kdl/hrl_geom" && python3 setup.py build && sudo python3 setup.py install) \
            || fail "Failed to install hrl_geom"
    else
        ok "hrl-kdl already cloned; pykdl_utils + hrl_geom skipped."
    fi
    ok "System dependencies installed."
}

# ---------- step: install UniROS (with multiros + realros submodules) -----
install_uniros() {
    info "[2/5] UniROS (with MultiROS + RealROS submodules)..."
    clone_if_missing "https://github.com/ncbdrck/UniROS.git" "$WORKSPACE_PATH/src/uniros" \
        --recurse-submodules -b gymnasium
    # Make sure the gymnasium branch is checked out everywhere (clone may
    # default to main on older Git versions).
    (cd "$WORKSPACE_PATH/src/uniros" && git checkout gymnasium && git pull --ff-only) || true
    (cd "$WORKSPACE_PATH/src/uniros" && git submodule update --remote --recursive) || true
    if [[ -d "$WORKSPACE_PATH/src/uniros/multiros" ]]; then
        (cd "$WORKSPACE_PATH/src/uniros/multiros" && git checkout gymnasium && git pull --ff-only) || true
    fi
    if [[ -d "$WORKSPACE_PATH/src/uniros/realros" ]]; then
        (cd "$WORKSPACE_PATH/src/uniros/realros" && git checkout gymnasium && git pull --ff-only) || true
    fi

    for req in uniros/uniros/requirements.txt \
               uniros/multiros/requirements.txt \
               uniros/realros/requirements.txt; do
        if [[ -f "$WORKSPACE_PATH/src/$req" ]]; then
            pip3 install --user -r "$WORKSPACE_PATH/src/$req" \
                || warn "pip3 install -r $req had issues"
        fi
    done
    ok "UniROS installed."
}

# ---------- step: sb3_ros_support -----------------------------------------
install_sb3_ros_support() {
    info "[3/5] sb3_ros_support (Stable Baselines3 wrappers)..."
    clone_if_missing "https://github.com/ncbdrck/sb3_ros_support.git" \
                     "$WORKSPACE_PATH/src/sb3_ros_support" -b gymnasium
    (cd "$WORKSPACE_PATH/src/sb3_ros_support" && git checkout gymnasium && git pull --ff-only) || true
    if [[ -f "$WORKSPACE_PATH/src/sb3_ros_support/requirements.txt" ]]; then
        pip3 install --user -r "$WORKSPACE_PATH/src/sb3_ros_support/requirements.txt" \
            || warn "pip3 install sb3_ros_support requirements had issues"
    fi
    ok "sb3_ros_support installed."
}

# ---------- step: rl_environments + all robot deps ------------------------
install_rl_environments() {
    info "[4/5] rl_environments + 4-robot vendor packages + supporting repos..."

    # The RL env package itself + supporting description-extras + cube tracker.
    clone_if_missing "https://github.com/ncbdrck/rl_environments.git"          "$WORKSPACE_PATH/src/rl_environments"
    clone_if_missing "https://github.com/ncbdrck/rl_envs_cube_tracker.git"     "$WORKSPACE_PATH/src/rl_envs_cube_tracker"
    clone_if_missing "https://github.com/ncbdrck/reactorx200_description.git"  "$WORKSPACE_PATH/src/reactorx200_description"
    clone_if_missing "https://github.com/ncbdrck/viperx300s_description.git"   "$WORKSPACE_PATH/src/viperx300s_description"
    clone_if_missing "https://github.com/ncbdrck/ur5e_description_extras.git"  "$WORKSPACE_PATH/src/ur5e_description_extras"
    clone_if_missing "https://github.com/ncbdrck/niryo_ned2_description_extras.git" "$WORKSPACE_PATH/src/niryo_ned2_description_extras"
    clone_if_missing "https://github.com/ncbdrck/common-sensors.git"           "$WORKSPACE_PATH/src/common-sensors"

    # Robot vendor packages — needed for the envs to construct on hardware
    # (the sim envs also pull URDFs from these). Cloned unconditionally
    # because every one of our 4 robots needs them.

    # Trossen Interbotix (RX200 + VX300S).
    info "Cloning Interbotix ROS packages (RX200 + VX300S)..."
    clone_if_missing "https://github.com/Interbotix/interbotix_ros_core.git"          "$WORKSPACE_PATH/src/interbotix_ros_core"          -b noetic
    clone_if_missing "https://github.com/Interbotix/interbotix_ros_manipulators.git"  "$WORKSPACE_PATH/src/interbotix_ros_manipulators"  -b noetic
    clone_if_missing "https://github.com/Interbotix/interbotix_ros_toolboxes.git"     "$WORKSPACE_PATH/src/interbotix_ros_toolboxes"     -b noetic
    # The Interbotix repos ship CATKIN_IGNORE markers in subdirs that we
    # actually need; remove them so catkin sees the packages.
    for f in \
        "$WORKSPACE_PATH/src/interbotix_ros_core/interbotix_ros_xseries/CATKIN_IGNORE" \
        "$WORKSPACE_PATH/src/interbotix_ros_manipulators/interbotix_ros_xsarms/CATKIN_IGNORE" \
        "$WORKSPACE_PATH/src/interbotix_ros_manipulators/interbotix_ros_xsarms/interbotix_xsarm_perception/CATKIN_IGNORE" \
        "$WORKSPACE_PATH/src/interbotix_ros_toolboxes/interbotix_perception_toolbox/CATKIN_IGNORE" \
        "$WORKSPACE_PATH/src/interbotix_ros_toolboxes/interbotix_xs_toolbox/CATKIN_IGNORE" \
        "$WORKSPACE_PATH/src/interbotix_ros_toolboxes/interbotix_common_toolbox/interbotix_moveit_interface/CATKIN_IGNORE"
    do [[ -f "$f" ]] && rm -f "$f" && info "  removed $(basename "$f") under $(dirname "$f")"; done
    # Interbotix USB perms. Skipped in container builds (no udevd, no
    # /etc/udev access) — install these on the *host* if you'll be
    # passing /dev/ttyDXL through to the container.
    if [[ "${UNIROS_INSTALL_IN_DOCKER:-0}" == "1" ]]; then
        info "  skipping Interbotix udev rules (in-container build; install on host instead)."
    elif [[ -f "$WORKSPACE_PATH/src/interbotix_ros_core/interbotix_ros_xseries/interbotix_xs_sdk/99-interbotix-udev.rules" ]]; then
        if [[ ! -f /etc/udev/rules.d/99-interbotix-udev.rules ]]; then
            sudo cp "$WORKSPACE_PATH/src/interbotix_ros_core/interbotix_ros_xseries/interbotix_xs_sdk/99-interbotix-udev.rules" \
                    /etc/udev/rules.d/ \
                && sudo udevadm control --reload-rules && sudo udevadm trigger \
                && ok "Installed Interbotix udev rules (replug U2D2 for /dev/ttyDXL)."
        fi
    fi
    pip3 install --user transforms3d modern_robotics || true

    # Niryo Ned2.
    info "Cloning Niryo Ned2 ROS package..."
    clone_if_missing "https://github.com/NiryoRobotics/ned_ros.git" "$WORKSPACE_PATH/src/ned_ros"
    if [[ -d "$WORKSPACE_PATH/src/ned_ros/.git" ]]; then
        (cd "$WORKSPACE_PATH/src/ned_ros" && git submodule update --init ros-foxglove-bridge 2>/dev/null) || true
        if [[ -f "$WORKSPACE_PATH/src/ned_ros/requirements.txt" ]]; then
            pip3 install --user -r "$WORKSPACE_PATH/src/ned_ros/requirements.txt" \
                || warn "ned_ros requirements.txt install had issues"
        fi
        sudo apt install -y sqlite3 ffmpeg || warn "Niryo system deps (sqlite3, ffmpeg) install had issues"
    fi

    # Universal Robots UR5e + Robotiq gripper + the MoveIt config that
    # ur5e_description_extras's launch files include.
    info "Cloning UR5e + Robotiq + MoveIt config packages..."
    clone_if_missing "https://github.com/ros-industrial/universal_robot.git" \
                     "$WORKSPACE_PATH/src/universal_robot" -b "$ROS_DISTRO-devel" \
        || clone_if_missing "https://github.com/ros-industrial/universal_robot.git" \
                            "$WORKSPACE_PATH/src/universal_robot"
    clone_if_missing "https://github.com/filesmuggler/robotiq.git" "$WORKSPACE_PATH/src/robotiq"
    clone_if_missing "https://github.com/ncbdrck/ur5e_robotiq_85_moveit_config.git" \
                     "$WORKSPACE_PATH/src/ur5e_robotiq_85_moveit_config"
    sudo apt install -y ros-noetic-ur-robot-driver ros-noetic-ur-calibration \
        || warn "UR robot driver install had issues (real-hardware optional)"
    ok "rl_environments + vendor packages cloned."
}

# ---------- step: rl_training_validation ---------------------------------
install_rl_training_validation() {
    info "[5/5] rl_training_validation (SB3 train + validate scripts)..."
    clone_if_missing "https://github.com/ncbdrck/rl_training_validation.git" \
                     "$WORKSPACE_PATH/src/rl_training_validation"
    if [[ -f "$WORKSPACE_PATH/src/rl_training_validation/requirements.txt" ]]; then
        pip3 install --user -r "$WORKSPACE_PATH/src/rl_training_validation/requirements.txt" \
            || warn "pip3 install rl_training_validation requirements had issues"
    fi
    ok "rl_training_validation installed."
}

# ---------- step: build the workspace -------------------------------------
build_workspace() {
    info "Building the workspace with catkin..."
    cd "$WORKSPACE_PATH" || fail "Cannot cd $WORKSPACE_PATH"
    if [[ ! -f "$WORKSPACE_PATH/.catkin_tools" ]] && [[ ! -d "$WORKSPACE_PATH/.catkin_tools" ]]; then
        catkin init || warn "catkin init returned non-zero (probably already initialised)"
    fi
    rosdep install --from-paths src --ignore-src -r -y --skip-keys "python-rpi.gpio" \
        || warn "rosdep install had issues"
    catkin build || fail "catkin build failed"
    if ! grep -q "source $WORKSPACE_PATH/devel/setup.bash" "$HOME/.bashrc"; then
        if confirm "Append 'source $WORKSPACE_PATH/devel/setup.bash' to your ~/.bashrc?" true; then
            echo "source $WORKSPACE_PATH/devel/setup.bash" >> "$HOME/.bashrc"
            ok "Appended to ~/.bashrc"
        fi
    fi
    # shellcheck disable=SC1090
    source "$WORKSPACE_PATH/devel/setup.bash" || true
    ok "Workspace built."
}

# ---------- top-level orchestration --------------------------------------
main() {
    info "UniROS RL stack installer"

    check_os
    resolve_workspace

    local install_all=true
    if ! $ASSUME_YES; then
        if ! confirm "Install ALL components (recommended for first-time setup)?" true; then
            install_all=false
        fi
    fi

    # Per-component flags. Defaults match install_all.
    local INSTALL_ROS=$install_all
    local INSTALL_UNIROS=$install_all
    local INSTALL_SB3=$install_all
    local INSTALL_RL_ENVS=$install_all
    local INSTALL_RL_TRAIN=$install_all

    if ! $install_all; then
        info "Per-component selection:"
        confirm "Install ROS Noetic?" true                                                && INSTALL_ROS=true       || INSTALL_ROS=false
        confirm "Install UniROS framework (multiros + realros submodules)?" true          && INSTALL_UNIROS=true    || INSTALL_UNIROS=false
        confirm "Install sb3_ros_support (Stable Baselines3 wrappers)?" true              && INSTALL_SB3=true       || INSTALL_SB3=false
        confirm "Install rl_environments + 4 robots' vendor packages + helpers?" true     && INSTALL_RL_ENVS=true   || INSTALL_RL_ENVS=false
        confirm "Install rl_training_validation (train + validate scripts)?" true         && INSTALL_RL_TRAIN=true  || INSTALL_RL_TRAIN=false
    fi

    if $INSTALL_ROS;       then install_ros_noetic;             install_system_deps; fi
    if $INSTALL_UNIROS;    then install_uniros;                                       fi
    if $INSTALL_SB3;       then install_sb3_ros_support;                              fi
    if $INSTALL_RL_ENVS;   then install_rl_environments;                              fi
    if $INSTALL_RL_TRAIN;  then install_rl_training_validation;                       fi

    build_workspace

    echo ""
    ok "Done!  source $WORKSPACE_PATH/devel/setup.bash"
    echo ""
    info "Next steps:"
    echo "    1) List the registered envs:"
    echo "         cd $WORKSPACE_PATH/src/rl_training_validation"
    echo "         python3 scripts/list_available_envs.py"
    echo ""
    echo "    2) Run a smoke training of the RX200 reacher:"
    echo "         roscore   # in one terminal"
    echo "         rosrun rl_training_validation rx200_reach_train_sim.py --gazebo-gui"
    echo ""
    echo "    3) Read the docs:"
    echo "         https://uniros.readthedocs.io/"
}

main "$@"
