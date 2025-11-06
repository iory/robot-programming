#!/usr/bin/env python3
"""
Complete SLAM demo for JEDY robot in Gazebo simulation.

This launch file brings up:
1. Gazebo simulation with JEDY robot (with LiDAR and IMU sensors)
2. SLAM Toolbox for mapping
3. RViz2 for visualization

Usage:
    ros2 launch jedy_bringup jedy_gazebo_slam_demo.launch.py

After launching:
- The robot will appear in Gazebo with all sensors active
- SLAM Toolbox will start building a map based on LiDAR data
- RViz2 will show the robot, sensor data, and the map being built
- You can teleoperate the robot to explore and build the map:
    ros2 run teleop_twist_keyboard teleop_twist_keyboard
  or
    ros2 launch jedy_bringup keyboard_teleop.launch.py

To save the map:
    ros2 run nav2_map_server map_saver_cli -f <map_name>
"""

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Get the launch directory
    pkg_jedy_bringup = get_package_share_directory('jedy_bringup')

    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Declare the launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # Launch Gazebo with JEDY robot
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_jedy_bringup, 'launch', 'jedy_gazebo.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time
        }.items()
    )

    # Launch SLAM Toolbox
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_jedy_bringup, 'launch', 'jedy_slam.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time
        }.items()
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_use_sim_time_cmd)

    # Add the actions to launch all nodes
    ld.add_action(gazebo_launch)
    ld.add_action(slam_launch)

    return ld
