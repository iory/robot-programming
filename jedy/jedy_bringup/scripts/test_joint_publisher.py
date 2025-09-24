#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from builtin_interfaces.msg import Time
import time

class TestJointPublisher(Node):
    def __init__(self):
        super().__init__('test_joint_publisher')
        
        # Joint state publisher
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Timer for publishing joint states
        self.timer = self.create_timer(0.1, self.publish_joint_states)
        
        # Joint names from URDF
        self.joint_names = [
            'rarm_joint0',
            'larm_joint0', 
            'head_joint0',
            'rarm_module1_joint1',
            'rarm_module1_joint2',
            'rarm_module2_joint1',
            'right_hand_joint1',
            'right_hand_joint2',
            'larm_module1_joint1',
            'larm_module1_joint2', 
            'larm_module2_joint1',
            'left_hand_joint1',
            'left_hand_joint2',
            'mechanum_joint1',
            'mechanum_joint2',
            'mechanum_joint3',
            'mechanum_joint4',
            'head_module1_joint1'
        ]
        
        self.get_logger().info(f'Publishing joint states for {len(self.joint_names)} joints')
        
    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        
        # Set all joints to zero position
        msg.position = [0.0] * len(self.joint_names)
        msg.velocity = [0.0] * len(self.joint_names)
        msg.effort = [0.0] * len(self.joint_names)
        
        self.joint_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = TestJointPublisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()