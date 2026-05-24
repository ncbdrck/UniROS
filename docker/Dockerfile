# UniROS RL stack — Ubuntu 20.04 + ROS Noetic + framework + 4 robots.
#
# Build (from the directory containing this Dockerfile):
#   ./build.sh                          # default: CUDA-runtime base (~16 GB)
#   ./build.sh --slim                   # osrf base, no CUDA in image (~12 GB)
#
# Two supported base images are selected by the BASE_IMAGE build arg:
#   nvidia/cuda:12.9.2-runtime-ubuntu20.04   # default; PyTorch/TF GPU
#                                              works inside the container.
#   osrf/ros:noetic-desktop-full-focal       # --slim; no CUDA libs baked
#                                              in. Smaller image; training
#                                              inside container is CPU-only
#                                              unless you bring your own
#                                              GPU PyTorch wheel.
#
# Headless run:        ./run.sh
# GUI run (rocker):    ./run_gui.sh
#
# Canonical copy lives in github.com/ncbdrck/UniROS. Identical copies
# are kept in the other 5 ecosystem repos (MultiROS, RealROS,
# sb3_ros_support, rl_environments, rl_training_validation) so users
# can build it from whichever repo they cloned first.

ARG BASE_IMAGE=nvidia/cuda:12.9.2-runtime-ubuntu20.04
FROM ${BASE_IMAGE}

ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Etc/UTC
ENV DEBIAN_FRONTEND=${DEBIAN_FRONTEND} \
    DEBCONF_NONINTERACTIVE_SEEN=true \
    TZ=${TZ}

# Make long ROS / Ubuntu apt transactions less fragile in Docker builds.
# This helps with transient mirror/network errors such as failed downloads
# of large dependency sets while installing ros-noetic-desktop-full.
RUN printf 'Acquire::Retries "5";\nAcquire::http::Timeout "60";\nAcquire::https::Timeout "60";\n' \
        > /etc/apt/apt.conf.d/80-retries

# Pre-seed every debconf prompt that has historically shown up when ROS /
# MoveIt / X11 / keyboard packages get pulled in transitively. With these
# answers locked in, no install step can block waiting for keyboard layout,
# timezone region, or console encoding selection — even if a package
# silently resets the debconf frontend internally.
RUN apt-get update \
    && apt-get install -y --no-install-recommends debconf-utils \
    && echo "tzdata tzdata/Areas select Etc"                                        | debconf-set-selections \
    && echo "tzdata tzdata/Zones/Etc select UTC"                                    | debconf-set-selections \
    && echo "keyboard-configuration keyboard-configuration/layoutcode string us"    | debconf-set-selections \
    && echo "keyboard-configuration keyboard-configuration/layout select English (US)" | debconf-set-selections \
    && echo "keyboard-configuration keyboard-configuration/variantcode string"      | debconf-set-selections \
    && echo "keyboard-configuration keyboard-configuration/modelcode string pc105"  | debconf-set-selections \
    && echo "keyboard-configuration keyboard-configuration/xkb-keymap select us"    | debconf-set-selections \
    && echo "console-setup console-setup/charmap47 select UTF-8"                    | debconf-set-selections \
    && echo "console-setup console-setup/codeset47 select Guess optimal character set" | debconf-set-selections \
    && rm -rf /var/lib/apt/lists/*

# The container runs as a non-root user so that bind-mounted host
# workspaces don't end up with root-owned build/ and devel/ files.
# UID/GID are build-time arguments — build.sh defaults them to the
# host's UID/GID so the bind-mount UX "just works" on Linux desktops.
ARG USERNAME=uniros
ARG USER_UID=1000
ARG USER_GID=1000

# Minimal system deps the installer itself needs to bootstrap. Everything
# else (ROS Noetic, framework packages, vendor robot packages, pip deps)
# is pulled in by install_uniros_stack.sh. Terminator is included for an
# easier multi-terminal workflow when running the GUI container.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        gnupg2 \
        lsb-release \
        locales \
        sudo \
        tzdata \
        build-essential \
        python3-pip \
        ncurses-bin \
        terminator \
    && ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && locale-gen en_US.UTF-8 \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

# Override the base image's NVIDIA_DRIVER_CAPABILITIES (which is set to
# the minimal "compute,utility" by nvidia/cuda images). Without
# "graphics" the NVIDIA Container Toolkit does NOT inject libGLX_nvidia
# / libEGL_nvidia at runtime, so libglvnd falls back to Mesa and any
# 3D app (Gazebo, RViz with OGRE) errors out trying to load
# nvidia-drm_dri.so. "all" enables graphics, compute, utility, video,
# and display.
ENV NVIDIA_DRIVER_CAPABILITIES=all

# Create the install user with passwordless sudo. The installer uses
# sudo for system-level steps (apt, rosdep init). Preserve the noninteractive
# debconf environment through sudo so package configuration cannot block
# Docker builds with prompts such as keyboard layout selection.
RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m -s /bin/bash ${USERNAME} \
    && { \
        echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL"; \
        echo 'Defaults env_keep += "DEBIAN_FRONTEND DEBCONF_NONINTERACTIVE_SEEN TZ"'; \
    } > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

USER ${USERNAME}
WORKDIR /home/${USERNAME}

# Run the installer at image build time. UNIROS_INSTALL_IN_DOCKER=1
# tells the installer to skip the udev-rules step (no udevd in the
# container; install those rules on the *host* if you'll be passing
# /dev/ttyDXL through). The workspace is created under the uniros
# user's HOME so bind mounts on a host with matching UID work cleanly.
COPY --chown=${USERNAME}:${USERNAME} install_uniros_stack.sh /tmp/install_uniros_stack.sh
RUN chmod +x /tmp/install_uniros_stack.sh \
    && UNIROS_INSTALL_IN_DOCKER=1 \
       /tmp/install_uniros_stack.sh -y -p /home/${USERNAME}/uniros_ws \
    && sudo rm -f /tmp/install_uniros_stack.sh \
    && sudo rm -rf /var/lib/apt/lists/* /tmp/* \
    && rm -rf /home/${USERNAME}/.cache/pip

# Container entry: drop into bash with the workspace already sourced
# (the installer appended the source line to /home/uniros/.bashrc).
WORKDIR /home/${USERNAME}/uniros_ws
ENTRYPOINT ["/bin/bash"]
