import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node


def generate_launch_description():
    # Set Gazebo resource path
    pkg_jedy_bringup = get_package_share_directory('jedy_bringup')
    pkg_jedy_description = get_package_share_directory('jedy_description')
    model_path = os.path.join(pkg_jedy_bringup, 'worlds', 'model')

    # ':' で区切られた複数のパスを設定
    resource_paths = [model_path, os.path.dirname(pkg_jedy_description)]

    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        gz_resource_path = os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + ':'.join(resource_paths)
    else:
        gz_resource_path = ':'.join(resource_paths)

    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    model_file = os.path.join(get_package_share_directory('jedy_bringup'), 'urdf', 'jedy_no_arm_gz.xacro')

    # Gazebo with safer settings
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={
            'gz_args': '-r empty.sdf',
            'on_exit_shutdown': 'true',
        }.items(),
    )

    # Robot description
    robot_description = {'robot_description': Command(['xacro ', model_file])}

    # Nodes
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time}]
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', '/robot_description', '-entity', 'jedy', '-z', '0.2'],
        output='screen'
    )

    # Wait for Gazebo to be ready before spawning controllers
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    mecanum_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['mecanum_drive_controller', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    head_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['head_controller', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    # Delay controller spawners to ensure gz_ros2_control is ready
    delayed_joint_state_broadcaster = TimerAction(
        period=3.0,
        actions=[joint_state_broadcaster_spawner]
    )

    delayed_mecanum_controller = TimerAction(
        period=5.0,
        actions=[mecanum_drive_controller_spawner]
    )

    delayed_head_controller = TimerAction(
        period=7.0,
        actions=[head_controller_spawner]
    )

    return LaunchDescription([
        SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=gz_resource_path),
        SetEnvironmentVariable(name='DISPLAY', value=':1'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        gazebo,
        robot_state_publisher,
        spawn_entity,
        delayed_joint_state_broadcaster,
        delayed_mecanum_controller,
        delayed_head_controller,
    ])
