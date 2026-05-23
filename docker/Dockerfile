# UniROS RL stack — Ubuntu 20.04 + ROS Noetic + framework + 4 robots.
#
# Build (from the directory containing this Dockerfile):
#   ./build.sh                          # uses your host UID/GID by default
#   docker build -t uniros:noetic .     # uses bake-time defaults (1000:1000)
#
# Headless run (Linux host):
#   ./run.sh
#
# GUI run (rocker; Linux host with X11):
#   ./run_gui.sh
#
# Canonical copy lives in github.com/ncbdrck/UniROS. Identical copies
# are kept in the other 5 ecosystem repos (MultiROS, RealROS,
# sb3_ros_support, rl_environments, rl_training_validation) so users
# can build it from whichever repo they cloned first.

FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Etc/UTC
ENV TZ=${TZ}

# The container runs as a non-root user so that bind-mounted host
# workspaces don't end up with root-owned build/ and devel/ files.
# UID/GID are build-time arguments — build.sh defaults them to the
# host's UID/GID so the bind-mount UX "just works" on Linux desktops.
ARG USERNAME=uniros
ARG USER_UID=1000
ARG USER_GID=1000

# Minimal system deps the installer itself needs to bootstrap. Everything
# else (ROS Noetic, framework packages, vendor robot packages, pip deps)
# is pulled in by install_uniros_stack.sh.
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
    && ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && locale-gen en_US.UTF-8 \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

# Create the install user with passwordless sudo. The installer uses
# sudo for system-level steps (apt, rosdep init); NOPASSWD keeps it
# non-interactive during the image build.
RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd --uid ${USER_UID} --gid ${USER_GID} -m -s /bin/bash ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
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
