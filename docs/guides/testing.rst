Testing
=======

Each of the four framework packages ships a pytest suite that runs
**without a live ROS install**. The rospy ecosystem (rospy, rospkg,
message packages, MoveIt, KDL, tf) is stubbed at conftest load time
so tests stay fast and developers can iterate without bringing up a
roscore.

Total coverage across the ecosystem: **103 tests**.

.. list-table:: Test inventory
   :widths: 22 14 64
   :header-rows: 1

   * - Package
     - Tests
     - Coverage
   * - uniros
     - 20
     - Gym proxy aliasing; end-to-end step/reset/__getattr__ across
       the multiprocessing pipe; unwrapped property; worker error
       propagation; idempotent close; canonical utils API surface.
   * - multiros
     - 33
     - Proxy re-export identity; kernel-based port allocator with
       20-thread concurrent test; cleanup registry + rospy.on_shutdown
       wiring; kill-helper rename with deprecated aliases; utility
       re-export identity.
   * - realros
     - 31
     - realros-shaped equivalent of the multiros suite.
   * - sb3_ros_support
     - 19
     - Smoke tests for BasicModel and the 10 algorithm subclasses.


Running the tests
-----------------

From the root of any package:

.. code-block:: bash

   cd ~/uniros_ws/src/<package_name>
   python3 -m pytest tests/ -v

Multiros and realros expect UniROS to be importable from a sibling
directory; the ``pytest.ini`` in each package's root already adds
the right paths.

A complete sweep:

.. code-block:: bash

   for pkg in UniROS/uniros multiros_v1/multiros realros sb3_ros_support; do
       echo "=== $pkg ==="
       (cd ~/uniros_ws/src/$pkg && python3 -m pytest tests/ -q)
   done


Continuous integration
----------------------

Each package has a ``.github/workflows/tests.yml`` that runs the
same pytest suite on push and pull request, with a Python 3.8 + 3.10
matrix on ``ubuntu-22.04``. Python 3.12 is intentionally skipped
until the ``setup.py`` files migrate from distutils to setuptools
(distutils was removed from 3.12's stdlib).

The workflows do **not** install ROS — they rely on the same stubs
the local tests use, so a green CI run reflects what passes on a
clean Ubuntu machine without Noetic installed.


Adding new tests
----------------

* Put new tests in the relevant package's ``tests/`` directory.
* If your test needs an extra ROS message type or third-party
  module that isn't already stubbed, add it to the package's
  ``tests/conftest.py`` ``_force_stub`` block — and add it to the
  workflow's ``pip install`` line if it's a pure-Python dep.
* Tests should run in under a second each. If you need a slow
  integration test (real ROS, real Gazebo), put it under
  ``tests/integration/`` and mark it ``@pytest.mark.integration``
  so it's excluded from the default run.
