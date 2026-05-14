#! /usr/bin/env python

"""
This script is to specify Classes for handling ROS markers.

The RosMarker Class has the following methods,
    01. set_frame_id: Set the frame ID of the marker.
    02. set_ns: Set the namespace of the marker.
    03. set_id: Set the ID of the marker.
    04. set_type: Set the type of the marker.
    05. set_action: Set the action of the marker.
    06. set_pose: Set the pose of the marker.
    07. set_position: Set the position of the marker.
    08. set_orientation: Set the orientation of the marker.
    09. set_duration: Set the lifetime of the marker.
    10. set_scale: Set the scale of the marker.
    11. set_color: Set the color of the marker.
    12. publish: Publish the marker.
    13. delete: Delete the marker.
    14. update: Update the marker.

The RosMarkerArray Class has the following methods,
    01. add_marker: Add a new marker to the array.
    02. remove_marker: Remove a marker from the array.
    03. update_markers: Update all markers in the array.
    04. publish: Publish all markers in the array.
    05. delete_all_markers: Delete all markers in the array.
    06. remove_all_markers: Remove all markers from the array.
    07. get_marker_by_id: Get a marker by its ID.
    08. get_markers_by_property: Get all markers with a specific property value.
"""
import rospy
from visualization_msgs.msg import Marker, MarkerArray
import numpy as np
from typing import Union


class RosMarker:
    """
        A class for working with ROS markers.

        This class provides methods for creating, updating, publishing and deleting a single ROS marker.
        It allows you to set and change the marker properties such as position, orientation, scale, color and lifetime.

    """

    def __init__(self, frame_id: str, ns: str, marker_type: int, marker_topic: str, marker_id: int = 0,
                 action: int = Marker.ADD, pose: list = None, position: Union[list, np.ndarray] = None,
                 orientation: Union[list, np.ndarray] = None, lifetime: float = 0.0,
                 scale: list = None, color: list = None):
        """
        Initialize a RosMarker object.

        Args:
            frame_id (str): The frame ID of the marker.
            ns (str): The namespace of the marker.
            marker_type (int): The type of the marker.
            marker_topic (str): The topic to publish the marker to.
            marker_id (int): The ID of the marker (optional).
            action (int): The action of the marker (optional).
            pose (list): The pose of the marker [x, y, z, qx, qy, qz, qw] (optional).
            position (Union[list, np.ndarray]): The new position of the marker [x, y, z] (optional).
            orientation (Union[list, np.ndarray]): The new orientation of the marker [qx, qy, qz, qw] (optional).
            lifetime (float): The lifetime of the marker in seconds (optional).
            scale (list): The scale of the marker [x, y, z] (optional).
            color (list): The color of the marker [r, g, b, a] (optional).

        Marker types:
          ARROW = 0
          CUBE = 1
          SPHERE = 2
          CYLINDER = 3
          LINE_STRIP = 4
          LINE_LIST = 5
          CUBE_LIST = 6
          SPHERE_LIST = 7
          POINTS = 8
          TEXT_VIEW_FACING = 9
          MESH_RESOURCE = 10
          TRIANGLE_LIST = 11
        """

        # Initialize the marker
        self.marker = Marker()
        self.marker.header.frame_id = frame_id
        self.marker.ns = ns
        self.marker.id = marker_id
        self.marker.type = marker_type
        self.marker.action = action

        if pose is not None:
            self.marker.pose.position.x = pose[0]
            self.marker.pose.position.y = pose[1]
            self.marker.pose.position.z = pose[2]
            self.marker.pose.orientation.x = pose[3]
            self.marker.pose.orientation.y = pose[4]
            self.marker.pose.orientation.z = pose[5]
            self.marker.pose.orientation.w = pose[6]

        if position is not None:

            # Convert position to list if it is a numpy array
            if isinstance(position, np.ndarray):
                position = position.tolist()

            self.marker.pose.position.x = position[0]
            self.marker.pose.position.y = position[1]
            self.marker.pose.position.z = position[2]

        if orientation is not None:

            # Convert position to list if it is a numpy array
            if isinstance(orientation, np.ndarray):
                orientation = orientation.tolist()

            self.marker.pose.orientation.x = orientation[0]
            self.marker.pose.orientation.y = orientation[1]
            self.marker.pose.orientation.z = orientation[2]
            self.marker.pose.orientation.w = orientation[3]

        if lifetime > 0:
            self.marker.lifetime = rospy.Duration(lifetime)

        if scale is not None:
            self.marker.scale.x = scale[0]
            self.marker.scale.y = scale[1]
            self.marker.scale.z = scale[2]
        else:
            self.marker.scale.x = 0.1
            self.marker.scale.y = 0.1
            self.marker.scale.z = 0.1

        if color is not None:
            self.marker.color.r = color[0]
            self.marker.color.g = color[1]
            self.marker.color.b = color[2]
            self.marker.color.a = color[3]
        else:
            self.marker.color.r = 1.0
            self.marker.color.g = 0.0
            self.marker.color.b = 0.0
            self.marker.color.a = 1.0

        # Create a publisher for the marker
        self.publisher = rospy.Publisher(marker_topic, Marker, queue_size=10)

    def set_frame_id(self, frame_id: str):
        """
        Set the frame ID of the marker.

        Args:
            frame_id (str): The new frame ID of the marker.
        """

        # Set the frame ID of the marker
        self.marker.header.frame_id = frame_id

    def set_ns(self, ns: str):
        """
        Set the namespace of the marker.

        Args:
            ns (str): The new namespace of the marker.
        """

        # Set the namespace of the marker
        self.marker.ns = ns

    def set_id(self, marker_id: int):
        """
        Set the ID of the marker.

        Args:
            marker_id (int): The new ID of the marker.
        """

        # Set the ID of the marker
        self.marker.id = marker_id

    def set_type(self, marker_type: int):
        """
        Set the type of the marker.

        Args:
            marker_type (int): The new type of the marker.
        """

        # Set the type of the marker
        self.marker.type = marker_type

    def set_action(self, action: int):
        """
        Set the action of the marker.

        Args:
            action (int): The new action of the marker.
        """

        # Set the action of the marker
        self.marker.action = action

    def set_pose(self, pose: list):
        """
        Set the pose of the marker.

        Args:
            pose (list): The new pose of the marker [x, y, z, qx, qy, qz, qw].
        """

        # Set the pose of the marker
        self.marker.pose.position.x = pose[0]
        self.marker.pose.position.y = pose[1]
        self.marker.pose.position.z = pose[2]
        self.marker.pose.orientation.x = pose[3]
        self.marker.pose.orientation.y = pose[4]
        self.marker.pose.orientation.z = pose[5]
        self.marker.pose.orientation.w = pose[6]

    def set_position(self, position: Union[list, np.ndarray]):
        """
        Set the position of the marker.

        Args:
            position (Union[list, np.ndarray]): The new position of the marker [x, y, z].
        """

        # Convert position to list if it is a numpy array
        if isinstance(position, np.ndarray):
            position = position.tolist()

        # Set the position of the marker
        self.marker.pose.position.x = position[0]
        self.marker.pose.position.y = position[1]
        self.marker.pose.position.z = position[2]

    def set_orientation(self, orientation: Union[list, np.ndarray]):
        """
        Set the orientation of the marker.

        Args:
            orientation (Union[list, np.ndarray]): The new orientation of the marker [qx, qy, qz, qw].
        """

        # Convert position to list if it is a numpy array
        if isinstance(orientation, np.ndarray):
            orientation = orientation.tolist()

        # Set the orientation of the marker
        self.marker.pose.orientation.x = orientation[0]
        self.marker.pose.orientation.y = orientation[1]
        self.marker.pose.orientation.z = orientation[2]
        self.marker.pose.orientation.w = orientation[3]

    def set_duration(self, duration: float):
        """
        Set the lifetime of the marker.

        Args:
            duration (float): The new lifetime of the marker in seconds.
        """

        # Set the lifetime of the marker
        self.marker.lifetime = rospy.Duration(duration)

    def set_scale(self, scale: list):
        """
        Set the scale of the marker.

        Args:
            scale (list): The new scale of the marker [x, y, z].
        """

        # Set the scale of the marker
        self.marker.scale.x = scale[0]
        self.marker.scale.y = scale[1]
        self.marker.scale.z = scale[2]

    def set_color(self, color: list = None, r: float = None, g: float = None, b: float = None, a: float = None):
        """
        Set the color of the marker.

        Args:
            color (list): The new color of the marker [r, g, b, a] (optional).
            r (float): The new red component of the marker color (optional).
            g (float): The new green component of the marker color (optional).
            b (float): The new blue component of the marker color (optional).
            a (float): The new alpha component of the marker color (optional).
        """

        if color is not None:
            # Set the color of the marker
            self.marker.color.r = color[0]
            self.marker.color.g = color[1]
            self.marker.color.b = color[2]
            self.marker.color.a = color[3]

        # Update the color of the marker if provided
        if r is not None:
            self.marker.color.r = r
        if g is not None:
            self.marker.color.g = g
        if b is not None:
            self.marker.color.b = b
        if a is not None:
            self.marker.color.a = a

    def publish(self):
        """
        Publish the marker.
        """

        # Update the timestamp of the marker
        self.marker.header.stamp = rospy.Time.now()

        # Publish the marker
        self.publisher.publish(self.marker)

    def delete(self):
        """
        Delete the marker.
        """

        # Set the action of the marker to DELETE
        self.marker.action = Marker.DELETE

        # Publish the updated marker
        self.publish()

    def update(self, position: Union[list, np.ndarray] = None, orientation: Union[list, np.ndarray] = None,
               r: float = None, g: float = None, b: float = None, a: float = None, duration: float = None):
        """
        Update the marker.

        Args:
            position (Union[list, np.ndarray]): The new position of the marker [x, y, z] (optional).
            orientation (Union[list, np.ndarray]): The new orientation of the marker [qx, qy, qz, qw] (optional).
            r (float): The new red component of the marker color (optional).
            g (float): The new green component of the marker color (optional).
            b (float): The new blue component of the marker color (optional).
            a (float): The new alpha component of the marker color (optional).
            duration (float): The new lifetime of the marker in seconds (optional).
        """

        # Update the position of the marker if provided
        if position is not None:

            # Convert position to list if it is a numpy array
            if isinstance(position, np.ndarray):
                position = position.tolist()

            self.marker.pose.position.x = position[0]
            self.marker.pose.position.y = position[1]
            self.marker.pose.position.z = position[2]

        # Update the orientation of the marker if provided
        if orientation is not None:

            # Convert position to list if it is a numpy array
            if isinstance(orientation, np.ndarray):
                orientation = orientation.tolist()

            self.marker.pose.orientation.x = orientation[0]
            self.marker.pose.orientation.y = orientation[1]
            self.marker.pose.orientation.z = orientation[2]
            self.marker.pose.orientation.w = orientation[3]

        # Update the color of the marker if provided
        if r is not None:
            self.marker.color.r = r
        if g is not None:
            self.marker.color.g = g
        if b is not None:
            self.marker.color.b = b
        if a is not None:
            self.marker.color.a = a

        # Update the lifetime of the marker if provided
        if duration is not None:
            self.marker.lifetime = rospy.Duration(duration)

        # Publish the updated marker
        self.publish()


class RosMarkerArray:
    """
        A class for working with arrays of ROS markers.

        This class provides methods for managing a list of RosMarker instances and publishing them as a MarkerArray.
        It allows you to add, remove, update and delete multiple markers at once.

    """

    def __init__(self, marker_topic: str):
        """
        Initialize the RosMarkerArray.

        Args:
            marker_topic (str): The topic to publish the markers on.
        """

        # Initialize the list of markers
        self.markers = []

        # Create a publisher for the markers
        self.publisher = rospy.Publisher(marker_topic, MarkerArray, queue_size=10)

    def add_marker(self, frame_id: str, ns: str, marker_type: int, marker_topic: str = "", marker_id: int = 0,
                   action: int = Marker.ADD, pose: list = None, position: Union[list, np.ndarray] = None,
                   orientation: Union[list, np.ndarray] = None, lifetime: float = 0.0,
                   scale: list = None, color: list = None):
        """
        Add a new marker to the array.

        Args:
            frame_id (str): The frame ID of the marker.
            ns (str): The namespace of the marker.
            marker_type (int): The type of the marker.
            marker_topic (str): The topic to publish the marker to (optional).
            marker_id (int): The ID of the marker (optional).
            action (int): The action of the marker (optional).
            pose (list): The pose of the marker [x, y, z, qx, qy, qz, qw] (optional).
            position (Union[list, np.ndarray]): The new position of the marker [x, y, z] (optional).
            orientation (Union[list, np.ndarray]): The new orientation of the marker [qx, qy, qz, qw] (optional).
            lifetime (float): The lifetime of the marker in seconds (optional).
            scale (list): The scale of the marker [x, y, z] (optional).
            color (list): The color of the marker [r, g, b, a] (optional).
        """

        # Create a new RosMarker instance
        marker = RosMarker(frame_id=frame_id,
                           ns=ns,
                           marker_type=marker_type,
                           marker_topic=marker_topic,
                           marker_id=marker_id,
                           action=action,
                           pose=pose,
                           position=position,
                           orientation=orientation,
                           lifetime=lifetime,
                           scale=scale,
                           color=color)

        # Add the new marker to the list
        self.markers.append(marker)

    def remove_marker(self, marker_id: int):
        """
        Remove a marker from the array.

        Args:
            marker_id (int): The ID of the marker to remove.
        """

        # Find the index of the marker with the specified ID
        marker_index = None
        for i, marker in enumerate(self.markers):
            if marker.marker.id == marker_id:
                marker_index = i
                break

        # Remove the marker from the list if it was found
        if marker_index is not None:
            del self.markers[marker_index]

    def update_markers(self, frame_id: str = None, ns: str = None, marker_type: int = None, action: int = None,
                       position: list = None, orientation: list = None, scale: list = None, color: list = None,
                       lifetime: float = None):
        """
        Update all markers in the array.

        Args:
            frame_id (str): The new frame ID of the markers (optional)
            ns (str): The new namespace of the markers (optional).
            marker_type (int): The new type of the markers (optional).
            action (int): The new action of the markers (optional).
            position (list): The new position of the markers [x, y, z] (optional).
            orientation (list): The new orientation of the markers [qx, qy, qz, qw] (optional).
            scale (list): The new scale of the markers [x, y, z] (optional).
            color (list): The new color of the markers [r, g, b, a] (optional).
            lifetime (float): The new lifetime of the markers in seconds (optional).
        """

        # Iterate over the list of markers
        for marker in self.markers:

            # Update the frame_id of the marker if provided
            if frame_id is not None:
                marker.set_frame_id(frame_id)

            # Update the namespace of the marker if provided
            if ns is not None:
                marker.set_ns(ns)

            # Update the marker_type of the marker if provided
            if marker_type is not None:
                marker.set_type(marker_type)

            # Update the action of the marker if provided
            if action is not None:
                marker.set_action(action)

            # Update the position of the marker if provided
            if position is not None:
                marker.set_position(position)

            # Update the orientation of the marker if provided
            if orientation is not None:
                marker.set_orientation(orientation)

            # Update the scale of the marker if provided
            if scale is not None:
                marker.set_scale(scale)

            # Update the color of the marker if provided
            if color is not None:
                marker.set_color(color)

            # Update the lifetime of the marker if provided
            if lifetime is not None:
                marker.set_duration(lifetime)

    def publish(self):
        """
        Publish all markers in the array.
        """

        # Create a MarkerArray message
        marker_array = MarkerArray()

        # Add all markers to the MarkerArray
        for marker in self.markers:
            # Update the timestamp of the marker
            marker.marker.header.stamp = rospy.Time.now()

            # Add the marker to the MarkerArray
            marker_array.markers.append(marker.marker)

        # Publish the MarkerArray
        self.publisher.publish(marker_array)

    def delete_all_markers(self):
        """
        Delete all markers in the array.
        """

        # Iterate over the list of markers
        for marker in self.markers:
            # Set the action of the marker to DELETE
            marker.delete()

        # Publish the updated markers
        self.publish()

    def remove_all_markers(self):
        """
        Remove all markers from the array.
        """

        # Clear the list of markers
        self.markers.clear()

    def get_marker_by_id(self, marker_id: int):
        """
        Get a marker by its ID.

        Args:
            marker_id (int): The ID of the marker to get.

        Returns:
            RosMarker: The marker with the specified ID, or None if no such marker exists.
        """

        # Find the marker with the specified ID
        for marker in self.markers:
            if marker.marker.id == marker_id:
                return marker

        # Return None if no such marker was found
        return None

    def get_markers_by_property(self, property_name: str, property_value):
        """
        Get all markers with a specific property value.

        Args:
            property_name (str): The name of the property to check (e.g., "ns" or "type").
            property_value: The value of the property to check for.

        Returns:
            list[RosMarker]: A list of all markers with the specified property value.
        """

        # Find all markers with the specified property value
        markers = []
        for marker in self.markers:
            if getattr(marker.marker, property_name) == property_value:
                markers.append(marker)

        # Return the list of markers
        return markers
