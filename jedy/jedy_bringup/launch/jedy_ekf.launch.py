import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Get the launch directory
    pkg_jedy_bringup = get_package_share_directory('jedy_bringup')

    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    ekf_config_file = LaunchConfiguration(
        'ekf_config',
        default=os.path.join(
            pkg_jedy_bringup,
            'config',
            'ekf.yaml'
        )
    )

    # Declare the launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_ekf_config_cmd = DeclareLaunchArgument(
        'ekf_config',
        default_value=os.path.join(
            pkg_jedy_bringup,
            'config',
            'ekf.yaml'
        ),
        description='Full path to the EKF config file'
    )

    # Start robot_localization EKF node
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config_file, {'use_sim_time': use_sim_time}]
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_ekf_config_cmd)

    # Add the nodes
    ld.add_action(ekf_node)

    return ld
