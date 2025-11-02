from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='jsk_enshu_recognition',
            executable='hand_pose_estimation',
            name='hand_pose_estimation',
            output='screen',
            remappings=[
                ('~/input', '/camera/image_raw'),
            ]
        ),
    ])
