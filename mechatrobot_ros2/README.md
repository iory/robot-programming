# mechatrobot_ros2

ROS2 version of the mechatrobot package.

## Overview

This package provides ROS2 control interface for the mechatrobot platform. It includes:

- Hardware interface for motor control
- ROS2 controllers configuration
- Launch files for different use cases
- Face detection based motor command script

## Dependencies

- ROS2 (Humble or later recommended)
- ros2_control
- controller_manager
- joint_state_broadcaster
- joint_trajectory_controller
- micro_ros_agent (replaces rosserial for ROS2)
- usb_cam
- opencv_apps (if available for ROS2)
- joint_state_publisher_gui
- rviz2

## Installation

```bash
cd ~/ros2_ws/src
colcon build --packages-select mechatrobot_ros2
source install/setup.bash
```

## Usage

### Launch the robot driver

```bash
ros2 launch mechatrobot_ros2 mechatrobot_driver.launch.py port:=/dev/ttyUSB0
```

### Launch the robot controller

```bash
ros2 launch mechatrobot_ros2 mechatrobot_controller.launch.py
```

### Launch the display (RViz2)

RViz2でロボットモデルを表示し、GUIでジョイント角度を制御：

```bash
ros2 launch mechatrobot_ros2 display.launch.py
```

This launches:
- RViz2 for visualization
- Joint State Publisher GUI for manual joint control
- LED controller for LED state visualization

You can control the joint1 angle using the GUI slider.

### Face detection demo

```bash
ros2 launch mechatrobot_ros2 sample_face_detect.launch.py
ros2 run mechatrobot_ros2 motor-command-by-face.py
```

### LED Control

The LED controller node provides simple ON/OFF control with fixed colors:

```bash
# Turn LED ON (Orange)
ros2 topic pub /led/state std_msgs/msg/Bool "data: true"

# Turn LED OFF (Gray)
ros2 topic pub /led/state std_msgs/msg/Bool "data: false"
```

The LED state will be reflected in RViz2 visualization:
- **RViz2**: Displays a Marker (sphere) at the LED position with the corresponding color on `/led_marker` topic

The LED Marker in RViz2 appears as a small sphere overlaid on the robot model at the LED link position:
- **ON**: Orange (R=1.0, G=0.5, B=0.0)
- **OFF**: Dark Gray (R=0.3, G=0.3, B=0.3)

## Migration from ROS1

This package is migrated from the original `mechatrobot` ROS1 package. Key changes:

1. **rosserial → micro_ros_agent**: Arduino communication now uses micro-ROS instead of rosserial
2. **XML launch → Python launch**: All launch files converted to Python format
3. **ros_control → ros2_control**: Hardware interface migrated to ROS2 control framework
4. **rospy → rclpy**: Python scripts updated to use rclpy API
5. **tf → tf2**: Static transforms now use tf2_ros

## Notes

- The original `mechatrobot` package is preserved and remains available
- Some dependencies (like opencv_apps) may need ROS2 versions or alternatives
- Controller configuration format has been updated for ROS2
