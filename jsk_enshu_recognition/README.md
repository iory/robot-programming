# jsk_enshu_recognition

ROS2 hand pose estimation and gesture recognition package using MediaPipe and TensorFlow Lite.

## Packages

### jsk_enshu_msgs
Custom message definitions for hand pose and gesture recognition:
- `PeoplePose.msg`, `PeoplePoseArray.msg` - Hand landmark poses
- `HumanSkeleton.msg`, `HumanSkeletonArray.msg` - Hand skeleton structures
- `Segment.msg` - Bone segment representation
- `ClassificationResult.msg` - Gesture classification results

### jsk_enshu_recognition
Recognition nodes:
- `hand_pose_estimation` - Hand landmark detection using MediaPipe
- `gesture_recognition` - Hand gesture classification using TensorFlow Lite
- `face_recognition` - Face detection and keypoint extraction using MediaPipe
- `people_pose_estimation` - Full body pose estimation (33 landmarks) using MediaPipe
- `skeleton_with_depth` - Converts 2D skeleton to 3D using depth images and publishes MarkerArray for RViz visualization

## Dependencies

### Python Dependencies

This package requires `mediapipe` and `tensorflow` which are not available through apt.
Each user needs to install these dependencies in their user space.

**Option 1: Use the provided install script (Recommended)**

```bash
cd /home/iory/ros2/enshu/src/robot-programming/jsk_enshu_recognition
./scripts/install_dependencies.sh
```

**Option 2: Manual installation with pip**

```bash
cd /home/iory/ros2/enshu/src/robot-programming/jsk_enshu_recognition
pip3 install --user -r requirements.txt
```

**Option 3: System-wide installation (Not recommended, requires sudo)**

```bash
pip3 install --break-system-packages mediapipe tensorflow
```

### Verify Installation

```bash
python3 -c 'import mediapipe; import tensorflow; print("✓ Dependencies installed successfully!")'
```

## Build

```bash
cd /home/iory/ros2/enshu
colcon build --packages-select jsk_enshu_msgs jsk_enshu_recognition
source install/setup.bash
```

## Usage

### All Recognition Nodes (Recommended)

Launch USB camera, hand pose estimation, and gesture recognition all at once:

```bash
ros2 launch jsk_enshu_recognition recognition_all.launch.py
```

This single command starts:
- USB camera node
- Hand pose estimation node
- Gesture recognition node

Parameters:
- `video_device` (default: `/dev/video0`) - Video device path
- `image_width` (default: `640`) - Image width
- `image_height` (default: `480`) - Image height
- `framerate` (default: `30.0`) - Camera framerate

### Individual Launch Files

**Hand Pose Estimation only:**
```bash
ros2 launch jsk_enshu_recognition hand_pose_estimation_with_camera.launch.py
```

**Gesture Recognition only:**
```bash
ros2 launch jsk_enshu_recognition gesture_recognition_with_camera.launch.py
```

**Face Recognition only:**
```bash
ros2 launch jsk_enshu_recognition face_recognition_with_camera.launch.py
```

**People Pose Estimation only:**
```bash
ros2 launch jsk_enshu_recognition people_pose_estimation_with_camera.launch.py
```

### Topics

#### hand_pose_estimation
- Input: `~/input` (sensor_msgs/Image)
- Output:
  - `~/output/pose` (jsk_enshu_msgs/PeoplePoseArray) - Hand landmarks
  - `~/output/skeleton` (jsk_enshu_msgs/HumanSkeletonArray) - Hand skeleton
  - `~/output/viz` (sensor_msgs/Image) - Visualization image
  - `~/output/viz/compressed` (sensor_msgs/CompressedImage) - Compressed visualization

#### gesture_recognition
- Input: `~/input` (sensor_msgs/Image)
- Output:
  - `~/result` (jsk_enshu_msgs/ClassificationResult) - Gesture recognition result (supports multiple hands)
  - `~/result/string` (std_msgs/String) - Simple string result (e.g., "Paper, Rock" for two hands)
  - `~/output` (sensor_msgs/Image) - Visualization image
  - `~/output/compressed` (sensor_msgs/CompressedImage) - Compressed visualization

#### face_recognition
- Input: `~/input` (sensor_msgs/Image)
- Output:
  - `~/output/skeleton` (jsk_enshu_msgs/HumanSkeletonArray) - Face keypoints as skeleton segments
  - `~/output/viz` (sensor_msgs/Image) - Visualization image with face detections
  - `~/output/viz/compressed` (sensor_msgs/CompressedImage) - Compressed visualization

#### people_pose_estimation
- Input: `~/input` (sensor_msgs/Image)
- Output:
  - `~/output/pose` (jsk_enshu_msgs/PeoplePoseArray) - Full body pose landmarks (33 points)
  - `~/output/skeleton` (jsk_enshu_msgs/HumanSkeletonArray) - Body skeleton structure
  - `~/output/viz` (sensor_msgs/Image) - Visualization image with pose overlay
  - `~/output/viz/compressed` (sensor_msgs/CompressedImage) - Compressed visualization

#### skeleton_with_depth
- Input:
  - `~/input/skeleton` (jsk_enshu_msgs/HumanSkeletonArray) - 2D skeleton data
  - `~/input/depth` (sensor_msgs/Image) - Depth image (16UC1 or 32FC1 encoding)
  - `~/input/info` (sensor_msgs/CameraInfo) - Camera calibration info
- Output:
  - `~/output/pose` (jsk_enshu_msgs/HumanSkeletonArray) - 3D skeleton in camera frame
  - `~/output/marker` (visualization_msgs/MarkerArray) - RViz markers for skeleton visualization
- Parameters:
  - `queue_size` (default: 10) - Message queue size
  - `approximate_sync` (default: true) - Use approximate time synchronization
  - `slop` (default: 0.1) - Time synchronization tolerance in seconds
  - `sync_camera_info` (default: false) - Synchronize camera info with other topics

## Verify Gesture Recognition Output

To check if gesture recognition is working:

```bash
# Terminal 1: Launch all nodes
ros2 launch jsk_enshu_recognition recognition_all.launch.py

# Terminal 2: Echo the result topic (ClassificationResult format)
ros2 topic echo /gesture_recognition/result

# OR: Echo the simple string format (easier to read)
ros2 topic echo /gesture_recognition/result/string
```

**Important**: The gesture recognition node supports **up to 2 hands simultaneously** and publishes results continuously. You should see:
- **No hand detected**: Empty `label_names` list
  ```
  header:
    stamp:
      sec: 1762037030
      nanosec: 880196019
    frame_id: ''
  label_names: []
  label_proba: []
  classifier: ''
  target_names: ''
  ---
  ```

- **One hand detected**: `label_names` contains one gesture
  ```
  header:
    stamp:
      sec: 1762037030
      nanosec: 880196019
    frame_id: ''
  label_names:
  - Paper
  label_proba: []
  classifier: ''
  target_names: ''
  ---
  ```

- **Two hands detected**: `label_names` contains two gestures
  ```
  header:
    stamp:
      sec: 1762037030
      nanosec: 880196019
    frame_id: ''
  label_names:
  - Paper
  - Rock
  label_proba: []
  classifier: ''
  target_names: ''
  ---
  ```

- **String format** (easier to read):
  ```
  data: "Paper, Rock"
  ---
  # Or when no hand detected:
  data: "No hand detected"
  ---
  ```

The available gestures (in config/keypoint_classifier_label.csv):
- **Paper** (パー) - Open hand
- **Rock** (グー) - Closed fist
- **Pointer** (指差し) - Pointing finger
- **Scissors** (チョキ) - V sign

### Check if nodes are running

```bash
ros2 node list
# Should show:
# /usb_cam
# /hand_pose_estimation
# /gesture_recognition

ros2 topic list
# Should show gesture recognition topics:
# /gesture_recognition/result
# /gesture_recognition/output
# /gesture_recognition/output/compressed
```

### Debug: Check logs

If not working, check the logs:
```bash
ros2 topic hz /gesture_recognition/result  # Check publication rate
ros2 topic hz /image_raw  # Check camera is publishing
```

## Example with Different Camera

```bash
ros2 launch jsk_enshu_recognition gesture_recognition_with_camera.launch.py video_device:=/dev/video1
```

## Notes

- The gesture recognition model is located at: `config/keypoint_classifier.tflite`
- The label file is located at: `config/keypoint_classifier_label.csv`
- Camera calibration warnings can be safely ignored
- Unknown control warnings (white_balance, exposure_auto, focus_auto) depend on your camera hardware and can be ignored
