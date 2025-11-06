import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    camera_namespace = LaunchConfiguration('camera', default='camera')
    remote_namespace = LaunchConfiguration('remote', default='remote')

    # Decompress color image (compressed -> raw)
    color_republish = Node(
        package='image_transport',
        executable='republish',
        name='color_republish',
        arguments=['compressed', 'raw'],
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
        ],
        remappings=[
            ('in', [camera_namespace, '/color/image_rect_raw']),
            ('out', [remote_namespace, '/color/image_rect_raw']),
        ]
    )

    # Relay color camera_info
    color_info_relay = Node(
        package='topic_tools',
        executable='relay',
        name='color_info_relay',
        arguments=[
            [camera_namespace, '/color/camera_info'],
            [remote_namespace, '/color/camera_info']
        ],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Decompress depth image (compressedDepth -> raw)
    depth_republish = Node(
        package='image_transport',
        executable='republish',
        name='depth_republish',
        arguments=['compressedDepth', 'raw'],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        remappings=[
            ('in', [camera_namespace, '/depth/image_rect_raw']),
            ('out', [remote_namespace, '/depth/image_rect_raw']),
        ]
    )

    # Relay depth camera_info
    depth_info_relay = Node(
        package='topic_tools',
        executable='relay',
        name='depth_info_relay',
        arguments=[
            [camera_namespace, '/depth/camera_info'],
            [remote_namespace, '/depth/camera_info']
        ],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Decompress aligned depth image (compressedDepth -> raw)
    aligned_depth_republish = Node(
        package='image_transport',
        executable='republish',
        name='aligned_depth_republish',
        arguments=['compressedDepth', 'raw'],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        remappings=[
            ('in', [camera_namespace, '/aligned_depth_to_color/image_raw']),
            ('out', [remote_namespace, '/aligned_depth_to_color/image_raw']),
        ]
    )

    # Relay aligned depth camera_info
    aligned_info_relay = Node(
        package='topic_tools',
        executable='relay',
        name='aligned_info_relay',
        arguments=[
            [camera_namespace, '/aligned_depth_to_color/camera_info'],
            [remote_namespace, '/aligned_depth_to_color/camera_info']
        ],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Point cloud generation from RGB + Aligned Depth
    point_cloud_xyzrgb = Node(
        package='depth_image_proc',
        executable='point_cloud_xyzrgb_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        remappings=[
            ('rgb/image_rect_color', [remote_namespace, '/color/image_rect_raw']),
            ('rgb/camera_info', [remote_namespace, '/color/camera_info']),
            ('depth_registered/image_rect', [remote_namespace, '/aligned_depth_to_color/image_raw']),
            ('depth_registered/camera_info', [remote_namespace, '/aligned_depth_to_color/camera_info']),
            ('points', [remote_namespace, '/depth/color/points']),
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time if true'
        ),
        DeclareLaunchArgument(
            'camera',
            default_value='camera',
            description='Namespace of input (compressed) topics'
        ),
        DeclareLaunchArgument(
            'remote',
            default_value='remote',
            description='Namespace of output (raw) topics'
        ),
        color_republish,
        color_info_relay,
        depth_republish,
        depth_info_relay,
        aligned_depth_republish,
        aligned_info_relay,
        point_cloud_xyzrgb,
    ])
