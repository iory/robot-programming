#!/usr/bin/env python3

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo
from sensor_msgs.msg import Image
from jsk_enshu_msgs.msg import HumanSkeleton
from jsk_enshu_msgs.msg import HumanSkeletonArray
from visualization_msgs.msg import Marker
from visualization_msgs.msg import MarkerArray
from geometry_msgs.msg import Point
from std_msgs.msg import ColorRGBA
from cv_bridge import CvBridge
from image_geometry import PinholeCameraModel
from message_filters import ApproximateTimeSynchronizer, Subscriber


class SkeletonWithDepth(Node):

    def __init__(self):
        super().__init__('skeleton_with_depth')

        # Parameters
        self.declare_parameter('queue_size', 10)
        self.declare_parameter('approximate_sync', True)
        self.declare_parameter('slop', 0.1)
        self.declare_parameter('sync_camera_info', False)

        queue_size = self.get_parameter('queue_size').value
        approximate_sync = self.get_parameter('approximate_sync').value
        slop = self.get_parameter('slop').value
        sync_cam_info = self.get_parameter('sync_camera_info').value

        self.bridge = CvBridge()
        self.camera_info_msg = None
        self.camera_model = PinholeCameraModel()

        # Publishers
        self.pose_pub = self.create_publisher(
            HumanSkeletonArray, '~/output/pose', 10)
        self.marker_pub = self.create_publisher(
            MarkerArray, '~/output/marker', 10)

        # Subscribers
        self.sub_skeleton = Subscriber(self, HumanSkeletonArray, '~/input/skeleton')
        self.sub_depth = Subscriber(self, Image, '~/input/depth')

        if sync_cam_info:
            self.sub_info = Subscriber(self, CameraInfo, '~/input/info')
            self.subs = [self.sub_skeleton, self.sub_depth, self.sub_info]
            if approximate_sync:
                self.sync = ApproximateTimeSynchronizer(
                    self.subs, queue_size, slop)
            else:
                from message_filters import TimeSynchronizer
                self.sync = TimeSynchronizer(self.subs, queue_size)
            self.sync.registerCallback(self._cb_with_depth_info)
        else:
            self.sub_info = self.create_subscription(
                CameraInfo, '~/input/info', self._cb_cam_info, 10)
            self.subs = [self.sub_skeleton, self.sub_depth]
            if approximate_sync:
                self.sync = ApproximateTimeSynchronizer(
                    self.subs, queue_size, slop)
            else:
                from message_filters import TimeSynchronizer
                self.sync = TimeSynchronizer(self.subs, queue_size)
            self.sync.registerCallback(self._cb_with_depth)

        self.get_logger().info('SkeletonWithDepth node initialized')

    def _cb_cam_info(self, msg):
        if self.camera_info_msg is None:
            self.camera_info_msg = msg
            self.camera_model.fromCameraInfo(msg)
            self.destroy_subscription(self.sub_info)
            self.sub_info = None
            self.get_logger().info('Received camera info')

    def _cb_with_depth(self, skeleton_msg, depth_msg):
        if self.camera_info_msg is None:
            return
        self._cb_with_depth_info(skeleton_msg, depth_msg, self.camera_info_msg)

    def _cb_with_depth_info(self, skeleton_msg, depth_msg, camera_info_msg):
        if self.camera_info_msg is None:
            self.camera_model.fromCameraInfo(camera_info_msg)
            self.camera_info_msg = camera_info_msg

        depth_img = self.bridge.imgmsg_to_cv2(depth_msg, 'passthrough')
        if depth_msg.encoding == '16UC1':
            depth_img = np.asarray(depth_img, dtype=np.float32)
            depth_img /= 1000.0  # convert metric: mm -> m
        elif depth_msg.encoding != '32FC1':
            self.get_logger().error(f'Unsupported depth encoding: {depth_msg.encoding}')
            return

        H, W = depth_img.shape
        out_skeleton_array_msg = HumanSkeletonArray(header=skeleton_msg.header)
        marker_array = MarkerArray()
        marker_id = 0

        for skeleton_idx, skeleton in enumerate(skeleton_msg.skeletons):
            out_skeleton_msg = HumanSkeleton(header=skeleton_msg.header)

            # Color for this skeleton (different color for each person)
            colors = [
                ColorRGBA(r=1.0, g=0.0, b=0.0, a=1.0),  # Red
                ColorRGBA(r=0.0, g=1.0, b=0.0, a=1.0),  # Green
                ColorRGBA(r=0.0, g=0.0, b=1.0, a=1.0),  # Blue
                ColorRGBA(r=1.0, g=1.0, b=0.0, a=1.0),  # Yellow
                ColorRGBA(r=1.0, g=0.0, b=1.0, a=1.0),  # Magenta
                ColorRGBA(r=0.0, g=1.0, b=1.0, a=1.0),  # Cyan
            ]
            color = colors[skeleton_idx % len(colors)]

            for bone_name, bone in zip(skeleton.bone_names, skeleton.bones):
                # Process start point
                u, v = bone.start_point.x, bone.start_point.y
                if not (0 <= u < W and 0 <= v < H):
                    continue
                z_start = float(depth_img[int(v)][int(u)])
                if np.isnan(z_start) or z_start <= 0:
                    continue

                start_x = (u - self.camera_model.cx()) * z_start / self.camera_model.fx()
                start_y = (v - self.camera_model.cy()) * z_start / self.camera_model.fy()
                start_z = z_start

                # Process end point
                u, v = bone.end_point.x, bone.end_point.y
                if not (0 <= u < W and 0 <= v < H):
                    continue
                z_end = float(depth_img[int(v)][int(u)])
                if np.isnan(z_end) or z_end <= 0:
                    continue

                end_x = (u - self.camera_model.cx()) * z_end / self.camera_model.fx()
                end_y = (v - self.camera_model.cy()) * z_end / self.camera_model.fy()
                end_z = z_end

                # Update bone with 3D coordinates
                bone.start_point.x = start_x
                bone.start_point.y = start_y
                bone.start_point.z = start_z
                bone.end_point.x = end_x
                bone.end_point.y = end_y
                bone.end_point.z = end_z

                out_skeleton_msg.bone_names.append(bone_name)
                out_skeleton_msg.bones.append(bone)

                # Create line marker for this bone
                marker = Marker()
                marker.header = skeleton_msg.header
                marker.ns = f'skeleton_{skeleton_idx}'
                marker.id = marker_id
                marker.type = Marker.LINE_STRIP
                marker.action = Marker.ADD
                marker.scale.x = 0.01  # Line width
                marker.color = color
                marker.pose.orientation.w = 1.0

                # Add start and end points
                marker.points.append(Point(x=start_x, y=start_y, z=start_z))
                marker.points.append(Point(x=end_x, y=end_y, z=end_z))

                marker_array.markers.append(marker)
                marker_id += 1

                # Create sphere markers for joints
                # Start point sphere
                sphere_marker_start = Marker()
                sphere_marker_start.header = skeleton_msg.header
                sphere_marker_start.ns = f'joints_{skeleton_idx}'
                sphere_marker_start.id = marker_id
                sphere_marker_start.type = Marker.SPHERE
                sphere_marker_start.action = Marker.ADD
                sphere_marker_start.pose.position.x = start_x
                sphere_marker_start.pose.position.y = start_y
                sphere_marker_start.pose.position.z = start_z
                sphere_marker_start.pose.orientation.w = 1.0
                sphere_marker_start.scale.x = 0.02
                sphere_marker_start.scale.y = 0.02
                sphere_marker_start.scale.z = 0.02
                sphere_marker_start.color = color
                marker_array.markers.append(sphere_marker_start)
                marker_id += 1

                # End point sphere
                sphere_marker_end = Marker()
                sphere_marker_end.header = skeleton_msg.header
                sphere_marker_end.ns = f'joints_{skeleton_idx}'
                sphere_marker_end.id = marker_id
                sphere_marker_end.type = Marker.SPHERE
                sphere_marker_end.action = Marker.ADD
                sphere_marker_end.pose.position.x = end_x
                sphere_marker_end.pose.position.y = end_y
                sphere_marker_end.pose.position.z = end_z
                sphere_marker_end.pose.orientation.w = 1.0
                sphere_marker_end.scale.x = 0.02
                sphere_marker_end.scale.y = 0.02
                sphere_marker_end.scale.z = 0.02
                sphere_marker_end.color = color
                marker_array.markers.append(sphere_marker_end)
                marker_id += 1

            out_skeleton_array_msg.skeletons.append(out_skeleton_msg)

        self.pose_pub.publish(out_skeleton_array_msg)
        self.marker_pub.publish(marker_array)


def main(args=None):
    rclpy.init(args=args)
    node = SkeletonWithDepth()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
