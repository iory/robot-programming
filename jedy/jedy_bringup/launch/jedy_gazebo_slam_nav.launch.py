import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Get package directories
    pkg_jedy_bringup = get_package_share_directory('jedy_bringup')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    slam_params_file = os.path.join(pkg_jedy_bringup, 'config', 'nav2', 'slam_params.yaml')

    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    # 1. Launch Gazebo with robot
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_jedy_bringup, 'launch', 'jedy_gazebo.launch.py')
        )
    )

    # 2. Launch SLAM after Gazebo stabilizes
    slam_launch = TimerAction(
        period=15.0,  # Wait 15 seconds for Gazebo and controllers to be ready
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_nav2_bringup, 'launch', 'slam_launch.py')
                ),
                launch_arguments={
                    'use_sim_time': 'true',
                    'params_file': slam_params_file,
                }.items()
            )
        ]
    )

    # 3. Launch Nav2 navigation stack after SLAM
    navigation_launch = TimerAction(
        period=20.0,  # Wait 20 seconds for SLAM to initialize
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')
                ),
                launch_arguments={
                    'use_sim_time': 'true',
                }.items()
            )
        ]
    )

    # Create the launch description
    ld = LaunchDescription()

    # Add actions
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(gazebo_launch)
    ld.add_action(slam_launch)
    ld.add_action(navigation_launch)

    return ld
