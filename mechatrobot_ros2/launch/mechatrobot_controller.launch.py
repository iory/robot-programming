from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Get package directories
    pkg_share = FindPackageShare('mechatrobot_ros2')

    # Paths
    urdf_file = PathJoinSubstitution([pkg_share, 'urdf', 'robot.urdf'])

    # Robot control node
    robot_control_node = Node(
        package='mechatrobot_ros2',
        executable='robot_control',
        name='robot_control',
        output='screen'
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': urdf_file
        }],
        respawn=True
    )

    # Static transform publisher (map to base_link)
    static_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_base',
        arguments=['-0.2', '0', '0', '3.1415', '0', '0', '/map', '/base_link']
    )

    return LaunchDescription([
        robot_control_node,
        robot_state_publisher,
        static_tf_node,
    ])
