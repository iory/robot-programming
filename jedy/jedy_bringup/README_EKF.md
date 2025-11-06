# JEDY Robot Localization (EKF) with IMU Fusion

このドキュメントでは、JEDYロボットでIMUとWheel Odometryを融合して、より正確なオドメトリを得る方法を説明します。

## 概要

`robot_localization`パッケージのExtended Kalman Filter (EKF)を使用して、以下のセンサーデータを融合します:

1. **Wheel Odometry** (mecanum_drive_controller) - 位置と速度
2. **IMU** - 姿勢(yaw)、角速度、線形加速度

## 必要なパッケージ

```bash
sudo apt install ros-humble-robot-localization
```

## 使い方

### 方法1: EKFを含むGazebo起動 (推奨)

まだ実装されていません。以下の手動起動を使用してください。

### 方法2: 手動でEKFを起動

**重要**: EKFを使用する場合、`enable_odom_tf: false`の設定が必要です。

#### オプションA: デフォルト設定でEKFなし（現在の動作）
```bash
# Gazeboのみ（mecanum_drive_controllerがodom->base_linkのTFを出力）
ros2 launch jedy_bringup jedy_gazebo.launch.py

# SLAMを起動
ros2 launch jedy_bringup jedy_slam.launch.py
```

#### オプションB: EKF使用時（推奨 - より正確）
```bash
# ターミナル1: Gazeboを起動（通常通り）
ros2 launch jedy_bringup jedy_gazebo.launch.py

# ターミナル2: mecanum_drive_controllerの設定を変更してリロード
# 方法1: 設定ファイルを手動編集
# config/jedy_controllers.ros2.yaml の enable_odom_tf を false に変更
# その後、controller_managerを再起動

# 方法2（推奨）: 別の設定ファイルを使用
# jedy_gazebo.launch.pyを終了して、EKF用の設定で再起動
# （現在は未実装 - 手動で設定変更が必要）

# ターミナル3: EKFを起動
ros2 launch jedy_bringup jedy_ekf.launch.py

# ターミナル4: SLAMを起動
ros2 launch jedy_bringup jedy_slam.launch.py
```

**注意**:
- `mecanum_drive_controller`と`robot_localization`の両方が`odom->base_link`のTFを出力すると競合します
- EKF使用時は必ず`enable_odom_tf: false`に設定してください
- SLAM Toolboxの`transform_timeout`を0.5秒に増やして、EKFの遅延に対応しています

## データフロー

### EKFなし（現在のデフォルト）
```
mecanum_drive_controller → odom → base_link
                            (Wheel Odometryのみ)
```

### EKFあり（推奨）
```
mecanum_drive_controller ─┐
                          ├→ EKF → odom → base_link
IMU (/imu) ───────────────┘      (融合されたオドメトリ)
```

## 設定の説明

### センサー入力

**Wheel Odometry** (`/mecanum_drive_controller/odometry`):
- 使用: 線形速度 (vx, vy)、角速度 (vyaw)
- 2D平面での移動を測定

**IMU** (`/imu`):
- 使用: 姿勢 (yaw)、角速度 (vyaw)、線形加速度 (ax, ay)
- より正確な回転情報を提供
- 加速度情報で動き出しを検知

### EKFの利点

1. **より正確な姿勢推定**: IMUの角速度で wheel slippage を補正
2. **加速度情報の活用**: 動き出しや急停止をより正確に検知
3. **ノイズ除去**: センサーノイズを統計的に除去
4. **スリップ対応**: メカナムホイールのスリップをIMUで補正

## トピック

### 入力トピック
- `/mecanum_drive_controller/odometry` (nav_msgs/Odometry)
- `/imu` (sensor_msgs/Imu)

### 出力トピック
- `/odometry/filtered` (nav_msgs/Odometry) - 融合されたオドメトリ
- `/tf` - odom → base_link変換

## トラブルシューティング

### 1. EKFが起動しない
```bash
# robot_localizationがインストールされているか確認
ros2 pkg list | grep robot_localization
```

### 2. IMUデータが来ない
```bash
# IMUトピックを確認
ros2 topic hz /imu
ros2 topic echo /imu --once
```

### 3. 融合されたオドメトリを確認
```bash
# EKFの出力を確認
ros2 topic echo /odometry/filtered

# TFを確認
ros2 run tf2_ros tf2_echo odom base_link
```

## 設定ファイル

### ekf.yaml の主要パラメータ

```yaml
# 融合するセンサー
odom0: /mecanum_drive_controller/odometry  # Wheel odometry
imu0: /imu                                  # IMU

# Wheel odometryから使用する値
# [x, y, z, roll, pitch, yaw, vx, vy, vz, vroll, vpitch, vyaw, ax, ay, az]
odom0_config: [false, false, false,    # 位置は使わない
               false, false, false,    # 姿勢も使わない
               true,  true,  false,    # 速度(vx, vy)を使う
               false, false, true,     # 角速度(vyaw)を使う
               false, false, false]    # 加速度は使わない

# IMUから使用する値
imu0_config: [false, false, false,     # 位置は使わない
              false, false, true,      # yaw姿勢を使う
              false, false, false,     # 速度は使わない
              false, false, true,      # 角速度(vyaw)を使う
              true,  true,  false]     # 加速度(ax, ay)を使う
```

## 次のステップ

1. **SLAMと組み合わせる**: EKFで融合したオドメトリをSLAMの入力として使用
2. **Navigationと組み合わせる**: より正確なナビゲーション
3. **パラメータチューニング**: 実機で動作させる際は、プロセスノイズを調整

## 参考リンク

- [robot_localization Documentation](http://docs.ros.org/en/humble/p/robot_localization/)
- [EKF Configuration Tutorial](http://docs.ros.org/en/humble/p/robot_localization/tutorials/configuring_robot_localization.html)
