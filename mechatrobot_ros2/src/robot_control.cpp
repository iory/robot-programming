/*********************************************************************
 * Software License Agreement (BSD License)
 *
 *  Copyright (c) 2008, Willow Garage, Inc.
 *  All rights reserved.
 *
 *  Modified 2020, by Kei OKada and Yuki Asano
 *  Modified 2025, for ROS2 migration
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
 *  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 *********************************************************************/
#include <signal.h>
#include <pthread.h>
#include <atomic>
#include <condition_variable>
#include <thread>
#include <chrono>
#include <vector>
#include <string>
#include <memory>

using namespace std::chrono_literals;

// ROS2
#include <rclcpp/rclcpp.hpp>

// messages
#include <std_msgs/msg/int64.hpp>
#include <std_msgs/msg/float64.hpp>

namespace robot_control
{
struct JointData
{
  std::string name_;
  double cmd_;
  double pos_;
  double vel_;
  double eff_;
  int home_encoder_offset_;
};

class JointControlInterface
{
public:
  JointControlInterface(std::shared_ptr<rclcpp::Node> node, int joint_id,
                        std::string command_topic, std::string position_topic)
    : node_(node)
  {
    // create joint name
    std::stringstream ss;
    ss << "joint" << joint_id;
    joint.name_ = ss.str();

    // Publishers and subscribers
    joint_pub_ = node_->create_publisher<std_msgs::msg::Int64>(command_topic, 10);
    joint_sub_ = node_->create_subscription<std_msgs::msg::Int64>(
        position_topic, 10,
        std::bind(&JointControlInterface::positionCB, this, std::placeholders::_1));

    // initialize joint/command
    joint.cmd_ = joint.pos_ = 0;
    joint.vel_ = joint.eff_ = 0;

    // initialize timing
    last_received_ = node_->now();
    last_read_ = node_->now();
  }

  ~JointControlInterface() = default;

  void read()
  {
    if (last_read_ >= last_received_)
    {  // no received message after last read
      std::unique_lock<std::mutex> lk(cv_m_);
      if (cv_.wait_for(lk, 100ms, [] { return false; }))
      {
        RCLCPP_ERROR_STREAM(node_->get_logger(),
                           "Did not receive message " << joint.name_ << " for 100ms");
      }
    }
    RCLCPP_DEBUG_STREAM(node_->get_logger(), joint.name_ << " read() : " << joint.pos_);
    joint.pos_ = joint.cmd_;  // do loop back
    last_read_ = node_->now();
  }

  void positionCB(const std_msgs::msg::Int64::SharedPtr msg)
  {
    joint.pos_ = msg->data * M_PI / 180.0;
    cv_.notify_all();
    last_received_ = node_->now();
  }

  void write()
  {
    RCLCPP_DEBUG_STREAM(node_->get_logger(), joint.name_ << " write() : " << joint.cmd_);
    auto msg = std_msgs::msg::Int64();
    msg.data = static_cast<int>(joint.cmd_ * 180 / M_PI);
    joint_pub_->publish(msg);
  }

  void shutdown()
  {
  }

  JointData joint;

protected:
  std::shared_ptr<rclcpp::Node> node_;
  rclcpp::Publisher<std_msgs::msg::Int64>::SharedPtr joint_pub_;
  rclcpp::Subscription<std_msgs::msg::Int64>::SharedPtr joint_sub_;
  rclcpp::Time last_received_;
  rclcpp::Time last_read_;
  // lock
  std::condition_variable cv_;
  std::mutex cv_m_;
};

class RobotHardwareInterface
{
private:
  std::shared_ptr<rclcpp::Node> node_;
  typedef std::vector<std::shared_ptr<JointControlInterface>> JointControlContainer;
  JointControlContainer controls_;

public:
  RobotHardwareInterface(std::shared_ptr<rclcpp::Node> node)
    : node_(node)
  {
    registerControl(std::make_shared<JointControlInterface>(
        node_, 1, "/motor1/command", "/motor1/position"));
  }

  ~RobotHardwareInterface()
  {
    shutdown();
  }

  void registerControl(std::shared_ptr<JointControlInterface> control)
  {
    controls_.push_back(control);
  }

  void read()
  {
    for (auto& control : controls_)
    {
      control->read();
    }
  }

  void write()
  {
    for (auto& control : controls_)
    {
      control->write();
    }
  }

  void shutdown()
  {
    for (auto& control : controls_)
    {
      control->shutdown();
    }
    controls_.clear();
  }

  rclcpp::Time getTime()
  {
    return node_->now();
  }

  rclcpp::Duration getPeriod()
  {
    return rclcpp::Duration::from_seconds(0.001);
  }
};

}  // namespace robot_control

static std::atomic<bool> g_quit{false};

void controlLoop(std::shared_ptr<rclcpp::Node> node)
{
  // Initialize the hardware interface
  robot_control::RobotHardwareInterface robot(node);

  RCLCPP_INFO(node->get_logger(), "started controlLoop");

  rclcpp::Rate rate(10);  // 10 Hz
  while (rclcpp::ok() && !g_quit)
  {
    robot.read();
    robot.write();
    rate.sleep();
  }

  robot.shutdown();
}

void quitRequested(int sig)
{
  g_quit = true;
  std::cerr << ";; call quitRequested sig(" << sig << ")" << std::endl;
}

int main(int argc, char* argv[])
{
  // Initialize ROS2
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("robot_control");

  // Catch attempts to quit
  signal(SIGTERM, quitRequested);
  signal(SIGINT, quitRequested);
  signal(SIGHUP, quitRequested);

  // Start control loop in separate thread
  std::thread control_thread(controlLoop, node);

  // Spin the node
  rclcpp::spin(node);

  // Wait for control thread to finish
  control_thread.join();

  rclcpp::shutdown();
  return 0;
}
