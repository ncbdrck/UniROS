"""
Smoke tests for the public API of ``uniros.utils.*``.

These modules host the canonical implementations of ros_markers,
ros_kinematics, and ros_controllers (the modules that multiros and
realros re-export from). Tests
here protect the import surface so that future refactors don't
silently drop public names that multiros / realros re-export.

Note: ros_kinematics has heavy KDL / urdf_parser dependencies that
are awkward to stub. We test only the existence of the expected
top-level names by reading the module's AST without actually
executing it.
"""
import ast
import pathlib
import pytest


HERE = pathlib.Path(__file__).resolve().parent
UNIROS_ROOT = HERE.parent / "src" / "uniros"


def _public_top_level_names_from_file(path: pathlib.Path) -> set:
    """Parse a Python file and return the names of top-level classes and functions."""
    tree = ast.parse(path.read_text())
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef))
        and not node.name.startswith("_")
    }


class TestRosMarkersAPI:
    """ros_markers public surface (canonical home)."""

    def test_imports(self):
        from uniros.utils.ros_markers import RosMarker, RosMarkerArray
        assert RosMarker is not None
        assert RosMarkerArray is not None

    def test_top_level_names_stable(self):
        names = _public_top_level_names_from_file(
            UNIROS_ROOT / "utils" / "ros_markers.py"
        )
        # If you intentionally add or remove a public class, update this set.
        assert names == {"RosMarker", "RosMarkerArray"}, (
            f"Public surface of uniros.utils.ros_markers changed: {names}"
        )


class TestRosControllersAPI:
    """ros_controllers public surface (canonical home)."""

    EXPECTED = {
        "load_ros_controller", "load_controller_list", "list_loaded_controllers",
        "unload_ros_controller", "unload_controller_list", "switch_controllers",
        "start_controllers", "stop_controllers", "reset_controllers",
        "spawn_controllers", "unspawn_controllers",
    }

    def test_imports(self):
        import uniros.utils.ros_controllers as mod
        for name in self.EXPECTED:
            assert hasattr(mod, name), f"uniros.utils.ros_controllers missing {name}"

    def test_top_level_names_stable(self):
        names = _public_top_level_names_from_file(
            UNIROS_ROOT / "utils" / "ros_controllers.py"
        )
        assert names == self.EXPECTED, (
            f"Public surface of uniros.utils.ros_controllers changed: "
            f"added={names - self.EXPECTED}, removed={self.EXPECTED - names}"
        )


class TestRosKinematicsAPI:
    """ros_kinematics public surface (canonical home).

    AST-based check only — PyKDL / urdf_parser_py are heavy native deps
    and we don't want the test suite to require them.
    """

    EXPECTED = {"Kinematics_pyrobot", "Kinematics_pykdl"}

    def test_top_level_names_stable(self):
        names = _public_top_level_names_from_file(
            UNIROS_ROOT / "utils" / "ros_kinematics.py"
        )
        assert names == self.EXPECTED, (
            f"Public surface of uniros.utils.ros_kinematics changed: "
            f"added={names - self.EXPECTED}, removed={self.EXPECTED - names}"
        )
