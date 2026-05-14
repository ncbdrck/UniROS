#! /usr/bin/env python

"""
This script is to specify all the functions related to the handling of ROS Controllers.
It has the following functions,
    01. load_ros_controller: Load a ROS controller.
    02. load_controller_list: Load a list of ROS controllers.
    03. list_loaded_controllers: List all loaded ROS controllers.
    04. unload_ros_controller: Unload a ROS controller.
    05. unload_controller_list: Unload a list of ROS controllers.
    06. switch_controllers: Switch between two sets of ROS controllers.
    07. start_controllers: Start a list of ROS controllers.
    08. stop_controllers: Stop a list of ROS controllers.
    09. reset_controllers: "reset" a list of ROS controllers by stopping and then starting them again.
    10. spawn_controllers: Spawn a list of ROS controllers by loading and then starting them.
    11. unspawn_controllers: Unspawn a list of ROS controllers by stopping and then unloading them.

    ROS Doc:
    http://docs.ros.org/en/noetic/api/controller_manager_msgs/html/index-msg.html
"""

import rospy
from controller_manager_msgs.srv import *

"""
    01. load_ros_controller: To load a ROS controller.
"""


def load_ros_controller(controller_name: str, ns: str = None, max_retries: int = 5) -> bool:
    """
    Function to load a ROS controller using the controller_manager_msgs/LoadController service.
    (Need to have this controller loaded in the parameter server)

    Args:
        controller_name (str): The name of the controller to load.
        ns (str): The namespace of the controller_manager service (optional).
        max_retries (int): The maximum number of times to retry loading the controller (optional).

    Returns:
        bool: True if the controller was successfully loaded, False otherwise.
    """
    # Create a service proxy for the LoadController service
    if ns is not None:
        # Remove any trailing slashes from ns
        ns = ns.rstrip('/')
        load_controller_service = f'{ns}/controller_manager/load_controller'
    else:
        load_controller_service = '/controller_manager/load_controller'

    # wait for service to be available
    try:
        rospy.wait_for_service(load_controller_service, timeout=30.0)
    except rospy.ROSException as e:
        rospy.logerr(f"Timeout (30s) waiting for service '{load_controller_service}': {e}")
        return False

    # create proxy to the service
    load_controller = rospy.ServiceProxy(load_controller_service, LoadController)

    # Attempt to load the controller
    for i in range(max_retries):
        try:
            response = load_controller(name=controller_name)
            if response.ok:
                return True
        except rospy.ServiceException as e:
            rospy.logerr(f'Try {i}: Failed to call service {load_controller_service}: {e}')

    # Failed to load the controller after max_retries attempts
    return False


"""
    02. load_controller_list: To load a list of ROS controllers.
"""


def load_controller_list(controller_list: list, ns: str = None, max_retries: int = 5) -> bool:
    """
    Function to load a list of ROS controllers.

    Args:
        controller_list (list): A list of controller names to load.
        ns (str): The namespace of the controller_manager service (optional).
        max_retries (int): The maximum number of times to retry loading each controller (optional).

    Returns:
        bool: True if all controllers were successfully loaded, False otherwise.
    """
    # Attempt to load each controller in the list
    for controller_name in controller_list:
        if not load_ros_controller(controller_name, ns, max_retries):
            return False

    # All controllers were successfully loaded
    return True


"""
    03. list_loaded_controllers: To list all loaded ROS controllers.
"""


def list_loaded_controllers(ns: str = None, max_retries: int = 5) -> list:
    """
    Function to list all loaded ROS controllers using the controller_manager_msgs/ListControllers service.

    Args:
        ns (str): The namespace of the controller_manager service (optional).
        max_retries (int): The maximum number of times to retry calling the service (optional).

    Returns:
        list: A list of loaded controller names. If an error occurred while calling the service,
              an empty list is returned.
    """
    # Create a service proxy for the ListControllers service
    if ns is not None:
        # Remove any trailing slashes from ns
        ns = ns.rstrip('/')
        list_controllers_service = f'{ns}/controller_manager/list_controllers'
    else:
        list_controllers_service = '/controller_manager/list_controllers'

    # wait for service to be available
    try:
        rospy.wait_for_service(list_controllers_service, timeout=30.0)
    except rospy.ROSException as e:
        rospy.logerr(f"Timeout (30s) waiting for service '{list_controllers_service}': {e}")
        return []

    # create proxy to the service
    list_controllers = rospy.ServiceProxy(list_controllers_service, ListControllers)

    # Attempt to call the ListControllers service
    for i in range(max_retries):
        try:
            response = list_controllers()
            return [controller.name for controller in response.controller]

        except rospy.ServiceException as e:
            rospy.logerr(f'Try {i}: Failed to call service {list_controllers_service}: {e}')

    # Failed to call the ListControllers service after max_retries attempts
    return []


"""
    04. unload_ros_controller: To unload a ROS controller.
"""


def unload_ros_controller(controller_name: str, ns: str = None, max_retries: int = 5) -> bool:
    """
    Function to unload a ROS controller using the controller_manager_msgs/UnloadController service.

    Args:
        controller_name (str): The name of the controller to unload.
        ns (str): The namespace of the controller_manager service (optional).
        max_retries (int): The maximum number of times to retry unloading the controller (optional).

    Returns:
        bool: True if the controller was successfully unloaded, False otherwise.
    """

    # Create a service proxy for the UnloadController service
    if ns is not None:
        # Remove any trailing slashes from ns
        ns = ns.rstrip('/')
        unload_controller_service = f'{ns}/controller_manager/unload_controller'
    else:
        unload_controller_service = '/controller_manager/unload_controller'

    # wait for service to be available
    try:
        rospy.wait_for_service(unload_controller_service, timeout=30.0)
    except rospy.ROSException as e:
        rospy.logerr(f"Timeout (30s) waiting for service '{unload_controller_service}': {e}")
        return False

    # create proxy to the service
    unload_controller = rospy.ServiceProxy(unload_controller_service, UnloadController)

    # Attempt to unload the controller
    for i in range(max_retries):
        try:
            response = unload_controller(name=controller_name)
            if response.ok:
                return True
        except rospy.ServiceException as e:
            rospy.logerr(f'Try {i}: Failed to call service {unload_controller_service}: {e}')

    # Failed to unload the controller after max_retries attempts
    return False


"""
    05. unload_controller_list: To unload a list of ROS controllers.
"""


def unload_controller_list(controller_list: list, ns: str = None, max_retries: int = 5) -> bool:
    """
    Function to unload a list of ROS controllers using the unload_ros_controller function.

    Args:
        controller_list (list): A list of controller names to unload.
        ns (str): The namespace of the controller_manager service (optional).
        max_retries (int): The maximum number of times to retry unloading each controller (optional).

    Returns:
        bool: True if all controllers were successfully unloaded, False otherwise.
    """
    # Attempt to unload each controller in the list
    for controller_name in controller_list:
        if not unload_ros_controller(controller_name, ns, max_retries):
            return False

    # All controllers were successfully unloaded
    return True


"""
    06. switch_controllers: To switch between two sets of ROS controllers.
"""


def switch_controllers(start_controllers_list: list, stop_controllers_list: list, ns: str = None,
                       strictness: int = 1, start_asap: bool = False, timeout: float = 0.0,
                       max_retries: int = 5) -> bool:
    """
    Function to switch between two sets of ROS controllers using the controller_manager_msgs/SwitchController service.

    Args:
        start_controllers_list (list): A list of controller names to start.
        stop_controllers_list (list): A list of controller names to stop.
        ns (str): The namespace of the controller_manager service (optional).
        strictness (int): The level of strictness to use when switching controllers (optional).
                          1 = BEST_EFFORT, 2 = STRICT.
        start_asap (bool): Whether to start controllers in the start_controllers list as soon as possible (optional).
        timeout (float): The maximum amount of time to wait for the controller switch to complete (optional).
        max_retries (int): The maximum number of times to retry switching controllers (optional).

    Returns:
        bool: True if the controllers were successfully switched, False otherwise.
    """
    # Create a service proxy for the SwitchController service
    if ns is not None:
        # Remove any trailing slashes from ns
        ns = ns.rstrip('/')
        switch_controller_service = f'{ns}/controller_manager/switch_controller'
    else:
        switch_controller_service = '/controller_manager/switch_controller'

    try:
        rospy.wait_for_service(switch_controller_service, timeout=30.0)
    except rospy.ROSException as e:
        rospy.logerr(f"Timeout (30s) waiting for service '{switch_controller_service}': {e}")
        return False
    switch_controller = rospy.ServiceProxy(switch_controller_service, SwitchController)

    # Attempt to switch controllers
    for i in range(max_retries):
        try:
            response = switch_controller(start_controllers=start_controllers_list,
                                         stop_controllers=stop_controllers_list,
                                         strictness=strictness,
                                         start_asap=start_asap,
                                         timeout=timeout)
            if response.ok:
                return True
        except rospy.ServiceException as e:
            rospy.logerr(f'ry {i}: Failed to call service {switch_controller_service}: {e}')

    # Failed to switch controllers after max_retries attempts
    return False


"""
    07. start_controllers: To start a list of ROS controllers.
"""


def start_controllers(controller_list: list, ns: str = None,
                      strictness: int = 1, start_asap: bool = False, timeout: float = 0.0,
                      max_retries: int = 5) -> bool:
    """
    Function to start a list of ROS controllers using the switch_controllers function.

    Args:
        controller_list (list): A list of controller names to start.
        ns (str): The namespace of the controller_manager service (optional).
        strictness (int): The level of strictness to use when starting controllers (optional).
                          1 = BEST_EFFORT, 2 = STRICT.
        start_asap (bool): Whether to start controllers in the controller_list as soon as possible (optional).
        timeout (float): The maximum amount of time to wait for the controllers to start (optional).
        max_retries (int): The maximum number of times to retry starting controllers (optional).

    Returns:
        bool: True if all controllers were successfully started, False otherwise.
    """
    return switch_controllers(controller_list, [], ns, strictness, start_asap, timeout, max_retries)


"""
    08. stop_controllers: To stop a list of ROS controllers.
"""


def stop_controllers(controller_list: list, ns: str = None,
                     strictness: int = 1, start_asap: bool = False, timeout: float = 0.0,
                     max_retries: int = 5) -> bool:
    """
    Function to stop a list of ROS controllers using the switch_controllers function.

    Args:
        controller_list (list): A list of controller names to stop.
        ns (str): The namespace of the controller_manager service (optional).
        strictness (int): The level of strictness to use when stopping controllers (optional).
                          1 = BEST_EFFORT, 2 = STRICT.
        start_asap (bool): Whether to stop controllers in the controller_list as soon as possible (optional).
        timeout (float): The maximum amount of time to wait for the controllers to stop (optional).
        max_retries (int): The maximum number of times to retry stopping controllers (optional).

    Returns:
        bool: True if all controllers were successfully stopped, False otherwise.
    """
    return switch_controllers([], controller_list, ns, strictness, start_asap, timeout, max_retries)


"""
    09. reset_controllers: To "reset" a list of ROS controllers by stopping and then starting them again.
"""


def reset_controllers(controller_list: list, ns: str = None,
                      strictness: int = 1, start_asap: bool = False, timeout: float = 0.0,
                      max_retries: int = 5) -> bool:
    """
    Function to "reset" a list of ROS controllers by stopping and then starting them again.

    Args:
        controller_list (list): A list of controller names to reset.
        ns (str): The namespace of the controller_manager service (optional).
        strictness (int): The level of strictness to use when resetting controllers (optional).
                          1 = BEST_EFFORT, 2 = STRICT.
        start_asap (bool): Whether to start controllers in the controller_list as soon as possible (optional).
        timeout (float): The maximum amount of time to wait for the controllers to reset (optional).
        max_retries (int): The maximum number of times to retry resetting controllers (optional).

    Returns:
        bool: True if all controllers were successfully reset, False otherwise.
    """
    # Stop the controllers
    if not stop_controllers(controller_list, ns, strictness, start_asap, timeout, max_retries):
        return False

    # Start the controllers
    if not start_controllers(controller_list, ns, strictness, start_asap, timeout, max_retries):
        return False

    # All controllers were successfully reset
    return True


"""
    10. spawn_controllers: To spawn a list of ROS controllers by loading and then starting them.
"""


def spawn_controllers(controller_list: list, ns: str = None,
                      strictness: int = 1, start_asap: bool = False, timeout: float = 0.0,
                      max_retries: int = 5) -> bool:
    """
    Function to spawn a list of ROS controllers by loading and then starting them.

    Args:
        controller_list (list): A list of controller names to spawn.
        ns (str): The namespace of the controller_manager service (optional).
        strictness (int): The level of strictness to use when spawning controllers (optional).
                          1 = BEST_EFFORT, 2 = STRICT.
        start_asap (bool): Whether to start controllers in the controller_list as soon as possible (optional).
        timeout (float): The maximum amount of time to wait for the controllers to spawn (optional).
        max_retries (int): The maximum number of times to retry spawning controllers (optional).

    Returns:
        bool: True if all controllers were successfully spawned, False otherwise.
    """
    # Load the controllers
    if not load_controller_list(controller_list, ns, max_retries):
        return False

    # Start the controllers
    if not start_controllers(controller_list, ns, strictness, start_asap, timeout, max_retries):
        return False

    # All controllers were successfully spawned
    return True


"""
    11. unspawn_controllers: To unspawn a list of ROS controllers by stopping and then unloading them.
"""


def unspawn_controllers(controller_list: list, ns: str = None,
                        strictness: int = 1, start_asap: bool = False, timeout: float = 0.0,
                        max_retries: int = 5) -> bool:
    """
    Function to unspawn a list of ROS controllers by stopping and then unloading them.

    Args:
        controller_list (list): A list of controller names to unspawn.
        ns (str): The namespace of the controller_manager service (optional).
        strictness (int): The level of strictness to use when unspawning controllers (optional).
                          1 = BEST_EFFORT, 2 = STRICT.
        start_asap (bool): Whether to stop controllers in the controller_list as soon as possible (optional).
        timeout (float): The maximum amount of time to wait for the controllers to unspawn (optional).
        max_retries (int): The maximum number of times to retry unspawning controllers (optional).

    Returns:
        bool: True if all controllers were successfully unspawned, False otherwise.
    """
    # Stop the controllers
    if not stop_controllers(controller_list, ns, strictness, start_asap, timeout, max_retries):
        return False

    # Unload the controllers
    if not unload_controller_list(controller_list, ns, max_retries):
        return False

    # All controllers were successfully unspawned
    return True
