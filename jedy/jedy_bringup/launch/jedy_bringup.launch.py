#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Package directories
    jedy_description_share = FindPackageShare('jedy_description')
    kxr_controller_share = FindPackageShare('kxr_controller')
    jedy_bringup_share = FindPackageShare('jedy_bringup')

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

    publish_sensor_arg = DeclareLaunchArgument(
        'publish_sensor',
        default_value='false',
        description='Publish sensor data'
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

    model_server_port_arg = DeclareLaunchArgument(
        'model_server_port',
        default_value='8123',
        description='Model server port'
    )

    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Robot namespace'
    )

    joint_group_description_arg = DeclareLaunchArgument(
        'joint_group_description',
        default_value='',
        description='Joint group description'
    )

    frame_count_arg = DeclareLaunchArgument(
        'frame_count',
        default_value='1',
        description='Frame count'
    )

    current_limit_arg = DeclareLaunchArgument(
        'current_limit',
        default_value='4.0',
        description='Current limit in Amp'
    )

    temperature_limit_arg = DeclareLaunchArgument(
        'temperature_limit',
        default_value='80',
        description='Temperature limit in celsius'
    )

    read_current_arg = DeclareLaunchArgument(
        'read_current',
        default_value='false',
        description='Read current from servos'
    )

    read_temperature_arg = DeclareLaunchArgument(
        'read_temperature',
        default_value='false',
        description='Read temperature from servos'
    )

    use_fullbody_controller_arg = DeclareLaunchArgument(
        'use_fullbody_controller',
        default_value='true',
        description='Use fullbody controller'
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
            'spawn_controllers': 'false',  # We spawn controllers in this launch file
        }.items()
    )

    # Load mecanum drive controller configuration
    try:
        jedy_bringup_pkg = get_package_share_directory('jedy_bringup')
        controller_config = os.path.join(
            jedy_bringup_pkg,
            'config',
            'jedy_controllers.ros2.yaml'
        )
    except:
        controller_config = PathJoinSubstitution([
            jedy_bringup_share,
            'config',
            'jedy_controllers.ros2.yaml'
        ])

    # Spawn mecanum_drive_controller
    mecanum_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        name='mecanum_drive_controller_spawner',
        arguments=[
            'mecanum_drive_controller',
            '--controller-manager',
            '/controller_manager',
            '--controller-manager-timeout',
            '30'
        ],
        parameters=[controller_config],
        output='screen',
        respawn=True,
        respawn_delay=5.0
    )

    # Relay cmd_vel topic
    # In ROS 2, we use topic remapping instead of relay node
    relay_cmd_vel = Node(
        package='topic_tools',
        executable='relay',
        name='relay_cmd_vel',
        arguments=[
            '/cmd_vel',
            '/mecanum_drive_controller/cmd_vel'
        ],
        output='screen'
    )

    # Relay odom topic
    relay_odom = Node(
        package='topic_tools',
        executable='relay',
        name='relay_odom',
        arguments=[
            '/mecanum_drive_controller/odom',
            '/odom'
        ],
        output='screen'
    )

    # Relay velocity_command_joint_state topic
    relay_velocity = Node(
        package='topic_tools',
        executable='relay',
        name='relay_velocity',
        arguments=[
            '/velocity_command_joint_state_from_robot_hardware',
            '/velocity_command_joint_state'
        ],
        output='screen'
    )

    return LaunchDescription([
        # Arguments
        urdf_path_arg,
        servo_config_path_arg,
        publish_imu_arg,
        publish_sensor_arg,
        publish_battery_voltage_arg,
        use_rcb4_arg,
        device_arg,
        model_server_port_arg,
        namespace_arg,
        joint_group_description_arg,
        frame_count_arg,
        current_limit_arg,
        temperature_limit_arg,
        read_current_arg,
        read_temperature_arg,
        use_fullbody_controller_arg,

        # Nodes and includes
        kxr_controller_launch,
        mecanum_drive_controller_spawner,
        relay_cmd_vel,
        relay_odom,
        relay_velocity,
    ])
