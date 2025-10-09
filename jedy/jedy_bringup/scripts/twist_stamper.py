#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped


class TwistStamper(Node):
    """
    Simple node to convert Twist messages to TwistStamped messages.
    This is useful for compatibility with nav2 and teleop tools that publish Twist,
    while using controllers that require TwistStamped.
    """

    def __init__(self):
        super().__init__('twist_stamper')

        self.declare_parameter('frame_id', 'base_link')

        self.frame_id = self.get_parameter('frame_id').get_parameter_value().string_value

        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel_in',
            self.twist_callback,
            10
        )

        self.publisher = self.create_publisher(
            TwistStamped,
            'cmd_vel_out',
            10
        )

        self.get_logger().info(f'TwistStamper node started. Converting Twist to TwistStamped with frame_id: {self.frame_id}')

    def twist_callback(self, msg):
        """Convert Twist to TwistStamped and publish."""
        stamped_msg = TwistStamped()
        stamped_msg.header.stamp = self.get_clock().now().to_msg()
        stamped_msg.header.frame_id = self.frame_id
        stamped_msg.twist = msg

        self.publisher.publish(stamped_msg)


def main(args=None):
    rclpy.init(args=args)
    node = TwistStamper()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
