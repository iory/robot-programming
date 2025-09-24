import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node


def generate_launch_description():
    # Set Gazebo resource path
    pkg_jedy_bringup = get_package_share_directory('jedy_bringup')
    pkg_jedy_description = get_package_share_directory('jedy_description')
    model_path = os.path.join(pkg_jedy_bringup, 'worlds', 'model')

    # Resource paths for Gazebo
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

    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    gui = LaunchConfiguration('gui', default='true')
    headless = LaunchConfiguration('headless', default='false')
    
    model_file = LaunchConfiguration('model', default=os.path.join(get_package_share_directory('jedy_description'), 'urdf', 'jedy_four_dof.urdf'))

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={
            'verbose': 'true',
            'on_exit_shutdown': 'true'
        }.items(),
    )

    # Robot description
    robot_description = {'robot_description': Command(['xacro ', model_file])}

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time}]
    )

    # Spawn entity in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', '/robot_description', 
                   '-entity', 'jedy',
                   '-x', '0',
                   '-y', '0',
                   '-z', '0.5'],
        output='screen'
    )

    # Gazebo-ROS bridge for joint states
    bridge_joint_states = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/world/default/model/jedy/joint_state@sensor_msgs/msg/JointState@gz.msgs.Model'
        ],
        remappings=[
            ('/world/default/model/jedy/joint_state', '/joint_states')
        ],
        output='screen'
    )

    # Gazebo-ROS bridge for clock
    bridge_clock = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    # Joint state publisher (publishes joint positions to Gazebo)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen'
    )

    # Optional: Joint state publisher GUI for manual control
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen',
        condition=LaunchConfiguration('use_gui', default='false').perform(None) == 'true'
    )

    # RViz
    rviz_config_file = os.path.join(pkg_jedy_bringup, 'config', 'jedy_gazebo.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file] if os.path.exists(rviz_config_file) else [],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=gz_resource_path),
        SetEnvironmentVariable(name='LIBGL_ALWAYS_SOFTWARE', value='1'),
        SetEnvironmentVariable(name='OGRE_RTT_MODE', value='Copy'),
        
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('headless', default_value='false'),
        DeclareLaunchArgument('use_gui', default_value='false', description='Use joint state publisher GUI'),
        
        DeclareLaunchArgument('model', default_value=os.path.join(get_package_share_directory('jedy_description'), 'urdf', 'jedy_four_dof.urdf')),
        
        gazebo,
        robot_state_publisher,
        spawn_entity,
        bridge_joint_states,
        bridge_clock,
        joint_state_publisher,
        joint_state_publisher_gui,
        rviz,
    ])