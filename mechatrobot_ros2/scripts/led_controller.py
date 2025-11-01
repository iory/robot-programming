#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, ColorRGBA
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy


class LEDController(Node):
    def __init__(self):
        super().__init__('led_controller')

        # Subscribe to LED state command
        self.led_state_sub = self.create_subscription(
            Bool,
            '/led/state',
            self.led_state_callback,
            10
        )

        # Publisher for Gazebo visual topic (if available)
        # This will control LED appearance in Gazebo through ros_gz_bridge
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            depth=10
        )

        self.led_color_pub = self.create_publisher(
            ColorRGBA,
            '/led_color',
            qos
        )

        self.get_logger().info('LED Controller node started')
        self.get_logger().info('Listening to /led/state (std_msgs/Bool)')
        self.get_logger().info('Publishing to /led_color (std_msgs/ColorRGBA)')

        self.current_state = False

    def led_state_callback(self, msg):
        """
        Callback for LED state changes.
        True = LED ON (bright red), False = LED OFF (dark gray)
        """
        if msg.data != self.current_state:
            self.current_state = msg.data

            color = ColorRGBA()
            if msg.data:
                # LED ON - bright red
                color.r = 1.0
                color.g = 0.0
                color.b = 0.0
                color.a = 1.0
                self.get_logger().info('LED: ON (Red)')
            else:
                # LED OFF - dark gray
                color.r = 0.3
                color.g = 0.3
                color.b = 0.3
                color.a = 1.0
                self.get_logger().info('LED: OFF (Gray)')

            self.led_color_pub.publish(color)


def main(args=None):
    rclpy.init(args=args)
    node = LEDController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
