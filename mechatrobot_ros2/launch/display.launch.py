import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Get package directories
    pkg_mechatrobot_ros2 = get_package_share_directory('mechatrobot_ros2')

    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    # URDF file path
    urdf_file = os.path.join(pkg_mechatrobot_ros2, 'urdf', 'robot.urdf')

    # Read URDF file
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_desc
        }]
    )

    # Joint state publisher GUI (for manual control)
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # RViz2 configuration
    rviz_config = os.path.join(pkg_mechatrobot_ros2, 'config', 'robot.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # LED controller node
    led_controller = Node(
        package='mechatrobot_ros2',
        executable='led_controller.py',
        name='led_controller',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz_node,
        led_controller,
    ])
