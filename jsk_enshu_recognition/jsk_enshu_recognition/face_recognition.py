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


class FaceRecognition(Node):

    def __init__(self):
        super().__init__('face_recognition')

        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils

        self.connections = [
            (self.mp_face_detection.FaceKeyPoint.RIGHT_EYE,
             self.mp_face_detection.FaceKeyPoint.RIGHT_EAR_TRAGION),
            (self.mp_face_detection.FaceKeyPoint.NOSE_TIP,
             self.mp_face_detection.FaceKeyPoint.RIGHT_EYE),
            (self.mp_face_detection.FaceKeyPoint.LEFT_EYE,
             self.mp_face_detection.FaceKeyPoint.LEFT_EAR_TRAGION),
            (self.mp_face_detection.FaceKeyPoint.NOSE_TIP,
             self.mp_face_detection.FaceKeyPoint.LEFT_EYE),
            (self.mp_face_detection.FaceKeyPoint.MOUTH_CENTER,
             self.mp_face_detection.FaceKeyPoint.NOSE_TIP),
        ]
        self.names = [i.name.lower()
                      for i in self.mp_face_detection.FaceKeyPoint]

        self.face_estimator = self.mp_face_detection.FaceDetection(
            min_detection_confidence=0.5)

        self.bridge = CvBridge()

        self.pub_img = self.create_publisher(
            Image, '~/output/viz', 10)
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
        mp_face_detection = self.mp_face_detection

        image = bridge.imgmsg_to_cv2(img_msg, desired_encoding='bgr8')

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = self.face_estimator.process(image)
        image_rows, image_cols, _ = image.shape

        skeleton_msgs = HumanSkeletonArray()
        skeleton_msgs.header = img_msg.header
        if results.detections:
            for detection in results.detections:
                location = detection.location_data
                relative_bounding_box = location.relative_bounding_box
                xy = self.mp_drawing._normalized_to_pixel_coordinates(
                    relative_bounding_box.xmin, relative_bounding_box.ymin,
                    image_cols, image_rows)
                if xy is None:
                    continue
                x1, y1 = xy
                xy = self.mp_drawing._normalized_to_pixel_coordinates(
                    relative_bounding_box.xmin + relative_bounding_box.width,
                    relative_bounding_box.ymin + relative_bounding_box.height,
                    image_cols, image_rows)
                if xy is None:
                    continue
                x2, y2 = xy

                skeleton_msg = HumanSkeleton()
                skeleton_msg.header = img_msg.header
                index2pixel = {}
                for i, keypoint in enumerate(location.relative_keypoints):
                    if keypoint is None:
                        continue
                    keypoint_px = self.mp_drawing._normalized_to_pixel_coordinates(
                        keypoint.x, keypoint.y,
                        image_cols, image_rows)
                    if keypoint_px is None:
                        continue
                    index2pixel[i] = [float(keypoint_px[0]), float(keypoint_px[1]), 0.0]
                for a_index, b_index in self.connections:
                    if not (a_index in index2pixel and b_index in index2pixel):
                        continue
                    a = self.names[a_index]
                    b = self.names[b_index]
                    bone_name = '{}->{}'.format(a, b)
                    bone = Segment(
                        start_point=Point(x=index2pixel[a_index][0],
                                        y=index2pixel[a_index][1],
                                        z=index2pixel[a_index][2]),
                        end_point=Point(x=index2pixel[b_index][0],
                                      y=index2pixel[b_index][1],
                                      z=index2pixel[b_index][2]))
                    skeleton_msg.bones.append(bone)
                    skeleton_msg.bone_names.append(bone_name)

                skeleton_msgs.skeletons.append(skeleton_msg)
        self.skeleton_pub.publish(skeleton_msgs)

        num_subscribers = self.count_subscribers('~/output/viz') + \
                         self.count_subscribers('~/output/viz/compressed')
        if num_subscribers > 0:
            # Draw the pose annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.detections:
                for detection in results.detections:
                    mp_drawing.draw_detection(image, detection)

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
    node = FaceRecognition()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
