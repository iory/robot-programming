
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node


def generate_launch_description():
    # Set Gazebo resource path
    pkg_jedy_bringup = get_package_share_directory('jedy_bringup')
    model_path = os.path.join(pkg_jedy_bringup, 'worlds', 'model')
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        gz_resource_path = os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + model_path
    else:
        gz_resource_path = model_path

    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    gui = LaunchConfiguration('gui', default='true')
    headless = LaunchConfiguration('headless', default='false')
    
    model_file = LaunchConfiguration('model', default=os.path.join(get_package_share_directory('jedy_description'), 'urdf', 'jedy_no_arm.urdf'))
    controllers_config = LaunchConfiguration('controllers_config', default=os.path.join(get_package_share_directory('jedy_bringup'), 'config', 'jedy_controllers.ros2.yaml'))

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'on_exit_shutdown': 'true'}.items(),
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
        parameters=[controllers_config],
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

    return LaunchDescription([
        SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=gz_resource_path),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('headless', default_value='false'),
        
        DeclareLaunchArgument('model', default_value=os.path.join(get_package_share_directory('jedy_description'), 'urdf', 'jedy_no_arm.urdf')),
        DeclareLaunchArgument('controllers_config', default_value=os.path.join(get_package_share_directory('jedy_bringup'), 'config', 'jedy_controllers.ros2.yaml')),
        gazebo,
        robot_state_publisher,
        spawn_entity,
        control_node,
        joint_state_broadcaster_spawner,
        diff_drive_controller_spawner,
        fullbody_controller_spawner,
    ])
