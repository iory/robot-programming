#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Package directories
    jedy_description_share = FindPackageShare('jedy_description')
    jedy_bringup_share = FindPackageShare('jedy_bringup')
    kxr_controller_share = FindPackageShare('kxr_controller')

    # Declare launch arguments
    urdf_path_arg = DeclareLaunchArgument(
        'urdf_path',
        default_value=PathJoinSubstitution([
            jedy_description_share,
            'urdf',
            'jedy_gz.xacro'
        ]),
        description='Path to URDF file'
    )

    servo_config_path_arg = DeclareLaunchArgument(
        'servo_config_path',
        default_value=PathJoinSubstitution([
            jedy_description_share,
            'config',
            'jedy_servo_config.yaml'
        ]),
        description='Path to servo configuration YAML file'
    )

    publish_imu_arg = DeclareLaunchArgument(
        'publish_imu',
        default_value='true',
        description='Publish IMU data'
    )

    publish_battery_voltage_arg = DeclareLaunchArgument(
        'publish_battery_voltage',
        default_value='false',
        description='Publish battery voltage'
    )

    use_rcb4_arg = DeclareLaunchArgument(
        'use_rcb4',
        default_value='false',
        description='Flag to use RCB4 mini board'
    )

    device_arg = DeclareLaunchArgument(
        'device',
        default_value='',
        description='Device path'
    )

    # Include kxr_controller launch file
    kxr_controller_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                kxr_controller_share,
                'launch',
                'rcb4_ros_bridge.launch.py'
            ])
        ]),
        launch_arguments={
            'urdf_path': LaunchConfiguration('urdf_path'),
            'servo_config_path': LaunchConfiguration('servo_config_path'),
            'use_rcb4': LaunchConfiguration('use_rcb4'),
            'device': LaunchConfiguration('device'),
            'publish_imu': LaunchConfiguration('publish_imu'),
            'publish_battery_voltage': LaunchConfiguration('publish_battery_voltage'),
            'spawn_controllers': 'false',
            'use_fullbody_controller': 'false',  # Use individual controllers
        }.items()
    )

    # Spawn mecanum_drive_controller
    spawn_mecanum_controller = ExecuteProcess(
        cmd=[
            'ros2', 'control', 'load_controller', '--set-state', 'active',
            'mecanum_drive_controller',
            '--controller-manager', '/controller_manager',
            '--param-file', PathJoinSubstitution([
                jedy_bringup_share,
                'config',
                'jedy_controllers.ros2.yaml'
            ])
        ],
        output='screen'
    )

    return LaunchDescription([
        urdf_path_arg,
        servo_config_path_arg,
        publish_imu_arg,
        publish_battery_voltage_arg,
        use_rcb4_arg,
        device_arg,
        kxr_controller_launch,
        spawn_mecanum_controller,
    ])
