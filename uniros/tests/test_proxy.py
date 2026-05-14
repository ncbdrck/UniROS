"""
Regression tests for ``uniros._proxy.GymProxy`` — the multiprocessing
gym-env proxy that multiros / realros / uniros all share.

Covers the following invariants:
  - Worker-side exceptions surface as parent-side RuntimeError
    (worker error propagation across the pipe).
  - ``env.unwrapped is env`` (SB3 DummyVecEnv pickle compatibility).
  - ``close()`` is idempotent across multiple calls and ``__del__``.
  - All historical aliases (MultirosGym, RealrosGym, uniros_gym)
    resolve to the same class object.
"""
import pytest
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from uniros._proxy import GymProxy, _RemoteException
from uniros.core import uniros_gym
from uniros import GymProxy as TopLevelGymProxy
from uniros import uniros_gym as TopLevelUnirosGym


# Tiny stub env used by the multiprocessing tests below. Registered
# with entry_point as a class object (not a string) so the worker
# process — which inherits the gym registry via fork() — can
# construct it without needing to re-import this test module by name.
class _TinyEnv(gym.Env):
    def __init__(self):
        self.observation_space = spaces.Box(-1, 1, (3,), dtype=np.float32)
        self.action_space = spaces.Box(-1, 1, (2,), dtype=np.float32)
        self._step_count = 0

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._step_count = 0
        return self.observation_space.sample(), {"reset": True}

    def step(self, action):
        self._step_count += 1
        return (
            self.observation_space.sample(),
            float(self._step_count),
            False, False,
            {"step_count": self._step_count},
        )

    def double_it(self, x):
        return x * 2


class _BoomEnv(gym.Env):
    """Env whose constructor raises — exercises the startup-phase error path."""
    def __init__(self):
        raise ValueError("boom-on-construct")


class _StepBoomEnv(gym.Env):
    """Env whose step() raises — exercises the command-loop error path."""
    def __init__(self):
        self.observation_space = spaces.Box(-1, 1, (2,), dtype=np.float32)
        self.action_space = spaces.Box(-1, 1, (1,), dtype=np.float32)
    def reset(self, *, seed=None, options=None):
        return self.observation_space.sample(), {}
    def step(self, action):
        raise RuntimeError("boom-on-step")


# Register at module load. fork()-based multiprocessing inherits this.
gym.register("UnirosTestTiny-v0", entry_point=_TinyEnv)
gym.register("UnirosTestBoomCtor-v0", entry_point=_BoomEnv)
gym.register("UnirosTestBoomStep-v0", entry_point=_StepBoomEnv)


class TestAliasIdentity:
    """All historical names must resolve to the same class object."""

    def test_uniros_core_alias(self):
        assert uniros_gym is GymProxy

    def test_uniros_top_level_aliases(self):
        assert TopLevelGymProxy is GymProxy
        assert TopLevelUnirosGym is GymProxy

    def test_isinstance_via_any_alias(self):
        env = GymProxy.make("UnirosTestTiny-v0")
        try:
            assert isinstance(env, uniros_gym)
            assert isinstance(env, TopLevelGymProxy)
        finally:
            env.close()


# ---------------------------------------------------------------- end-to-end


class TestEndToEnd:
    """Step/reset/close round-trip across the multiprocessing pipe."""

    def test_make_returns_observation_action_spaces(self):
        env = GymProxy.make("UnirosTestTiny-v0")
        try:
            assert env.observation_space.shape == (3,)
            assert env.action_space.shape == (2,)
        finally:
            env.close()

    def test_reset_returns_obs_and_info(self):
        env = GymProxy.make("UnirosTestTiny-v0")
        try:
            obs, info = env.reset(seed=42)
            assert obs.shape == (3,)
            assert info == {"reset": True}
        finally:
            env.close()

    def test_step_round_trip(self):
        env = GymProxy.make("UnirosTestTiny-v0")
        try:
            env.reset(seed=0)
            obs, reward, terminated, truncated, info = env.step(
                np.zeros(2, dtype=np.float32)
            )
            assert obs.shape == (3,)
            assert reward == 1.0
            assert terminated is False
            assert truncated is False
            assert info["step_count"] == 1
        finally:
            env.close()

    def test_getattr_value(self):
        env = GymProxy.make("UnirosTestTiny-v0")
        try:
            # action_space is a value (already populated on parent at make() time)
            assert env.action_space.shape == (2,)
        finally:
            env.close()

    def test_getattr_callable_round_trip(self):
        """__getattr__ for a callable returns a method proxy that IPCs to worker."""
        env = GymProxy.make("UnirosTestTiny-v0")
        try:
            assert env.double_it(21) == 42
        finally:
            env.close()


class TestUnwrappedProperty:
    """env.unwrapped must return self (no IPC) for SB3 compatibility."""

    def test_unwrapped_is_self_not_ipc(self):
        env = GymProxy.make("UnirosTestTiny-v0")
        try:
            # If this routed through __getattr__ → IPC → worker, the
            # worker would try to pickle its gym.Env (which contains
            # non-picklable rospy.RLock state on real envs) and crash.
            # Locally the failure mode is just "returns the wrong object".
            assert env.unwrapped is env
        finally:
            env.close()


class TestIdempotentClose:
    """close() must be safe to call multiple times and from __del__."""

    def test_close_called_twice(self):
        env = GymProxy.make("UnirosTestTiny-v0")
        env.close()
        env.close()  # must not raise

    def test_close_then_del_ok(self):
        env = GymProxy.make("UnirosTestTiny-v0")
        env.close()
        del env  # __del__ calls close again; must not raise


class TestContextManager:
    """`with uniros.make(...) as env:` cleans up on both success and exception."""

    def test_with_block_closes_on_success(self):
        with GymProxy.make("UnirosTestTiny-v0") as env:
            assert env._closed is False
            env.reset()
        # After the with block, close() should have been called.
        assert env._closed is True

    def test_with_block_closes_on_exception(self):
        env_ref = []
        with pytest.raises(RuntimeError, match="boom"):
            with GymProxy.make("UnirosTestTiny-v0") as env:
                env_ref.append(env)
                raise RuntimeError("boom")
        # __exit__ ran close() on the way out; the exception still propagates.
        assert env_ref[0]._closed is True

    def test_with_block_propagates_exception(self):
        # __exit__ must return None (falsy) so exceptions aren't swallowed.
        sentinel = ValueError("propagate me")
        with pytest.raises(ValueError) as excinfo:
            with GymProxy.make("UnirosTestTiny-v0"):
                raise sentinel
        assert excinfo.value is sentinel


class TestWorkerErrorPropagation:
    """A worker raising must surface as a parent-side RuntimeError, not hang."""

    def test_worker_raises_during_make(self):
        # Startup-phase error must reach parent via _RemoteException
        # rather than the parent blocking on recv() forever.
        with pytest.raises(RuntimeError) as excinfo:
            GymProxy.make("UnirosTestBoomCtor-v0")
        assert "boom-on-construct" in str(excinfo.value)
        assert "ValueError" in str(excinfo.value)

    def test_worker_raises_during_step(self):
        # Command-loop error must reach parent.
        env = GymProxy.make("UnirosTestBoomStep-v0")
        try:
            env.reset()
            with pytest.raises(RuntimeError) as excinfo:
                env.step(np.zeros(1, dtype=np.float32))
            assert "boom-on-step" in str(excinfo.value)
            assert "RuntimeError" in str(excinfo.value)  # original exception type embedded
        finally:
            env.close()


# ---------------------------------------------------------------- carrier


class TestRemoteExceptionCarrier:
    """_RemoteException is the pickle-safe carrier for worker tracebacks."""

    def test_remote_exception_holds_type_and_traceback(self):
        try:
            raise ValueError("test value")
        except Exception as e:
            import traceback as _tb
            rex = _RemoteException(e, _tb.format_exc())

        assert rex.exc_type_name == "ValueError"
        assert "test value" in rex.exc_repr
        assert "test_remote_exception_holds_type_and_traceback" in rex.tb_string

    def test_remote_exception_reraise(self):
        try:
            raise KeyError("missing-key")
        except Exception as e:
            import traceback as _tb
            rex = _RemoteException(e, _tb.format_exc())

        with pytest.raises(RuntimeError) as excinfo:
            rex.reraise()
        assert "GymProxy worker process" in str(excinfo.value)
        assert "KeyError" in str(excinfo.value)
        assert "missing-key" in str(excinfo.value)
