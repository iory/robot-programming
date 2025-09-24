import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node


def generate_launch_description():
    # Resource paths
    pkg_jedy_description = get_package_share_directory('jedy_description')
    
    # URDF file
    urdf_file = os.path.join(pkg_jedy_description, 'urdf', 'jedy_four_dof.urdf')

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'verbose': 'true'}.items(),
    )

    # Robot description
    robot_description = {'robot_description': Command(['xacro ', urdf_file])}

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )

    # Spawn entity
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', '/robot_description', 
                   '-entity', 'jedy',
                   '-x', '0',
                   '-y', '0',
                   '-z', '0.2'],
        output='screen'
    )

    # Joint state publisher GUI for manual control
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )

    # Bridge for clock
    bridge_clock = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    # Bridge for joint states - try multiple possible topic names
    bridge_joint_states = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/model/jedy/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        remappings=[
            ('/model/jedy/joint_state', '/joint_states')
        ],
        output='screen'
    )

    # Alternative joint state publisher (if Gazebo bridge doesn't work)
    # This will publish zero joint states to keep TF tree alive
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen',
        parameters=[{'use_gui': False}]
    )

    return LaunchDescription([
        SetEnvironmentVariable(name='LIBGL_ALWAYS_SOFTWARE', value='1'),
        SetEnvironmentVariable(name='OGRE_RTT_MODE', value='Copy'),
        
        gazebo,
        robot_state_publisher,
        spawn_entity,
        bridge_clock,
        bridge_joint_states,
        joint_state_publisher_gui,  # This will publish joint states manually
    ])