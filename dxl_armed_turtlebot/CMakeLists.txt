cmake_minimum_required(VERSION 2.8.3)
project(dxl_armed_turtlebot)

find_package(catkin REQUIRED COMPONENTS rostest)

catkin_package()

add_rostest(test/test-dxl-armed-turtlebot.test)
