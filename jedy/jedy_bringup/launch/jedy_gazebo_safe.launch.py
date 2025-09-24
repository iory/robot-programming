import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, ExecuteProcess
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node


def generate_launch_description():
    # Set Gazebo resource path
    pkg_jedy_bringup = get_package_share_directory('jedy_bringup')
    pkg_jedy_description = get_package_share_directory('jedy_description')
    model_path = os.path.join(pkg_jedy_bringup, 'worlds', 'model')

    # Add multiple paths for Gazebo to find resources
    resource_paths = [
        model_path,
        os.path.dirname(pkg_jedy_description),
        pkg_jedy_description,
        os.path.join(pkg_jedy_description, 'meshes')
    ]

    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        gz_resource_path = os.environ['GZ_SIM_RESOURCE_PATH'] + ':' + ':'.join(resource_paths)
    else:
        gz_resource_path = ':'.join(resource_paths)
    
    # Also set IGN_GAZEBO_RESOURCE_PATH for compatibility
    ign_resource_path = gz_resource_path

    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    gui = LaunchConfiguration('gui', default='true')
    headless = LaunchConfiguration('headless', default='false')
    
    model_file = LaunchConfiguration('model', default=os.path.join(get_package_share_directory('jedy_description'), 'urdf', 'jedy_four_dof.urdf'))
    controllers_config = LaunchConfiguration('controllers_config', default=os.path.join(get_package_share_directory('jedy_bringup'), 'config', 'jedy_mecanum_controllers.ros2.yaml'))

    # Start Gazebo with safer physics parameters
    gazebo_cmd = [
        'ign', 'gazebo', 
        '--physics-engine', 'ignition-physics-dartsim-plugin',
        '--physics-update-rate', '500',  # Lower update rate
        '--render-engine', 'ogre2'
    ]
    
    gazebo_process = ExecuteProcess(
        cmd=gazebo_cmd,
        output='screen',
        additional_env={
            'GZ_SIM_RESOURCE_PATH': gz_resource_path,
            'IGN_GAZEBO_RESOURCE_PATH': ign_resource_path,
            'LIBGL_ALWAYS_SOFTWARE': '1',
            'OGRE_RTT_MODE': 'Copy'
        }
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
        arguments=['-topic', '/robot_description', 
                   '-entity', 'jedy',
                   '-x', '0',
                   '-y', '0', 
                   '-z', '0.5'],  # Spawn higher to avoid ground collision
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

    mecanum_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['mecanum_drive_controller', '--controller-manager', '/controller_manager'],
    )

    return LaunchDescription([
        SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=gz_resource_path),
        SetEnvironmentVariable(name='IGN_GAZEBO_RESOURCE_PATH', value=ign_resource_path),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('headless', default_value='false'),
        
        DeclareLaunchArgument('model', default_value=os.path.join(get_package_share_directory('jedy_description'), 'urdf', 'jedy_four_dof.urdf')),
        DeclareLaunchArgument('controllers_config', default_value=os.path.join(get_package_share_directory('jedy_bringup'), 'config', 'jedy_mecanum_controllers.ros2.yaml')),
        gazebo_process,
        robot_state_publisher,
        spawn_entity,
        control_node,
        joint_state_broadcaster_spawner,
        mecanum_drive_controller_spawner,
    ])