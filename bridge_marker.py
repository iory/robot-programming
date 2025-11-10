#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from jsk_recognition_msgs.msg import BoundingBoxArray
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import ColorRGBA
import colorsys

# グローバル変数としてPublisherを保持
g_marker_array_pub = None

def generate_color_by_label(label):
    """
    ラベル番号に基づいて色を生成します (HSV色空間を利用)
    """
    # 黄金比を使って色相を分散させる
    hue = (label * 0.6180339887) % 1.0
    # 彩度と明度は固定
    saturation = 1.0
    value = 1.0
    
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    
    # 半透明 (alpha=0.5) にする
    return ColorRGBA(r=r, g=g, b=b, a=0.5)

def bbox_array_callback(bbox_array_msg):
    """
    BoundingBoxArray を受信したときのコールバック関数
    """
    global g_marker_array_pub
    if g_marker_array_pub is None:
        return

    marker_array = MarkerArray()
    
    for i, bbox in enumerate(bbox_array_msg.boxes):
        marker = Marker()
        
        # ヘッダー情報は配列のものを使用
        marker.header = bbox_array_msg.header
        
        # マーカーの識別情報
        marker.ns = "jsk_bounding_boxes"
        marker.id = i  # 配列内のインデックスをIDとして使用
        
        # 形状はCUBE (立方体)
        marker.type = Marker.CUBE
        
        # アクションは追加/修正
        marker.action = Marker.ADD
        
        # 座標と向き (BoundingBoxからそのままコピー)
        marker.pose = bbox.pose
        
        # 大きさ (BoundingBoxのdimensionsをscaleにマッピング)
        marker.scale = bbox.dimensions
        
        # 色 (ラベルに基づいて生成)
        marker.color = generate_color_by_label(bbox.label)
        
        # マーカーの寿命 (0.2秒。新しいメッセージが来ないと自動的に消える)
        # これにより、検出が消えたときにRvizからも消えます。
        marker.lifetime = rospy.Duration(2.0)
        
        marker_array.markers.append(marker)

    # 変換したMarkerArrayをパブリッシュ
    g_marker_array_pub.publish(marker_array)

def main():
    global g_marker_array_pub
    
    rospy.init_node('bbox_to_marker_converter_node')
    
    # ROS 1トピックのサブスクライバ
    # jsk_recognition_msgs/BoundingBoxArray を購読
    rospy.Subscriber('/HSI_color_filter/boxes', BoundingBoxArray, bbox_array_callback, queue_size=1)
    
    # ROS 1トピックのパブリッシャ
    # visualization_msgs/MarkerArray を発行
    # このトピックを ros1_bridge で ROS 2 に渡します
    g_marker_array_pub = rospy.Publisher('output_marker_array', MarkerArray, queue_size=1)
    
    rospy.loginfo("BoundingBoxArray -> MarkerArray 変換ノードを開始しました。")
    rospy.spin()

if __name__ == '__main__':
    main()
