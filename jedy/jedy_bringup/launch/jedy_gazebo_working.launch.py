import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # Resource paths
    pkg_jedy_bringup = get_package_share_directory('jedy_bringup')
    pkg_jedy_description = get_package_share_directory('jedy_description')
    
    # Use the actual jedy URDF file with meshes
    urdf_file = os.path.join(pkg_jedy_description, 'urdf', 'jedy_four_dof.urdf')

    # Gazebo with default world (with ground plane)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={
            'verbose': 'true',
            'gz_args': 'empty.sdf'
        }.items(),
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

    # Spawn entity using SDF file directly
    sdf_file = os.path.join(pkg_jedy_description, 'urdf', 'jedy_four_dof.sdf')
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-file', sdf_file,
                   '-entity', 'jedy',
                   '-x', '0',
                   '-y', '0',
                   '-z', '0.15'],  # Adjusted height so wheels touch ground
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

    # Bridge for joint states (Gazebo -> ROS2)  
    bridge_joint_states = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/model/jedy/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        remappings=[
            ('/model/jedy/joint_state', '/joint_states_gazebo')
        ],
        output='screen'
    )
    
    # Bridge for joint commands (ROS2 -> Gazebo)
    bridge_joint_commands = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/world/default/model/jedy/joint/rarm_joint0/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double',
            '/world/default/model/jedy/joint/larm_joint0/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double',
            '/world/default/model/jedy/joint/head_joint0/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double',
            '/world/default/model/jedy/joint/mechanum_joint1/cmd_vel@std_msgs/msg/Float64]gz.msgs.Double',
            '/world/default/model/jedy/joint/mechanum_joint2/cmd_vel@std_msgs/msg/Float64]gz.msgs.Double',
            '/world/default/model/jedy/joint/mechanum_joint3/cmd_vel@std_msgs/msg/Float64]gz.msgs.Double',
            '/world/default/model/jedy/joint/mechanum_joint4/cmd_vel@std_msgs/msg/Float64]gz.msgs.Double',
        ],
        output='screen'
    )

    # Joint command relay - converts /joint_states to individual joint commands
    joint_relay_script = os.path.join(pkg_jedy_bringup, 'scripts', 'joint_command_relay.py')
    joint_command_relay = ExecuteProcess(
        cmd=['python3', joint_relay_script],
        output='screen'
    )

    return LaunchDescription([
        SetEnvironmentVariable(name='LIBGL_ALWAYS_SOFTWARE', value='1'),
        SetEnvironmentVariable(name='OGRE_RTT_MODE', value='Copy'),
        SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=pkg_jedy_description),
        
        gazebo,
        robot_state_publisher,
        spawn_entity,
        bridge_clock,
        bridge_joint_states,
        bridge_joint_commands,
        joint_command_relay,
        joint_state_publisher_gui,
    ])