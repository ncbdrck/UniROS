#!/bin/python3

import gym
from multiprocessing import Process, Pipe

"""
    This is the main class for the UniROS package. 
    It is a wrapper around the OpenAI Gym environment class.
    It allows the user to create an instance of the environment in a separate process.
    This is useful when the environment is a ROS node that needs to be run in a separate process.
    The class has the same methods and attributes as the OpenAI Gym environment class.
    The methods and attributes are forwarded to the environment in the worker process.

    Usage:
        from uniros.core import uniros_gym as gym
        env = gym.make("env_name", args)
        env.reset()
"""


class uniros_gym:
    def __init__(self, env_name, *args, **kwargs):
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
        # Create the environment using the gym.make function and pass it any additional arguments
        env = gym.make(env_name, *args, **kwargs)
        # Send the observation and action spaces to the main process
        conn.send((env.observation_space, env.action_space))
        # Continuously receive commands from the main process and perform the corresponding actions on the environment
        while True:
            cmd, data = conn.recv()
            if cmd == 'step':
                conn.send(env.step(data))

            elif cmd == 'reset':
                conn.send(env.reset())

            elif cmd == 'close':
                env.close()
                break

            elif cmd == 'get_attribute':
                # If the command is 'get_attribute', get the value of the specified attribute from the environment
                try:
                    attr = getattr(env, data)

                    # If the attribute is callable (i.e., a method),
                    # send a special string 'callable' to the main process
                    if callable(attr):
                        conn.send('callable')

                    # Otherwise, send the value of the attribute to the main process
                    else:
                        conn.send(attr)

                # If the attribute does not exist in the environment, send an AttributeError to the main process
                except AttributeError:
                    conn.send(AttributeError(f"{data} not found"))

            elif cmd == 'call_method':
                # If the command is 'call_method', get the name of the method and its arguments from the data
                method_name, args, kwargs = data

                # Call the specified method on the environment with the provided arguments and keyword arguments
                result = getattr(env, method_name)(*args, **kwargs)

                # Send the result of calling the method back to the main process
                conn.send(result)

    @classmethod
    def make(cls, env_name, *args, **kwargs):
        # Create an instance of the uniros_gym class and pass it the environment name and any additional arguments
        env = cls(env_name, *args, **kwargs)
        # Receive the observation and action spaces from the worker process and set them on the instance
        env.observation_space, env.action_space = env.parent_conn.recv()
        # Return the instance of the uniros_gym class
        return env

    def step(self, action):
        # Send a 'step' command to the worker process along with the action to take
        self.parent_conn.send(('step', action))
        # Receive and return the result of taking a step in the environment
        return self.parent_conn.recv()

    def reset(self):
        # Send a 'reset' command to the worker process
        self.parent_conn.send(('reset', None))
        # Receive and return the initial observation of the environment after resetting it
        return self.parent_conn.recv()

    def close(self):
        # Send a 'close' command to the worker process to close the environment
        self.parent_conn.send(('close', None))
        # Wait for the worker process to terminate before returning
        self.process.join()

    def __getattr__(self, name):
        # Send a 'get_attribute' command to the worker process along with the name of the attribute
        self.parent_conn.send(('get_attribute', name))

        # Receive the value of the attribute from the worker process
        attr = self.parent_conn.recv()

        # If the received value is a string, and it is equal to 'callable'
        if isinstance(attr, str) and attr == 'callable':

            # Define a new method that sends a 'call_method' command to the worker process
            # along with the name of the method and its arguments
            def method(*args, **kwargs):
                self.parent_conn.send(('call_method', (name, args, kwargs)))

                # Receive and return the result of calling the method in the worker process
                return self.parent_conn.recv()

            # Return the newly defined method
            return method

        # If the received value is an Exception, raise it
        elif isinstance(attr, Exception):
            raise attr

        # Otherwise, return the received value as is
        else:
            return attr

    def __del__(self):
        # Send a 'close' command to the worker process to close the environment
        self.parent_conn.send(('close', None))
        # Wait for the worker process to terminate before returning
        self.process.join()
