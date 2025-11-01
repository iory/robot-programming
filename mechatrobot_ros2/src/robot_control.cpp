/*********************************************************************
 * Software License Agreement (BSD License)
 *
 *  Copyright (c) 2008, Willow Garage, Inc.
 *  All rights reserved.
 *
 *  Modified 2020, by Kei OKada and Yuki Asano
 *  Modified 2025, for ROS2 migration and ros2_control integration
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *   * Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer in the documentation and/or other materials provided
 *     with the distribution.
 *   * Neither the name of the Willow Garage nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 *  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 *  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 *  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 *  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 *  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 *  ANY WAY OUT OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF DAMAGE.
 *********************************************************************/
#include <chrono>
#include <memory>
#include <string>
#include <vector>

#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/state.hpp"
#include "std_msgs/msg/int64.hpp"

using namespace std::chrono_literals;

namespace mechatrobot_hardware
{

class MechatrobotSystemHardware : public hardware_interface::SystemInterface
{
public:
  RCLCPP_SHARED_PTR_DEFINITIONS(MechatrobotSystemHardware)

  hardware_interface::CallbackReturn on_init(
    const hardware_interface::HardwareInfo & info) override
  {
    if (hardware_interface::SystemInterface::on_init(info) !=
        hardware_interface::CallbackReturn::SUCCESS)
    {
      return hardware_interface::CallbackReturn::ERROR;
    }

    // Initialize joint data structures
    hw_commands_.resize(info_.joints.size(), 0.0);
    hw_positions_.resize(info_.joints.size(), 0.0);
    hw_velocities_.resize(info_.joints.size(), 0.0);
    hw_efforts_.resize(info_.joints.size(), 0.0);

    // Store joint names
    for (const auto & joint : info_.joints)
    {
      joint_names_.push_back(joint.name);
    }

    return hardware_interface::CallbackReturn::SUCCESS;
  }

  hardware_interface::CallbackReturn on_configure(
    const rclcpp_lifecycle::State & /*previous_state*/) override
  {
    // Create ROS2 node for communication
    node_ = rclcpp::Node::make_shared("mechatrobot_hardware_interface");

    // Create publishers and subscribers for each joint
    for (size_t i = 0; i < info_.joints.size(); i++)
    {
      std::string motor_name = "motor" + std::to_string(i + 1);

      // Publisher for commands
      auto pub = node_->create_publisher<std_msgs::msg::Int64>(
        "/" + motor_name + "/command", 10);
      command_pubs_.push_back(pub);

      // Subscriber for positions
      auto sub = node_->create_subscription<std_msgs::msg::Int64>(
        "/" + motor_name + "/position", 10,
        [this, i](const std_msgs::msg::Int64::SharedPtr msg) {
          position_callback(msg, i);
        });
      position_subs_.push_back(sub);
    }

    RCLCPP_INFO(node_->get_logger(), "Mechatrobot hardware interface configured");
    return hardware_interface::CallbackReturn::SUCCESS;
  }

  std::vector<hardware_interface::StateInterface> export_state_interfaces() override
  {
    std::vector<hardware_interface::StateInterface> state_interfaces;

    for (size_t i = 0; i < info_.joints.size(); i++)
    {
      state_interfaces.emplace_back(hardware_interface::StateInterface(
        info_.joints[i].name, hardware_interface::HW_IF_POSITION, &hw_positions_[i]));
      state_interfaces.emplace_back(hardware_interface::StateInterface(
        info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &hw_velocities_[i]));
      state_interfaces.emplace_back(hardware_interface::StateInterface(
        info_.joints[i].name, hardware_interface::HW_IF_EFFORT, &hw_efforts_[i]));
    }

    return state_interfaces;
  }

  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override
  {
    std::vector<hardware_interface::CommandInterface> command_interfaces;

    for (size_t i = 0; i < info_.joints.size(); i++)
    {
      command_interfaces.emplace_back(hardware_interface::CommandInterface(
        info_.joints[i].name, hardware_interface::HW_IF_POSITION, &hw_commands_[i]));
    }

    return command_interfaces;
  }

  hardware_interface::CallbackReturn on_activate(
    const rclcpp_lifecycle::State & /*previous_state*/) override
  {
    RCLCPP_INFO(node_->get_logger(), "Activating Mechatrobot hardware interface");

    // Initialize commands to current positions
    for (size_t i = 0; i < hw_commands_.size(); i++)
    {
      hw_commands_[i] = hw_positions_[i];
    }

    return hardware_interface::CallbackReturn::SUCCESS;
  }

  hardware_interface::CallbackReturn on_deactivate(
    const rclcpp_lifecycle::State & /*previous_state*/) override
  {
    RCLCPP_INFO(node_->get_logger(), "Deactivating Mechatrobot hardware interface");
    return hardware_interface::CallbackReturn::SUCCESS;
  }

  hardware_interface::return_type read(
    const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/) override
  {
    // Spin the node to process callbacks
    rclcpp::spin_some(node_);

    // Position data is updated via callbacks
    // Velocity and effort are not available from hardware, set to 0
    for (size_t i = 0; i < hw_velocities_.size(); i++)
    {
      hw_velocities_[i] = 0.0;
      hw_efforts_[i] = 0.0;
    }

    return hardware_interface::return_type::OK;
  }

  hardware_interface::return_type write(
    const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/) override
  {
    // Publish commands to motors
    for (size_t i = 0; i < hw_commands_.size(); i++)
    {
      auto msg = std_msgs::msg::Int64();
      // Convert from radians to degrees
      msg.data = static_cast<int>(hw_commands_[i] * 180.0 / M_PI);
      command_pubs_[i]->publish(msg);

      RCLCPP_DEBUG(node_->get_logger(),
                   "Joint %zu command: %.2f rad (%ld deg)",
                   i, hw_commands_[i], msg.data);
    }

    return hardware_interface::return_type::OK;
  }

private:
  void position_callback(const std_msgs::msg::Int64::SharedPtr msg, size_t joint_index)
  {
    // Convert from degrees to radians
    hw_positions_[joint_index] = msg->data * M_PI / 180.0;

    RCLCPP_DEBUG(node_->get_logger(),
                 "Joint %zu position: %ld deg (%.2f rad)",
                 joint_index, msg->data, hw_positions_[joint_index]);
  }

  // ROS2 node
  rclcpp::Node::SharedPtr node_;

  // Joint data
  std::vector<std::string> joint_names_;
  std::vector<double> hw_commands_;
  std::vector<double> hw_positions_;
  std::vector<double> hw_velocities_;
  std::vector<double> hw_efforts_;

  // ROS2 communication
  std::vector<rclcpp::Publisher<std_msgs::msg::Int64>::SharedPtr> command_pubs_;
  std::vector<rclcpp::Subscription<std_msgs::msg::Int64>::SharedPtr> position_subs_;
};

}  // namespace mechatrobot_hardware

#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(
  mechatrobot_hardware::MechatrobotSystemHardware,
  hardware_interface::SystemInterface)
