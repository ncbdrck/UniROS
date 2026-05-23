# UniROS RL stack — Ubuntu 20.04 + ROS Noetic + framework + 4 robots.
#
# Build (from the directory containing this Dockerfile):
#   docker build -t uniros:noetic .
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

# Run the installer at image build time. UNIROS_INSTALL_IN_DOCKER=1
# tells the installer to skip the udev-rules step (no udevd in the
# container; install those rules on the *host* if you'll be passing
# /dev/ttyDXL through).
COPY install_uniros_stack.sh /tmp/install_uniros_stack.sh
RUN chmod +x /tmp/install_uniros_stack.sh \
    && UNIROS_INSTALL_IN_DOCKER=1 \
       /tmp/install_uniros_stack.sh -y -p /root/uniros_ws \
    && rm -f /tmp/install_uniros_stack.sh \
    && rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache/pip

# Container entry: drop into bash with the workspace already sourced
# (the installer appended the source line to /root/.bashrc).
WORKDIR /root/uniros_ws
ENTRYPOINT ["/bin/bash"]
