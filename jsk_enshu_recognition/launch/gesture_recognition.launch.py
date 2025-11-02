from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='jsk_enshu_recognition',
            executable='gesture_recognition',
            name='gesture_recognition',
            output='screen',
            parameters=[{
                'model_path': PathJoinSubstitution([
                    FindPackageShare('jsk_enshu_recognition'),
                    'config',
                    'keypoint_classifier.tflite'
                ]),
                'label_csv': PathJoinSubstitution([
                    FindPackageShare('jsk_enshu_recognition'),
                    'config',
                    'keypoint_classifier_label.csv'
                ]),
            }],
            remappings=[
                ('~/input', '/camera/image_raw'),
            ]
        ),
    ])
