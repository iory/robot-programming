# Installation Guide for jsk_enshu_recognition

## Overview

Unlike ROS1's `catkin virtualenv`, ROS2 does not have built-in Python virtual environment management. This guide explains how to install Python dependencies for this package.

## Why User Installation?

- **Per-user isolation**: Each user has their own Python packages in `~/.local/lib/python3.x/site-packages`
- **No sudo required**: Users don't need administrator privileges
- **No system conflicts**: Doesn't interfere with system Python packages
- **Safe**: Doesn't use `--break-system-packages` flag

## Installation Methods

### Method 1: Quick Install (Recommended)

The easiest way is to use the provided installation script:

```bash
cd /path/to/jsk_enshu_recognition
./scripts/install_dependencies.sh
```

This will:
1. Install all required Python packages to your user directory (`~/.local`)
2. Automatically read from `requirements.txt`
3. No sudo or system-wide changes needed

### Method 2: Manual Installation

If you prefer manual control:

```bash
cd /path/to/jsk_enshu_recognition
pip3 install --user -r requirements.txt
```

This installs:
- `mediapipe>=0.10.0`
- `tensorflow>=2.19.0`
- `opencv-contrib-python>=4.11.0`

### Method 3: System-wide (Not Recommended)

Only use this if you have a specific reason and sudo access:

```bash
pip3 install --break-system-packages mediapipe tensorflow opencv-contrib-python
```

⚠️ **Warning**: This modifies system Python packages and may cause conflicts.

## Verification

After installation, verify that everything is working:

```bash
python3 -c 'import mediapipe; import tensorflow; print("✓ All dependencies installed!")'
```

If you see the success message, you're ready to build and use the package!

## For New Users on the Same Machine

Each new user on the machine needs to install dependencies:

```bash
# As a new user
cd /path/to/workspace/src/robot-programming/jsk_enshu_recognition
./scripts/install_dependencies.sh
```

The installation is completely isolated per user - no conflicts between different users.

## Troubleshooting

### `pip3: command not found`

Install pip3:
```bash
sudo apt update
sudo apt install python3-pip
```

### `~/.local/bin not in PATH`

If installed executables aren't found, add to your `~/.bashrc`:
```bash
export PATH=$HOME/.local/bin:$PATH
```

Then reload:
```bash
source ~/.bashrc
```

### Import errors when running nodes

Make sure you've:
1. Installed dependencies: `./scripts/install_dependencies.sh`
2. Sourced the workspace: `source install/setup.bash`
3. Rebuilt the package: `colcon build --packages-select jsk_enshu_recognition`

## Comparison with ROS1 catkin virtualenv

| Feature | ROS1 catkin virtualenv | ROS2 user installation |
|---------|------------------------|------------------------|
| Virtual environment | Automatic per package | Manual per user |
| Isolation | Per package | Per user |
| Installation | Handled by catkin | Manual via pip |
| Dependencies | In devel/.venv | In ~/.local |
| Activation | Automatic with setup.bash | Not needed |

## Alternative: Using Python Virtual Environments

If you prefer explicit virtual environments (like ROS1's approach):

```bash
# Create a virtual environment
python3 -m venv ~/ros2_venv

# Activate it
source ~/ros2_venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build and use ROS2 with the venv activated
colcon build
source install/setup.bash
ros2 launch jsk_enshu_recognition gesture_recognition_with_camera.launch.py
```

Remember to activate the virtual environment each time before using the package.
