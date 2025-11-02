#!/usr/bin/env python3

import os
import sys

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from sensor_msgs.msg import Image
from geometry_msgs.msg import Pose
from geometry_msgs.msg import Point
from jsk_enshu_msgs.msg import PeoplePoseArray
from jsk_enshu_msgs.msg import PeoplePose
from jsk_enshu_msgs.msg import HumanSkeleton
from jsk_enshu_msgs.msg import HumanSkeletonArray
from jsk_enshu_msgs.msg import Segment

import cv2
import mediapipe as mp
from cv_bridge import CvBridge


class PeoplePoseEstimation(Node):

    def __init__(self):
        super().__init__('people_pose_estimation')

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose

        self.connections = mp.solutions.pose.POSE_CONNECTIONS
        self.names = [i.name.lower()
                      for i in mp.solutions.pose.PoseLandmark]
        self.get_logger().info(f'Pose landmarks: {self.names}')

        self.people_pose_estimator = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

        self.bridge = CvBridge()

        self.pub_img = self.create_publisher(
            Image, '~/output/viz', 10)
        self.pose_pub = self.create_publisher(
            PeoplePoseArray, '~/output/pose', 10)
        self.pub_img_compressed = self.create_publisher(
            CompressedImage, '~/output/viz/compressed', 10)
        self.skeleton_pub = self.create_publisher(
            HumanSkeletonArray, '~/output/skeleton', 10)

        self.sub = self.create_subscription(
            Image,
            '~/input',
            self.callback,
            10)

    def callback(self, img_msg):
        bridge = self.bridge

        mp_drawing = self.mp_drawing
        mp_pose = self.mp_pose

        image = bridge.imgmsg_to_cv2(img_msg, desired_encoding='bgr8')

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = self.people_pose_estimator.process(image)

        people_pose_msg = PeoplePoseArray()
        people_pose_msg.header = img_msg.header
        skeleton_msgs = HumanSkeletonArray()
        skeleton_msgs.header = img_msg.header
        _PRESENCE_THRESHOLD = 0.5
        _VISIBILITY_THRESHOLD = 0.5
        if results.pose_landmarks:
            pose_list = []
            for pose_landmarks in [results.pose_landmarks]:
                pose_msg = PeoplePose()
                image_rows, image_cols, _ = image.shape
                pose = {}
                for idx, landmark in enumerate(pose_landmarks.landmark):
                    if ((landmark.HasField('visibility') and
                         landmark.visibility < _VISIBILITY_THRESHOLD) or
                        (landmark.HasField('presence') and
                         landmark.presence < _PRESENCE_THRESHOLD)):
                        continue
                    landmark_px = self.mp_drawing._normalized_to_pixel_coordinates(
                        landmark.x, landmark.y,
                        image_cols, image_rows)
                    if landmark_px:
                        pose_msg.scores.append(landmark.visibility)
                        pose_msg.limb_names.append(self.names[idx])
                        pose_msg.poses.append(
                            Pose(position=Point(x=float(landmark_px[0]),
                                                y=float(landmark_px[1]),
                                                z=0.0)))
                        pose[self.names[idx]] = np.array([landmark_px[0],
                                                          landmark_px[1],
                                                          0.0])
                people_pose_msg.poses.append(pose_msg)
                pose_list.append(pose)

            for pose in pose_list:
                skeleton_msg = HumanSkeleton()
                skeleton_msg.header = img_msg.header
                for a, b in self.connections:
                    a_name = self.names[a]
                    b_name = self.names[b]
                    if not (a_name in pose and b_name in pose):
                        continue
                    bone_name = '{}->{}'.format(a_name, b_name)
                    bone = Segment(
                        start_point=Point(x=pose[a_name][0],
                                        y=pose[a_name][1],
                                        z=pose[a_name][2]),
                        end_point=Point(x=pose[b_name][0],
                                      y=pose[b_name][1],
                                      z=pose[b_name][2]))
                    skeleton_msg.bones.append(bone)
                    skeleton_msg.bone_names.append(bone_name)
                skeleton_msgs.skeletons.append(skeleton_msg)
        self.pose_pub.publish(people_pose_msg)
        self.skeleton_pub.publish(skeleton_msgs)

        num_subscribers = self.count_subscribers('~/output/viz') + \
                         self.count_subscribers('~/output/viz/compressed')
        if num_subscribers > 0:
            # Draw the pose annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.pose_landmarks:
                for pose_landmarks in [results.pose_landmarks]:
                    mp_drawing.draw_landmarks(
                        image, pose_landmarks, self.connections)

        if self.count_subscribers('~/output/viz') > 0:
            out_img_msg = bridge.cv2_to_imgmsg(
                image, encoding='bgr8')
            out_img_msg.header = img_msg.header
            self.pub_img.publish(out_img_msg)

        if self.count_subscribers('~/output/viz/compressed') > 0:
            # publish compressed
            vis_compressed_msg = CompressedImage()
            vis_compressed_msg.header = img_msg.header
            vis_compressed_msg.format = 'bgr8' + '; jpeg compressed bgr8'
            vis_compressed_msg.data = np.array(
                cv2.imencode('.jpg', image)[1]).tobytes()
            self.pub_img_compressed.publish(vis_compressed_msg)


def main(args=None):
    rclpy.init(args=args)
    node = PeoplePoseEstimation()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
