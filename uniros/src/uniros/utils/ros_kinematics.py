#!/bin/python3

"""
There are two classes in this file that provide similar functionality:
- Kinematics_pyrobot: This is modified from the Kinematics class in the pyrobot repo.
- Kinematics_pykdl: Kinematics class based on pykdl_utils package.

These classes provide kinematics functionality for a robot. Instead of using computation-heavy ROS packages like MoveIt,
this class uses the KDL library to perform kinematics calculations.

With these classes, you can calculate,
- Forward kinematics - compute the pose of the end-effector given the joint angles
- Inverse kinematics - compute the joint angles given the pose of the end-effector

Since both classes provide similar functionality, you can use either one of them. However, the Kinematics_pyrobot class
is recommended since it is more flexible and provides more functionality.
"""

import numpy as np
from urdf_parser_py.urdf import URDF
from pykdl_utils.kdl_parser import kdl_tree_from_urdf_model
from pykdl_utils.kdl_kinematics import KDLKinematics
from tf.transformations import euler_from_matrix
from tf.transformations import quaternion_matrix

import PyKDL as kdl
import copy
import tf
from kdl_parser_py.urdf import treeFromParam
from trac_ik_python import trac_ik
import rospy


class Kinematics_pyrobot(object):
    """
    This is modified from the Kinematics class in the pyrobot repo.
    link: https://github.com/facebookresearch/pyrobot/blob/b334b60842271d9d8f4ed7a97bc4e5efe8bb72d6/pyrobot_bridge/nodes/kinematics.py
    """

    def __init__(self, robot_description_parm: str, base_link: str, end_link: str, debug=False):
        """
        Initialize the Kinematics class.

        Args:
            robot_description_parm: robot description parameter name including the namespace
            base_link: base link of the robot including the namespace
            end_link: end-effector link of the robot including the namespace
            debug: debug flag
        """
        # Validate inputs
        if not robot_description_parm or not base_link or not end_link:
            raise ValueError("Inputs robot_description, base_link, and end_link must be non-empty strings.")

        # robot description from parameter server
        robot_description = rospy.get_param(param_name=robot_description_parm)

        # get robot urdf from parameter server
        # robot_urdf = URDF.from_parameter_server(key=self._robot_description_parm_name)

        # create ik solver
        self.num_ik_solver = trac_ik.IK(base_link=base_link, tip_link=end_link, urdf_string=robot_description)

        # get the kinematic tree from the robot urdf
        _, self.urdf_tree = treeFromParam(param=robot_description_parm)

        # get the kinematic chain from the kinematic tree
        self.urdf_chain = self.urdf_tree.getChain(chain_root=base_link, chain_tip=end_link)

        # get the joint names from the kinematic chain
        self.arm_joint_names = self._get_kdl_joint_names()
        if debug:
            print("arm_joint_names:", self.arm_joint_names)

        # get the link names from the kinematic chain
        self.arm_link_names = self._get_kdl_link_names()
        if debug:
            print("arm_link_names:", self.arm_link_names)

        # get the number of joints in the kinematic chain
        self.arm_dof = len(self.arm_joint_names)
        if debug:
            print("arm_dof:", self.arm_dof)

        # compute the Jacobian matrix.
        # represents how the velocity of the end-effector is related to the velocities of the joints
        self.jac_solver = kdl.ChainJntToJacSolver(self.urdf_chain)

        # compute the forward kinematics - position
        self.fk_solver_pos = kdl.ChainFkSolverPos_recursive(self.urdf_chain)

        # compute the forward kinematics - velocity
        self.fk_solver_vel = kdl.ChainFkSolverVel_recursive(self.urdf_chain)

    def _get_kdl_link_names(self):
        """
        Get the link names from the kinematic chain.
        """

        # get the number of links in the kinematic chain - the rigid bodies
        num_links = self.urdf_chain.getNrOfSegments()

        # get the link names from the kinematic chain
        link_names = []
        for i in range(num_links):
            link_names.append(self.urdf_chain.getSegment(i).getName())
        return copy.deepcopy(link_names)

    def _get_kdl_joint_names(self):
        """
        Get the joint names from the kinematic chain.
        """

        # same as above
        num_links = self.urdf_chain.getNrOfSegments()

        # get the joint names from the kinematic chain
        num_joints = self.urdf_chain.getNrOfJoints()  # for assertion

        # get the joint names from the kinematic chain
        joint_names = []
        for i in range(num_links):
            link = self.urdf_chain.getSegment(i)
            joint = link.getJoint()
            joint_type = joint.getType()  # types 0 and 1 represent rotational and translational joints, respectively.
            # JointType definition: [RotAxis,RotX,RotY,RotZ,TransAxis,
            #                        TransX,TransY,TransZ,None]
            if joint_type > 1:
                continue
            joint_names.append(joint.getName())
        assert num_joints == len(joint_names)
        return copy.deepcopy(joint_names)

    def calculate_ik(self, target_pose, tolerance, init_joint_positions):
        """
        Calculate the inverse kinematics for a given pose.

        Args:
            target_pose (list): The desired position and orientation of the end effector given as [x, y, z, qx, qy, qz, qw]
            tolerance (list): The tolerance for each of the pose components
            init_joint_positions (list): The initial positions of the joints from which to start the IK calculation

        Returns:
            A tuple (success, joint_positions), where `success` is a boolean indicating success of IK,
            and `joint_positions` are the calculated joint angles.
        """

        # Validate inputs
        if len(target_pose) < 7 or len(tolerance) < 6 or len(init_joint_positions) != self.arm_dof:
            rospy.logerr("Incorrect IK parameters. Please fix them.")
            return False, None

        # Calculate IK
        joint_positions_IK = self.num_ik_solver.get_ik(
            init_joint_positions,
            target_pose[0], target_pose[1], target_pose[2],
            target_pose[3], target_pose[4], target_pose[5], target_pose[6],
            tolerance[0], tolerance[1], tolerance[2],
            tolerance[3], tolerance[4], tolerance[5],
        )

        # Check if a valid joint position list is returned
        if joint_positions_IK is None:
            rospy.logwarn("Failed to find an IK solution.")
            return False, None

        # Return the joint positions
        return True, np.array(joint_positions_IK)

    def _kdl_frame_to_numpy(self, frame):
        """
        Convert the KDL frame to a numpy array.

        Args:
            frame: KDL frame
        """
        p = frame.p
        M = frame.M
        return np.array(
            [
                [M[0, 0], M[0, 1], M[0, 2], p.x()],
                [M[1, 0], M[1, 1], M[1, 2], p.y()],
                [M[2, 0], M[2, 1], M[2, 2], p.z()],
                [0, 0, 0, 1],
            ]
        )

    @staticmethod
    def rot_mat_to_quat(rot):
        """
        Convert the rotation matrix into quaternion.

        Args:
            rot (numpy.ndarray): the rotation matrix (shape: :math:`[3, 3]`)
        Returns:
            quaternion (numpy.ndarray) [x, y, z, w] (shape: :math:`[4,]`)
        """
        R = np.eye(4)
        R[:3, :3] = rot
        return tf.transformations.quaternion_from_matrix(R)

    @staticmethod
    def joints_to_kdl(joint_values):
        """
        Convert the numpy array into KDL data format

        Args:
            joint_values: values for the joints
        Returns:
            kdl data type for the joints
        """
        num_jts = joint_values.size
        kdl_array = kdl.JntArray(num_jts)
        for idx in range(num_jts):
            kdl_array[idx] = joint_values[idx]
        return kdl_array

    def calculate_fk(self, joint_positions, des_frame, euler=True):
        """
        Given joint angles, compute the pose of desired_frame with respect
        to the base frame. The desired frame must be in self.arm_link_names.

        Args:
            joint_positions (np.ndarray): Joint angles.
            des_frame (str): Desired frame.
            euler (bool): If True, return the orientation in Euler angles.

        Returns:
            A tuple (success, pos, rpy), where `success` is a boolean indicating success of FK,
            and `pos` are the calculated position and `rpy` are the calculated roll, pitch, yaw.
        """
        # Validate inputs
        if not isinstance(joint_positions, np.ndarray):
            raise ValueError("joint_positions must be of type np.ndarray")
        if des_frame not in self.arm_link_names:
            raise ValueError("des_frame must be one of the configured link names")
        if joint_positions.size != self.arm_dof:
            raise ValueError("Invalid length of joint angles! Expected length: {}".format(self.arm_dof))

        # covert joint positions to kdl data type
        kdl_jnt_angles = self.joints_to_kdl(joint_positions)

        # Create a KDL frame to hold the result
        kdl_end_frame = kdl.Frame()

        # Get the index of the desired frame within the robot's link names
        idx = self.arm_link_names.index(des_frame) + 1

        # Perform the JntToCart calculation to get the pose of the desired frame
        fk_result = self.fk_solver_pos.JntToCart(kdl_jnt_angles, kdl_end_frame, idx)

        # Check for any errors during computation
        if fk_result < 0:
            rospy.logerr("Error computing forward kinematics with KDL.")
            return False, None, None

        # Convert the KDL frame to a NumPy array to extract the position and orientation
        pose = self._kdl_frame_to_numpy(kdl_end_frame)
        pos = pose[:3, 3].reshape(-1, 1)

        if euler:
            # Convert the rotation matrix to roll-pitch-yaw angles
            rotations = euler_from_matrix(pose[:3, :3], 'sxyz')  # 'sxyz' specifies static (fixed) axes
            rotations = np.array(rotations).flatten()
        else:
            # Convert the rotation matrix to a quaternion
            rotations = self.rot_mat_to_quat(pose[:3, :3])

        # Return position and rotations both as 1D arrays
        return True, pos.flatten(), rotations


class Kinematics_pykdl(object):
    """
    Kinematics class based on pykdl_utils package.
    https://github.com/ncbdrck/hrl-kdl
    """

    def __init__(self, robot_description_parm: str, base_link: str, end_link: str, debug=False):
        """
        Initialize the Kinematics class.

        Args:
            robot_description_parm: robot description parameter name including the namespace
            base_link: base link of the robot including the namespace
            end_link: end-effector link of the robot including the namespace
            debug: debug mode
        """

        # Validate inputs
        if not robot_description_parm or not base_link or not end_link:
            raise ValueError("Inputs robot_description, base_link, and end_link must be non-empty strings.")

        # load the robot urdf from parameter server
        self.pykdl_robot = URDF.from_parameter_server(key=robot_description_parm)

        # create the kdl kinematics
        self.kdl_kin = KDLKinematics(urdf=self.pykdl_robot, base_link=base_link, end_link=end_link)

        if debug:
            # get the kdl tree from the robot urdf
            tree = kdl_tree_from_urdf_model(self.pykdl_robot)

            # Print the number of links in the tree - the rigid bodies
            print("All Links from tree:", tree.getNrOfSegments())

            # Print the number of joints in the tree - the joints
            print("All Joints from tree:", tree.getNrOfJoints())

            # get the kdl chain from the kdl tree - the kinematic chain
            chain = tree.getChain(base_link, end_link)

            # Print the number of links in the chain - the rigid bodies
            print("Links from chain:", chain.getNrOfSegments())

            # Print the number of joints in the chain - the joints
            print("Joints from chain:", chain.getNrOfJoints())

            # Print the joint names
            print("Joint names from chain:")
            for i in range(chain.getNrOfSegments()):
                print(chain.getSegment(i).getJoint().getName())

            # Print the link names
            print("Link names from chain:")
            for i in range(chain.getNrOfSegments()):
                print(chain.getSegment(i).getName())

            # # Print the link names
            # print("Link names from URDF:")
            # for link_name in self.pykdl_robot.link_map.keys():
            #     print(link_name)
            #
            # # Print the joint names
            # print("Joint names from URDF:")
            # for joint_name in self.pykdl_robot.joint_map.keys():
            #     print(joint_name)

    @staticmethod
    def rot_mat_to_quat(rot):
        """
        Convert the rotation matrix into quaternion.

        Args:
            rot (numpy.ndarray): the rotation matrix (shape: :math:`[3, 3]`)
        Returns:
            quaternion (numpy.ndarray) [x, y, z, w] (shape: :math:`[4,]`)
        """
        R = np.eye(4)
        R[:3, :3] = rot
        return tf.transformations.quaternion_from_matrix(R)

    def calculate_fk(self, joint_positions, end_link=None, base_link=None, euler=True):
        """
        Given joint angles, compute the pose of desired_frame with respect
        to the base frame. The desired frame must be in self.arm_link_names.

        Args:
            joint_positions (np.ndarray): Joint angles.
            end_link (str): Desired frame. If None, the end-effector frame is used.
            base_link (str): Base frame. If None, the base frame is used.
            euler (bool): If True, return the orientation in Euler angles.

        Returns:
            A tuple (success, pos, rpy), where `success` is a boolean indicating success of FK,
            and `pos` are the calculated position and `rpy` are the calculated roll, pitch, yaw.
        """
        # Calculate forward kinematics
        pose_pykdl = self.kdl_kin.forward(q=joint_positions, end_link=end_link, base_link=base_link)

        # Check for any errors during computation
        if pose_pykdl is None:
            rospy.logerr("Error computing forward kinematics with KDL.")
            return False, None, None

        # Extract position
        position = np.array([pose_pykdl[0, 3], pose_pykdl[1, 3], pose_pykdl[2, 3]],
                            dtype=np.float32)  # we need to convert to float32

        if euler:
            # Extract rotation matrix and convert to euler angles
            orientation = euler_from_matrix(pose_pykdl[:3, :3], 'sxyz')
            rotations = np.array(orientation).flatten()
        else:
            # Convert the rotation matrix to a quaternion
            rotations = self.rot_mat_to_quat(pose_pykdl[:3, :3])

        return True, position, rotations

    def calculate_ik(self, target_pose, init_joint_positions=None):
        """
        Calculate the inverse kinematics for a given pose.

        Args:
            target_pose (matrix): The desired position and orientation of the end effector given as a 4x4 matrix
            init_joint_positions (list): The initial positions of the joints from which to start the IK calculation

        Returns:
            A tuple (success, joint_positions), where `success` is a boolean indicating success of IK,
            and `joint_positions` are the calculated joint angles.
        """
        # calculate inverse kinematics
        q_ik = self.kdl_kin.inverse(pose=target_pose, q_guess=init_joint_positions)

        if q_ik is None:
            rospy.logwarn("Failed to find an IK solution.")
            return False, None

        return True, np.array(q_ik)


if __name__ == '__main__':
    ########################################### examples ###########################################
    # with pyrobot
    kin = Kinematics_pyrobot(robot_description_parm='rx200/robot_description', base_link='rx200/base_link',
                             end_link='rx200/ee_gripper_link')

    # fake joint angles
    q = np.array([0.0, 0.0, 0.0, 0.0, 0.0])  # Joint angles in radians

    # desired frame
    des_frame = 'rx200/ee_gripper_link'

    # get fk
    fk_done, pos, rpy = kin.calculate_fk(q, des_frame)

    print("pyrobot fk_done:", fk_done)
    print("pyrobot pos:", pos)
    print("pyrobot rpy:", rpy)

    # random ee pose
    action = np.array([0.409951, 0.0, 0.276585], dtype=np.float32)

    # define the pose in 1D array [x, y, z, qx, qy, qz, qw]
    action = np.concatenate((action, np.array([0.0, 0.0, 0.0, 1.0])))

    # get ik
    ik_done, joint_positions = kin.calculate_ik(target_pose=action, tolerance=[1e-3] * 6,
                                                init_joint_positions=q)

    print("pyrobot ik_done:", ik_done)
    print("pyrobot joint_positions:", joint_positions)

    ###########################################
    # with pykdl_utils
    kin_pykdl = Kinematics_pykdl(robot_description_parm='rx200/robot_description', base_link='rx200/base_link',
                                 end_link='rx200/ee_gripper_link', debug=False)

    # get fk
    fk_done, pos, rpy = kin_pykdl.calculate_fk(q)

    print("py_kdl fk_done:", fk_done)
    print("py_kdl pos:", pos)
    print("py_kdl rpy:", rpy)

    # This is your RL action which represents the desired position
    action = np.array([0.409951, 0.0, 0.276585], dtype=np.float32)

    # Default orientation in quaternion (no rotation)
    default_orientation = np.array([0.0, 0.0, 0.0, 1.0])

    # Convert the quaternion into a 4x4 rotation matrix
    rotation_matrix = quaternion_matrix(default_orientation)

    # Place the position into the translation part of the pose matrix
    pose_matrix = np.matrix(rotation_matrix)  # Make sure it is a numpy matrix, as KDL expects
    pose_matrix[:3, 3] = action.reshape(3, 1)  # Reshape just for safety

    # get ik
    ik_done, joint_positions = kin_pykdl.calculate_ik(target_pose=pose_matrix, init_joint_positions=q)

    print("py_kdl ik_done:", ik_done)
    print("py_kdl joint_positions:", joint_positions)
