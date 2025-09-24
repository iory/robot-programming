import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # Resource paths
    pkg_jedy_bringup = get_package_share_directory('jedy_bringup')
    
    # Gazebo-compatible URDF file
    urdf_file = os.path.join(pkg_jedy_bringup, 'urdf', 'jedy_gazebo_compatible.urdf')

    # Gazebo - just use default empty world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'verbose': 'true'}.items(),
    )

    # Robot description
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()
    
    robot_description = {'robot_description': robot_desc}

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )

    # Add ground plane manually
    add_ground = ExecuteProcess(
        cmd=[
            'ign', 'service', '-s', '/world/default/create',
            '--reqtype', 'gz.msgs.EntityFactory',
            '--reptype', 'gz.msgs.Boolean',
            '--timeout', '5000',
            '--req', 'sdf: "' + 
            '<sdf version=\\"1.6\\"><model name=\\"ground\\"><static>true</static>' +
            '<link name=\\"ground_link\\"><collision name=\\"ground_collision\\">' +
            '<geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry>' +
            '</collision><visual name=\\"ground_visual\\">' +
            '<geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry>' +
            '<material><ambient>0.8 0.8 0.8 1</ambient><diffuse>0.8 0.8 0.8 1</diffuse></material>' +
            '</visual></link></model></sdf>", name: "ground"'
        ],
        output='screen'
    )

    # Spawn robot entity - higher position
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', '/robot_description', 
                   '-entity', 'jedy',
                   '-x', '0',
                   '-y', '0',
                   '-z', '0.20'],  # Higher position to ensure clearance
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

    return LaunchDescription([
        SetEnvironmentVariable(name='LIBGL_ALWAYS_SOFTWARE', value='1'),
        SetEnvironmentVariable(name='OGRE_RTT_MODE', value='Copy'),
        
        gazebo,
        robot_state_publisher,
        add_ground,  # Add ground first
        spawn_entity,
        bridge_clock,
        joint_state_publisher_gui,
    ])