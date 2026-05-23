# UniROS in Docker

The UniROS stack targets **ROS Noetic on Ubuntu 20.04**. Modern OEM
laptops and workstations (Ubuntu 22.04 / 24.04, RTX 50-series GPUs,
WSL2) can't easily install Noetic natively — this Docker image gives
them a turn-key Ubuntu 20.04 + ROS Noetic + UniROS environment that
runs on any Linux host with Docker installed.

The image installs everything `install_uniros_stack.sh` installs:
ROS Noetic, the four framework packages (UniROS, MultiROS, RealROS,
sb3_ros_support), the two application packages (rl_environments,
rl_training_validation), all four robots' description-extras helpers,
robot vendor packages (Interbotix RX200 + VX300S, Niryo Ned2, UR5e + Robotiq), and rl_envs_cube_tracker.

The container runs as a non-root `uniros` user (UID/GID configurable
at build time, defaults to the host's) so bind-mounted host workspaces
don't end up with root-owned `build/` and `devel/` files.

## Requirements

- Linux host (Ubuntu 20.04 / 22.04 / 24.04 tested) with
  [Docker](https://docs.docker.com/engine/install/ubuntu/) installed.
- Optional: [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
  if you want GPU-accelerated Gazebo rendering or PyTorch inside the
  container.
- Optional: [rocker](https://github.com/osrf/rocker) for GUI mode
  (`sudo apt install python3-rocker` or `pip3 install --user rocker`).

Windows users: install Docker Desktop with the WSL2 backend; WSL2 +
WSLg gives X11/GPU passthrough natively. Mac users: the container
will run but GUI passthrough and `--network=host` won't work as
cleanly as on Linux.

## Build

From this directory:

```bash
./build.sh
```

`build.sh` auto-detects your host UID/GID and passes them as
`--build-arg USER_UID=$(id -u) --build-arg USER_GID=$(id -g)`, so the
non-root `uniros` user inside the container has the same UID as you
on the host. First build takes 30–60 minutes depending on network
speed (it clones every robot vendor repo and pip-installs SB3 /
PyTorch); subsequent builds with no changes are fast.

Custom tag or explicit UID:

```bash
./build.sh -t myname/uniros:dev
./build.sh -u 1001 -g 1001          # different UID/GID
```

## Run

**Headless** (no Gazebo / RViz windows):

```bash
./run.sh
```

You land in `bash` as the `uniros` user inside the container with
`/home/uniros/uniros_ws` sourced. `rospy`, `roscore`, and headless
Gazebo all work. Use this for training scripts or for piping data
over `--network=host` to a learner on the host.

**With GUI** (Gazebo, RViz windows on host display, via rocker):

```bash
./run_gui.sh
```

Auto-detects NVIDIA. Pass `--no-gpu` to force software rendering
(Intel / AMD / llvmpipe). rocker's `--user` flag layers your current
host UID at runtime, so file ownership stays clean even if you
didn't rebuild after your host UID changed.

## Hardware passthrough

For real-robot work, edit `run.sh` (or `run_gui.sh`) and uncomment the
relevant lines:

- **USB serial robots** (Interbotix RX200 / VX300S over U2D2):
  - Install the udev rules on the **host** (not in the container; the
    installer detects `UNIROS_INSTALL_IN_DOCKER=1` and skips them).
    From the host workspace: `sudo cp ~/uniros_ws/src/interbotix_ros_core/interbotix_ros_xseries/interbotix_xs_sdk/99-interbotix-udev.rules /etc/udev/rules.d/ && sudo udevadm control --reload-rules && sudo udevadm trigger`.
  - Then in the run script, uncomment `--device=/dev/ttyDXL:/dev/ttyDXL`.

- **Network-attached robots** (Niryo Ned2, UR5e):
  - `--network=host` is already on by default in `run.sh`. Just set
    `ROS_MASTER_URI` to the robot's onboard rosmaster from inside the
    container (e.g. `export ROS_MASTER_URI=http://ned2.local:11311`).

## Active development (bind-mount your host workspace)

Both run scripts accept `-w` to bind-mount your host workspace over
`/home/uniros/uniros_ws` in the container. Useful when you're
editing source files on the host (in your IDE) and want the
container to see the changes immediately:

```bash
./run.sh -w ~/uniros_ws
./run_gui.sh -w ~/uniros_ws
```

The host workspace must be a fully bootstrapped catkin workspace
(`install_uniros_stack.sh -p ~/uniros_ws` on a Linux 20.04 host, or
inside another container). `catkin build` from inside the container
writes to `~/uniros_ws/build` and `~/uniros_ws/devel` on the host,
owned by the host user (because the container UID matches).

## Versions

The canonical copy of `Dockerfile`, `build.sh`, `run.sh`, `run_gui.sh`
and this README lives in
[ncbdrck/UniROS](https://github.com/ncbdrck/UniROS) under `docker/`.
Identical copies are kept in the other ecosystem repos (MultiROS,
RealROS, sb3_ros_support, rl_environments, rl_training_validation)
so you can build the image from whichever repo you cloned first.
