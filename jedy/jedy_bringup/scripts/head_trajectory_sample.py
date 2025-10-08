#!/usr/bin/env python3
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import numpy as np

class HeadTrajectoryActionClient(Node):
    """
    A ROS 2 action client to send head joint trajectory goals.
    """
    def __init__(self):
        super().__init__('head_trajectory_action_client')

        # Action client for the FollowJointTrajectory action
        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/head_controller/follow_joint_trajectory'
        )
        self.start_time = None
        self.get_logger().info("Head trajectory action client initialized.")

    def send_goal(self):
        """Creates and sends a head joint trajectory goal to the action server."""

        # 1. Wait for the action server to be available
        self.get_logger().info('Waiting for action server to be available...')
        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Action server not available after 5 seconds.')
            rclpy.shutdown()
            return

        # 2. Create the goal message (including the trajectory)
        goal_msg = FollowJointTrajectory.Goal()

        traj = JointTrajectory()

        # Head joint names
        traj.joint_names = ['head_joint0', 'head_joint1']

        # Define trajectory points
        # Point 1: Look right and slightly down
        point1 = JointTrajectoryPoint()
        point1.positions = [np.deg2rad(60), np.deg2rad(20)]  # head_joint0=60deg, head_joint1=20deg
        point1.time_from_start = Duration(sec=2, nanosec=0)
        traj.points.append(point1)

        # Point 2: Look left and slightly down
        point2 = JointTrajectoryPoint()
        point2.positions = [np.deg2rad(-60), np.deg2rad(20)]  # head_joint0=-60deg, head_joint1=20deg
        point2.time_from_start = Duration(sec=4, nanosec=0)
        traj.points.append(point2)

        # Point 3: Look center and down
        point3 = JointTrajectoryPoint()
        point3.positions = [0.0, np.deg2rad(40)]  # head_joint0=0deg, head_joint1=40deg
        point3.time_from_start = Duration(sec=6, nanosec=0)
        traj.points.append(point3)

        # Point 4: Look up
        point4 = JointTrajectoryPoint()
        point4.positions = [0.0, np.deg2rad(-30)]  # head_joint0=0deg, head_joint1=-30deg
        point4.time_from_start = Duration(sec=8, nanosec=0)
        traj.points.append(point4)

        # Point 5: Return to center
        point5 = JointTrajectoryPoint()
        point5.positions = [0.0, 0.0]  # head_joint0=0deg, head_joint1=0deg
        point5.time_from_start = Duration(sec=10, nanosec=0)
        traj.points.append(point5)

        goal_msg.trajectory = traj

        # 3. Send the goal
        self.get_logger().info('Sending goal to the action server...')

        # send_goal_async returns a future to a goal handle
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        # Register a callback for when the future is complete
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """Callback function for when the goal is accepted or rejected."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected by server')
            rclpy.shutdown()
            return

        self.get_logger().info('Goal accepted by server, waiting for result...')

        self.start_time = self.get_clock().now()

        # Get the result future
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """Callback function for when the action is finished."""
        result = future.result().result

        # Check the error code
        if result.error_code == FollowJointTrajectory.Result.SUCCESSFUL:
            self.get_logger().info('Head trajectory execution successful!')
        else:
            self.get_logger().error(f'Head trajectory execution failed with error code: {result.error_code}')

        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        """Callback function for receiving feedback during the action."""
        feedback = feedback_msg.feedback

        # Check if the feedback contains the necessary info
        if not feedback.actual.positions or not feedback.desired.time_from_start:
            return

        # Get current joint angles and convert from radians to degrees
        actual_positions_rad = feedback.actual.positions
        actual_positions_deg = np.rad2deg(actual_positions_rad)
        formatted_degrees = [f"{deg:.2f}" for deg in actual_positions_deg]

        # Log the combined feedback
        self.get_logger().info(
            f"Head Angles (deg): [joint0: {formatted_degrees[0]}, joint1: {formatted_degrees[1]}]"
        )


def main(args=None):
    rclpy.init(args=args)

    action_client = HeadTrajectoryActionClient()
    action_client.send_goal()

    # Spin the node to allow callbacks to be processed
    rclpy.spin(action_client)


if __name__ == '__main__':
    main()
