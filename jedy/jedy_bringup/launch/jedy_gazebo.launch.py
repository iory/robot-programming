
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node


def generate_launch_description():
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    gui = LaunchConfiguration('gui', default='true')
    headless = LaunchConfiguration('headless', default='false')
    world_file = LaunchConfiguration('world_file', default=os.path.join(get_package_share_directory('jedy_bringup'), 'worlds', 'empty.world'))
    model_file = LaunchConfiguration('model', default=os.path.join(get_package_share_directory('jedy_description'), 'urdf', 'jedy_no_arm.urdf'))
    rviz_config = LaunchConfiguration('rviz_config', default=os.path.join(get_package_share_directory('jedy_bringup'), 'config', 'jedy.rviz'))
    controllers_config = LaunchConfiguration('controllers_config', default=os.path.join(get_package_share_directory('jedy_bringup'), 'config', 'jedy_controllers.ros2.yaml'))

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': [' -r -v 4 ', world_file], 'on_exit_shutdown': 'true'}.items(),
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
        arguments=['-topic', '/robot_description', '-entity', 'jedy'],
        output='screen'
    )

    control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[robot_description, controllers_config],
        output='screen',
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
    )

    diff_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--controller-manager', '/controller_manager'],
    )

    fullbody_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['fullbody_controller', '--controller-manager', '/controller_manager'],
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen',
        condition=IfCondition(gui)
    )

    depth_renamer = Node(
        package='topic_tools',
        executable='relay',
        arguments=['/camera/depth/points', '/camera/depth_registered/points'],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('headless', default_value='false'),
        DeclareLaunchArgument('world_file', default_value=os.path.join(get_package_share_directory('jedy_bringup'), 'worlds', 'empty.world')),
        DeclareLaunchArgument('model', default_value=os.path.join(get_package_share_directory('jedy_description'), 'urdf', 'jedy_no_arm.urdf')),
        DeclareLaunchArgument('rviz_config', default_value=os.path.join(get_package_share_directory('jedy_bringup'), 'config', 'jedy.rviz')),
        DeclareLaunchArgument('controllers_config', default_value=os.path.join(get_package_share_directory('jedy_bringup'), 'config', 'jedy_controllers.ros2.yaml')),
        gazebo,
        robot_state_publisher,
        spawn_entity,
        control_node,
        joint_state_broadcaster_spawner,
        diff_drive_controller_spawner,
        fullbody_controller_spawner,
        rviz,
        depth_renamer
    ])
