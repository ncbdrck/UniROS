#!/bin/python3
"""
Canonical gym-proxy implementation for the UniROS ecosystem.

This is the single source of truth for the multiprocessing
gym-proxy class used by multiros, realros, and uniros. Each of
those packages re-exports it under a historical name
(``MultirosGym``, ``RealrosGym``, ``uniros_gym``) so existing user
code continues to work — every alias points at the class defined
here, so a fix landed here automatically reaches all three
packages.

The proxy spawns a worker process that holds the actual ``gym.Env``.
Parent-side method calls (``step`` / ``reset`` / ``close`` /
attribute access) flow over a ``multiprocessing.Pipe`` to the worker
and back. Worker-side exceptions are caught and shipped back as
:class:`_RemoteException`, so the parent re-raises with the
worker's traceback instead of hanging on the next ``recv()``.
"""

import traceback
import gymnasium as gym
from multiprocessing import Process, Pipe


class _RemoteException:
    """
    Pickle-safe carrier for a worker-side exception + traceback.

    The worker process catches every uncaught exception and ships an
    instance of this class back through the pipe; the parent's _recv()
    detects it and re-raises a RuntimeError with the worker-side
    traceback embedded. Without this carrier a worker-side raise would
    kill the worker silently and the parent's next recv() would block
    forever.

    We deliberately keep only string state (not the original exception
    object) because some user-defined exception classes don't pickle
    cleanly across process boundaries.
    """
    __slots__ = ('exc_type_name', 'exc_repr', 'tb_string')

    def __init__(self, exc, tb_string):
        self.exc_type_name = type(exc).__name__
        self.exc_repr = repr(exc)
        self.tb_string = tb_string

    def reraise(self):
        raise RuntimeError(
            f"Exception in GymProxy worker process "
            f"({self.exc_type_name}: {self.exc_repr}):\n{self.tb_string}"
        )


class GymProxy:
    """
    Parent-side proxy for a ``gym.Env`` running inside a worker process.

    Equivalent aliases re-exported by other packages in the ecosystem:

    - ``multiros.core.MultirosGym``
    - ``realros.core.RealrosGym``
    - ``uniros.core.uniros_gym``

    All four names refer to the same class object.

    Usage::

        from uniros.core import uniros_gym as gym  # or any alias
        env = gym.make("env_name", **kwargs)
        env.reset()
    """

    def __init__(self, env_name, *args, **kwargs):
        # Set _closed first so close() / __del__ can be idempotent even if
        # the rest of __init__ raises before completing.
        self._closed = False
        # Create a pipe for communication between the main process and the worker process
        self.parent_conn, self.child_conn = Pipe()
        # Start the worker process and pass it the environment name, the child connection, and any additional arguments
        self.process = Process(target=self.worker, args=(env_name, self.child_conn, *args), kwargs=kwargs)
        self.process.start()
        # Initialize the observation and action spaces to None
        self.observation_space = None
        self.action_space = None

    @staticmethod
    def worker(env_name, conn, *args, **kwargs):
        # --- Startup phase --------------------------------------------------
        # If gym.make() raises, the parent is blocked on recv() in make().
        # Send a _RemoteException so the parent can re-raise it and close,
        # rather than hanging forever.
        try:
            env = gym.make(env_name, *args, **kwargs)
            conn.send((env.observation_space, env.action_space))
        except Exception as e:
            try:
                conn.send(_RemoteException(e, traceback.format_exc()))
            except (BrokenPipeError, OSError):
                pass
            try:
                conn.close()
            except Exception:
                pass
            return

        # --- Command loop ---------------------------------------------------
        # Every command is wrapped: any user-side raise (bad action, NaN
        # observation, controller_manager timeout, MoveIt crash, etc.)
        # surfaces to the parent as a _RemoteException instead of killing
        # the worker silently.
        while True:
            try:
                cmd, data = conn.recv()
            except (EOFError, BrokenPipeError, ConnectionResetError):
                # Parent has gone away; exit cleanly.
                return

            try:
                if cmd == 'step':
                    result = env.step(data)
                elif cmd == 'reset':
                    seed, options = data
                    result = env.reset(seed=seed, options=options)
                elif cmd == 'close':
                    env.close()
                    try:
                        conn.close()
                    except Exception:
                        pass
                    return
                elif cmd == 'get_attribute':
                    # AttributeError is a normal API response here ("attr
                    # not found"); pass it through as a value so the
                    # parent's __getattr__ can re-raise it client-side.
                    # Any OTHER exception still flows through the outer
                    # except and becomes a _RemoteException.
                    try:
                        attr = getattr(env, data)
                    except AttributeError:
                        result = AttributeError(f"{data} not found")
                    else:
                        result = 'callable' if callable(attr) else attr
                elif cmd == 'call_method':
                    method_name, m_args, m_kwargs = data
                    result = getattr(env, method_name)(*m_args, **m_kwargs)
                else:
                    raise ValueError(f"Unknown command from parent: {cmd!r}")
                conn.send(result)
            except Exception as e:
                try:
                    conn.send(_RemoteException(e, traceback.format_exc()))
                except (BrokenPipeError, OSError):
                    return

    @property
    def unwrapped(self):
        """
        Return self as the unwrapped env.

        The proxy IS the user-visible env from the parent's perspective;
        whatever lives in the worker process is opaque and not accessible
        across the pipe (gym.Env instances typically hold non-picklable
        state such as _thread.RLock from rospy's spinner threads, so
        sending them through the pipe raises TypeError).

        Without this handler, env.unwrapped would route through
        __getattr__, IPC to the worker, and fail to pickle. SB3's
        DummyVecEnv calls `id(env.unwrapped)` for uniqueness checking
        during construction, so this property is required for SB3
        compatibility.
        """
        return self

    def _recv(self):
        """
        Receive a message from the worker, re-raising any remote exception.

        Every parent-side recv() goes through this so a worker-side raise
        becomes a parent-side RuntimeError (with the worker traceback)
        rather than a silent hang on the next recv().
        """
        msg = self.parent_conn.recv()
        if isinstance(msg, _RemoteException):
            # If the worker died, also tear down our side cleanly so the
            # caller doesn't have to remember to call close() after the
            # exception.
            self._closed = True
            self.process.join(timeout=2.0)
            if self.process.is_alive():
                self.process.terminate()
            msg.reraise()
        return msg

    @classmethod
    def make(cls, env_name, *args, **kwargs):
        # Create an instance of the proxy class and pass it the environment name and any additional arguments
        env = cls(env_name, *args, **kwargs)
        # Receive the observation and action spaces from the worker process and set them on the instance.
        # If the worker raised during gym.make(), _recv() re-raises here.
        env.observation_space, env.action_space = env._recv()
        # Return the instance of the proxy class
        return env

    def step(self, action):
        # Send a 'step' command to the worker process along with the action to take
        self.parent_conn.send(('step', action))
        # Receive and return the result of taking a step in the environment
        return self._recv()

    def reset(self, seed=None, options=None):
        # Send a 'reset' command to the worker process
        self.parent_conn.send(('reset', (seed, options)))
        # Receive and return the initial observation of the environment after resetting it
        return self._recv()

    def close(self):
        # Idempotent close: safe to call multiple times and from __del__.
        if self._closed:
            return
        self._closed = True
        try:
            self.parent_conn.send(('close', None))
        except (BrokenPipeError, OSError, EOFError):
            # Worker already exited or pipe already torn down.
            pass
        # Bounded join so a hung worker can't lock the parent indefinitely.
        self.process.join(timeout=5.0)
        if self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=1.0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Always close, even on exception. close() is idempotent so a later
        # __del__ won't double-tear-down the worker. Propagate the exception
        # by returning None (truthy return would swallow it).
        self.close()

    def __getattr__(self, name):
        # Send a 'get_attribute' command to the worker process along with the name of the attribute
        self.parent_conn.send(('get_attribute', name))

        # Receive the value of the attribute from the worker process.
        # _recv() unwraps any _RemoteException; a normal AttributeError
        # (attr not found) still flows through as a value and is re-raised
        # below for backwards compatibility.
        attr = self._recv()

        # If the received value is a string, and it is equal to 'callable'
        if isinstance(attr, str) and attr == 'callable':

            # Define a new method that sends a 'call_method' command to the worker process
            # along with the name of the method and its arguments
            def method(*args, **kwargs):
                self.parent_conn.send(('call_method', (name, args, kwargs)))

                # Receive and return the result of calling the method in the worker process
                return self._recv()

            # Return the newly defined method
            return method

        # If the received value is an Exception (e.g. AttributeError for
        # "attr not found"), raise it client-side.
        elif isinstance(attr, Exception):
            raise attr

        # Otherwise, return the received value as is
        else:
            return attr

    def __del__(self):
        # Destructors must never raise. Swallow everything; close() already
        # absorbs the common cases (pipe closed, process gone) on its own.
        try:
            self.close()
        except Exception:
            pass
