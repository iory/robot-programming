from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    """
    指定された ros2 run コマンドと等価なローンチ記述を生成する。
    - パッケージ: teleop_twist_keyboard
    - 実行ファイル: teleop_twist_keyboard
    - リマップ: cmd_vel -> /mecanum_drive_controller/reference
    - パラメータ: stamped -> True
    - ターミナルを割り当て (prefix)
    """
    
    keyboard_teleop_node = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='keyboard_teleop',     # ノード名はlaunchファイル内で任意に設定できます
        output='screen',
        
        # 
        # 🚨 最も重要な設定: ターミナルを割り当てる
        #
        # `ros2 run` は自動でターミナルに接続しますが、
        # `ros2 launch` は自動では接続しません。
        # これがないと termios.error (25) が発生します。
        prefix='gnome-terminal --',
        # (もし xterm がなければ 'gnome-terminal --' なども使えます)
        #
        
        #
        # 1. リマッピングの設定 (--remap ... と等価)
        #
        remappings=[
            ('cmd_vel', '/mecanum_drive_controller/reference')
        ],
        
        #
        # 2. パラメータの設定 ( -p stamped:=true と等価)
        #
        parameters=[
            {'stamped': True}
        ]
    )
    
    return LaunchDescription([
        keyboard_teleop_node
    ])
