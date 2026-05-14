"""
Sphinx configuration for the UniROS / MultiROS / RealROS ecosystem docs.

Builds the unified ecosystem documentation site hosted on Read the
Docs. autodoc reads docstrings directly from the source packages
(installed as editable on the build machine); ROS / Gazebo / KDL
dependencies that aren't available on RTD are mocked via
``autodoc_mock_imports`` so docstring extraction succeeds without a
real ROS install.
"""

import os
import sys
from datetime import date

# ---------------------------------------------------------------- Project

project = "UniROS ecosystem"
author = "Jayasekara Kapukotuwa"
copyright = f"{date.today().year}, {author}"
release = "1.0.0"
version = "1.0"

# ---------------------------------------------------------------- Source path
# Add the framework packages so autodoc can import them. Paths are
# relative to this conf.py file (UniROS/docs/conf.py).
#
# Two layouts are supported:
#
#   Read the Docs / fresh clone (with submodules):
#       UniROS/uniros/             - uniros Python package
#       UniROS/multiros/           - submodule
#       UniROS/realros/            - submodule
#       <next to UniROS>/sb3_ros_support/
#       <next to UniROS>/rl_environments/
#       <next to UniROS>/rl_training_validation/
#
#   Developer's local catkin workspace (where the multiros and realros
#   submodules are deleted because catkin can't have two packages with
#   the same <name>, so the real packages live alongside UniROS):
#       catkin_ws/src/UniROS/uniros/
#       catkin_ws/src/multiros_v1/multiros/   (nested wrapper)
#       catkin_ws/src/realros/
#       catkin_ws/src/sb3_ros_support/
#       rl_ws/src/rl_environments/            (different workspace)
#       rl_ws/src/rl_training_validation/
#
# Each candidate is tried in order; the first existing path wins.

_HERE = os.path.dirname(os.path.abspath(__file__))

_PACKAGE_CANDIDATES = {
    "uniros": [
        "../uniros/src",
    ],
    "multiros": [
        "../multiros/src",                       # RTD / fresh clone w/ submodules
        "../../multiros_v1/multiros/src",        # local catkin_ws layout
        "../../multiros/src",                    # alt local layout
    ],
    "realros": [
        "../realros/src",                        # RTD / fresh clone w/ submodules
        "../../realros/src",                     # local catkin_ws layout
    ],
    "sb3_ros_support": [
        "../sb3_ros_support/src",                # RTD clone
        "../../sb3_ros_support/src",             # local catkin_ws sibling
    ],
    "rl_environments": [
        "../rl_environments/src",                # RTD clone
        "../../../../rl_ws/src/rl_environments/src",  # local rl_ws layout (sibling of catkin_ws)
        "../../rl_environments/src",             # alt local layout
    ],
    "rl_training_validation": [
        "../rl_training_validation/src",         # RTD clone
        "../../../../rl_ws/src/rl_training_validation/src",  # local rl_ws layout
        "../../rl_training_validation/src",      # alt local layout
    ],
}
for pkg, candidates in _PACKAGE_CANDIDATES.items():
    for rel in candidates:
        abs_path = os.path.abspath(os.path.join(_HERE, rel))
        if os.path.isdir(abs_path):
            sys.path.insert(0, abs_path)
            break

# ---------------------------------------------------------------- Extensions

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",          # Google / NumPy-style docstrings
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",            # copy-to-clipboard for code blocks
    "myst_parser",                  # include .md files alongside .rst
]

# Allow .md to render as a first-class doc format.
source_suffix = {
    ".rst": "restructuredtext",
    ".md":  "markdown",
}

# Read the Docs / pre-2024 Sphinx put templates and exclude_patterns
# in the same neighbourhood — keep them grouped.
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# ---------------------------------------------------------------- HTML theme

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "titles_only": False,
}
html_show_sphinx = True
html_show_copyright = True

# ---------------------------------------------------------------- autodoc

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"
autoclass_content = "both"

# ROS, Gazebo, MoveIt, PyKDL, and message packages aren't installable
# on Read the Docs (Ubuntu 22 / Python 3.x without a Noetic apt mirror).
# Mock them so autodoc can introspect docstrings without crashing on
# unresolved imports.
autodoc_mock_imports = [
    "rospy", "rosparam", "rospkg", "rostopic", "xacro",
    "rospy.service",
    "visualization_msgs", "geometry_msgs", "std_msgs",
    "sensor_msgs", "controller_manager_msgs",
    "gazebo_msgs", "std_srvs", "nav_msgs",
    "tf", "tf2_ros", "tf.transformations",
    "moveit_commander", "moveit_msgs",
    "shape_msgs", "trajectory_msgs",
    "PyKDL", "kdl_parser_py", "urdf_parser_py",
    "pykdl_utils", "hrl_geom", "trac_ik_python",
    "torch", "stable_baselines3",
    # SB3 + TensorBoard transitively pull tensorflow on some installs;
    # mock both so docs builds on a developer machine don't print CUDA /
    # TensorRT warnings while reading the sb3_ros_support API.
    "tensorflow", "tensorboard",
    # rl_environments / rl_training_validation extras
    "cv2", "cv_bridge", "image_transport",
    "interbotix_xs_modules", "interbotix_xs_msgs",
    "niryo_robot_python_ros_wrapper", "niryo_robot_msgs",
    "ur_msgs", "ur_dashboard_msgs",
    "pyzed", "open3d",
]

# ---------------------------------------------------------------- napoleon

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_use_rtype = True

# ---------------------------------------------------------------- intersphinx

intersphinx_mapping = {
    "python":     ("https://docs.python.org/3", None),
    "numpy":      ("https://numpy.org/doc/stable", None),
    "gymnasium":  ("https://gymnasium.farama.org", None),
}

# ---------------------------------------------------------------- MyST

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "linkify",
]
myst_heading_anchors = 3
