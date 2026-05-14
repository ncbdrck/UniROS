"""
Shared pytest fixtures and rospy / catkin stubs.

These tests are designed to run WITHOUT a live ROS install. We stub
the rospy ecosystem with no-op equivalents so the unit-under-test
can import them, but every behaviour we exercise is pure Python.

Anything that genuinely requires Gazebo or a roscore is out of scope
for this test suite and lives elsewhere (manual integration tests
the developer runs locally with `catkin build && source devel/setup.bash`).
"""
import sys
import types
import pytest


def _stub(name, attrs=None):
    """Install ``name`` as a fresh stub module if not already present."""
    if name in sys.modules:
        return sys.modules[name]
    sys.modules[name] = types.SimpleNamespace(**(attrs or {}))
    return sys.modules[name]


@pytest.fixture(autouse=True, scope="session")
def stub_rospy_ecosystem():
    """
    Provide minimal stubs for rospy / rospkg / xacro / std_msgs / etc.
    so tests can import code that does ``import rospy`` etc. without
    a live ROS install. Session-scoped so the stubs persist for the
    whole pytest run.
    """
    captured_shutdown_callbacks: list = []

    _stub("rospy", {
        "loginfo":   lambda *a, **k: None,
        "logwarn":   lambda *a, **k: None,
        "logdebug":  lambda *a, **k: None,
        "logerr":    lambda *a, **k: None,
        "logfatal":  lambda *a, **k: None,
        "ROSException": Exception,
        "ROSInterruptException": Exception,
        "on_shutdown": lambda cb: captured_shutdown_callbacks.append(cb),
        "is_shutdown": lambda: False,
        "init_node":  lambda *a, **k: None,
        "wait_for_service": lambda *a, **k: None,
        "Duration":   lambda *a, **k: types.SimpleNamespace(),
        "Time":       types.SimpleNamespace(now=lambda: types.SimpleNamespace()),
        "Rate":       lambda *a, **k: types.SimpleNamespace(sleep=lambda: None),
        "Publisher":  lambda *a, **k: types.SimpleNamespace(publish=lambda *a2, **k2: None),
        "ServiceProxy": lambda *a, **k: (lambda *a2, **k2: None),
        # Test introspection: expose the shutdown callback list
        "_test_shutdown_callbacks": captured_shutdown_callbacks,
    })
    _stub("rosparam", {"upload_params": lambda *a, **k: None})
    _stub("rospkg", {
        "RosPack": lambda: types.SimpleNamespace(get_path=lambda *a: "/tmp"),
        "common":  types.SimpleNamespace(ResourceNotFound=Exception),
    })
    _stub("xacro", {"process_file": lambda *a, **k: None})

    # ROS message packages used by the canonical utility modules
    class _DummyMsg:
        def __init__(self, *a, **k):
            for k_, v_ in k.items():
                setattr(self, k_, v_)

    class _MarkerMsg:
        SPHERE = 2; CUBE = 1; CYLINDER = 3; LINE_LIST = 5
        ARROW = 0; ADD = 0; DELETE = 2; MODIFY = 0; DELETEALL = 3
        def __init__(self, *a, **k): pass

    class _MarkerArrayMsg:
        def __init__(self, *a, **k):
            self.markers = []

    _stub("visualization_msgs", {})
    _stub("visualization_msgs.msg", {
        "Marker": _MarkerMsg, "MarkerArray": _MarkerArrayMsg,
    })
    _stub("geometry_msgs", {})
    _stub("geometry_msgs.msg", {
        "Point": _DummyMsg, "Pose": _DummyMsg, "Quaternion": _DummyMsg,
        "Vector3": _DummyMsg, "PoseStamped": _DummyMsg, "Twist": _DummyMsg,
        "Transform": _DummyMsg, "TransformStamped": _DummyMsg,
    })
    _stub("std_msgs", {})
    _stub("std_msgs.msg", {
        "ColorRGBA": _DummyMsg, "Header": _DummyMsg, "Float64": _DummyMsg,
        "String": _DummyMsg, "Bool": _DummyMsg,
    })
    _stub("sensor_msgs", {})
    _stub("sensor_msgs.msg", {
        "JointState": _DummyMsg, "Image": _DummyMsg, "PointCloud2": _DummyMsg,
    })
    _stub("controller_manager_msgs", {})
    _stub("controller_manager_msgs.srv", {
        "LoadController": _DummyMsg, "LoadControllerRequest": _DummyMsg,
        "UnloadController": _DummyMsg, "UnloadControllerRequest": _DummyMsg,
        "ListControllers": _DummyMsg, "ListControllersRequest": _DummyMsg,
        "SwitchController": _DummyMsg, "SwitchControllerRequest": _DummyMsg,
        "ReloadControllerLibraries": _DummyMsg,
    })
    _stub("tf", {})
    _stub("tf.transformations", {
        "quaternion_from_euler": lambda *a, **k: (0.0, 0.0, 0.0, 1.0),
        "euler_from_quaternion": lambda *a, **k: (0.0, 0.0, 0.0),
        "euler_from_matrix":     lambda *a, **k: (0.0, 0.0, 0.0),
        "quaternion_matrix":     lambda *a, **k: [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
    })

    yield captured_shutdown_callbacks


@pytest.fixture
def fresh_shutdown_callbacks(stub_rospy_ecosystem):
    """Clear the captured rospy.on_shutdown list before/after each test."""
    stub_rospy_ecosystem.clear()
    yield stub_rospy_ecosystem
    stub_rospy_ecosystem.clear()
