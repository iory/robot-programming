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
- gazebo_ros (for simulation)
- joint_state_publisher_gui (for Gazebo simulation)

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

```bash
ros2 launch mechatrobot_ros2 mechatrobot_display.launch.py
```

### Face detection demo

```bash
ros2 launch mechatrobot_ros2 sample_face_detect.launch.py
ros2 run mechatrobot_ros2 motor-command-by-face.py
```

### Launch in Gazebo simulation

```bash
ros2 launch mechatrobot_ros2 gazebo.launch.py
```

This will:
- Start Gazebo simulator
- Spawn the mechatrobot model
- Launch robot_state_publisher
- Open joint_state_publisher_gui for manual joint control
- Start RViz2 for robot visualization
- Launch LED controller node

You can control the joint1 angle using the GUI slider.

### LED Control

The LED controller node subscribes to `/led/state` topic and publishes color commands. To control the LED:

```bash
# Turn LED ON (Red)
ros2 topic pub /led/state std_msgs/msg/Bool "data: true"

# Turn LED OFF (Gray)
ros2 topic pub /led/state std_msgs/msg/Bool "data: false"
```

The LED state will be reflected in both Gazebo and RViz2 visualizations through the `/led_color` topic.

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
