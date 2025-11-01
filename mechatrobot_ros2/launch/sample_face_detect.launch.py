from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Declare arguments
    debug_view_arg = DeclareLaunchArgument(
        'debug_view',
        default_value='true',
        description='Enable debug view for face detection'
    )

    # USB camera node
    usb_cam_node = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name='usb_cam',
        parameters=[{
            'framerate': 10.0,
            'pixel_format': 'yuyv',
        }],
        output='screen'
    )

    # Face detection launch (opencv_apps)
    # Note: You may need to check if opencv_apps has ROS2 support
    # or use alternative face detection packages like vision_opencv
    opencv_apps_share = FindPackageShare('opencv_apps')
    face_detection_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([opencv_apps_share, 'launch', 'face_detection.launch.py'])
        ]),
        launch_arguments={
            'image': '/usb_cam/image_raw',
            'debug_view': LaunchConfiguration('debug_view'),
            'face_cascade_name': '/usr/share/opencv4/haarcascades/haarcascade_frontalface_alt.xml',
            'eyes_cascade_name': '/usr/share/opencv4/haarcascades/haarcascade_eye_tree_eyeglasses.xml',
        }.items()
    )

    return LaunchDescription([
        debug_view_arg,
        usb_cam_node,
        face_detection_launch,
    ])
