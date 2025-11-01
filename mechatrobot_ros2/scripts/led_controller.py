#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, ColorRGBA
from visualization_msgs.msg import Marker
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy


class LEDController(Node):
    def __init__(self):
        super().__init__('led_controller')

        # Subscribe to LED state command (Bool: True=Orange, False=Gray)
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

        # Publisher for RViz2 Marker visualization
        self.led_marker_pub = self.create_publisher(
            Marker,
            '/led_marker',
            10
        )

        self.get_logger().info('LED Controller node started')
        self.get_logger().info('Listening to /led/state (std_msgs/Bool)')
        self.get_logger().info('Publishing to /led_color (std_msgs/ColorRGBA)')
        self.get_logger().info('Publishing to /led_marker (visualization_msgs/Marker)')

        self.current_state = False

    def led_state_callback(self, msg):
        """
        Callback for LED state changes.
        True = LED ON (orange), False = LED OFF (dark gray)
        """
        if msg.data != self.current_state:
            self.current_state = msg.data

            color = ColorRGBA()
            if msg.data:
                # LED ON - orange
                color.r = 1.0
                color.g = 0.5
                color.b = 0.0
                color.a = 1.0
                self.get_logger().info('LED: ON (Orange)')
            else:
                # LED OFF - dark gray
                color.r = 0.3
                color.g = 0.3
                color.b = 0.3
                color.a = 1.0
                self.get_logger().info('LED: OFF (Gray)')

            self.led_color_pub.publish(color)
            self.publish_led_marker(color)

    def publish_led_marker(self, color):
        """
        Publish a Marker for RViz2 visualization of the LED.
        The marker is positioned at the LED link location.
        """
        marker = Marker()
        marker.header.frame_id = "led"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "led_indicator"
        marker.id = 0
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD

        # Position at the center of the LED link
        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.0
        marker.pose.orientation.x = 0.0
        marker.pose.orientation.y = 0.0
        marker.pose.orientation.z = 0.0
        marker.pose.orientation.w = 1.0

        # Scale: slightly larger than the LED cylinder to be visible
        marker.scale.x = 0.006  # 6mm diameter sphere
        marker.scale.y = 0.006
        marker.scale.z = 0.006

        # Color from the LED state
        marker.color = color

        # Lifetime: 0 means forever (until replaced)
        marker.lifetime.sec = 0
        marker.lifetime.nanosec = 0

        self.led_marker_pub.publish(marker)


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
