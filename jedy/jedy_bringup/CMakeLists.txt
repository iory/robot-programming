cmake_minimum_required(VERSION 3.5)
project(jedy_bringup)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY urdf
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY euslisp
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY kadai
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY scripts
  DESTINATION share/${PROJECT_NAME}
)

# Install Python executables
install(
  PROGRAMS
    scripts/joint_command_relay.py
    scripts/head_trajectory_sample.py
    scripts/twist_stamper.py
    scripts/mecanum_teleop_keyboard.py
    scripts/odom_to_tf.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
