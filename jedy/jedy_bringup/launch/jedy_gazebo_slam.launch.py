import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Get the launch directory
    pkg_jedy_bringup = get_package_share_directory('jedy_bringup')

    # Create the launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Declare the launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    # Include Gazebo launch
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_jedy_bringup, 'launch', 'jedy_gazebo.launch.py')
        )
    )

    # Include SLAM launch with delay
    slam_launch = TimerAction(
        period=10.0,  # Wait 10 seconds for Gazebo to stabilize
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_jedy_bringup, 'launch', 'jedy_slam.launch.py')
                )
            )
        ]
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_use_sim_time_cmd)

    # Add the actions to launch Gazebo and SLAM with delay
    ld.add_action(gazebo_launch)
    ld.add_action(slam_launch)

    return ld
