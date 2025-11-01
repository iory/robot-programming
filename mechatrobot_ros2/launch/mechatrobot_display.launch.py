from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Get package directories
    pkg_share = FindPackageShare('mechatrobot_ros2')

    # RViz config path
    rviz_config = PathJoinSubstitution([pkg_share, 'config', 'robot.rviz'])

    # RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen'
    )

    # Note: rqt_joint_trajectory_controller may not be available in ROS2
    # You can use rqt or other GUI tools for joint control

    return LaunchDescription([
        rviz_node,
    ])
