#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64


class JointCommandRelay(Node):
    def __init__(self):
        super().__init__('joint_command_relay')
        
        # Joint names that we want to control
        self.joint_names = [
            'rarm_joint0',
            'larm_joint0', 
            'head_joint0',
            'mechanum_joint1',
            'mechanum_joint2',
            'mechanum_joint3',
            'mechanum_joint4'
        ]
        
        # Subscriber to joint states from Joint State Publisher GUI
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )
        
        # Publishers for individual joint commands to Gazebo
        self.joint_publishers = {}
        for joint_name in self.joint_names:
            if 'mechanum' in joint_name:
                # Velocity commands for continuous joints (wheels)
                topic_name = f'/world/default/model/jedy/joint/{joint_name}/cmd_vel'
            else:
                # Position commands for revolute joints
                topic_name = f'/world/default/model/jedy/joint/{joint_name}/cmd_pos'
            
            self.joint_publishers[joint_name] = self.create_publisher(
                Float64,
                topic_name,
                10
            )
        
        self.get_logger().info('Joint Command Relay Node started')
        self.get_logger().info(f'Relaying commands for joints: {self.joint_names}')

    def joint_state_callback(self, msg):
        """Callback to process joint states and publish individual commands"""
        if not msg.name or not msg.position:
            return
            
        # Process each joint in the message
        for i, joint_name in enumerate(msg.name):
            if joint_name in self.joint_names and i < len(msg.position):
                # Create Float64 message with joint position/velocity
                cmd_msg = Float64()
                cmd_msg.data = msg.position[i]
                
                # Publish the command
                if joint_name in self.joint_publishers:
                    self.joint_publishers[joint_name].publish(cmd_msg)


def main(args=None):
    rclpy.init(args=args)
    
    joint_relay = JointCommandRelay()
    
    try:
        rclpy.spin(joint_relay)
    except KeyboardInterrupt:
        pass
    
    joint_relay.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()