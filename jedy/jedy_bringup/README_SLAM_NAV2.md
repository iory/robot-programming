# JEDY SLAM and Navigation Demo

このドキュメントでは、JEDYロボットでSLAMとNavigation2を使用したデモの実行方法を説明します。

## 必要なパッケージ

以下のパッケージがインストールされている必要があります:

```bash
sudo apt install ros-humble-slam-toolbox
sudo apt install ros-humble-navigation2
sudo apt install ros-humble-nav2-bringup
sudo apt install ros-humble-teleop-twist-keyboard
```

## ビルド

```bash
cd ~/ros2/enshu
colcon build --symlink-install
source install/setup.bash
```

## デモの実行方法

### 1. SLAMデモ（地図作成）

まず、SLAMを使用して環境の地図を作成します。

#### ステップ1: Gazeboシミュレーション + SLAMの起動

```bash
ros2 launch jedy_bringup jedy_gazebo_slam_demo.launch.py
```

このコマンドで以下が起動します:
- Gazeboシミュレーション環境にJEDYロボット
- LiDARセンサー（`/scan`トピック）
- IMUセンサー（`/imu`トピック）
- SLAM Toolbox（オンライン非同期マッピング）
- RViz2（ビジュアライゼーション）

#### ステップ2: ロボットの操縦

別のターミナルで、キーボード操縦を起動します:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

または、jedy_bringupのキーボード操縦を使用:

```bash
ros2 launch jedy_bringup keyboard_teleop.launch.py
```

キーボードでロボットを操縦して環境を探索します:
- `i`: 前進
- `k`: 停止
- `,`: 後退
- `j`: 左回転
- `l`: 右回転
- `u`: 前進しながら左回転
- `o`: 前進しながら右回転
- `m`: 後退しながら左回転
- `.`: 後退しながら右回転

#### ステップ3: 地図の保存

環境を十分に探索したら、地図を保存します:

```bash
cd ~/ros2/enshu/maps
mkdir -p .
ros2 run nav2_map_server map_saver_cli -f my_map
```

これにより、`my_map.yaml`と`my_map.pgm`が作成されます。

### 2. Navigationデモ（自律ナビゲーション）

作成した地図を使用して、自律ナビゲーションを実行します。

#### ステップ1: Gazebo + Navigation2の起動

```bash
ros2 launch jedy_bringup jedy_gazebo_navigation_demo.launch.py map:=/absolute/path/to/my_map.yaml
```

例:
```bash
ros2 launch jedy_bringup jedy_gazebo_navigation_demo.launch.py map:=$HOME/ros2/enshu/maps/my_map.yaml
```

このコマンドで以下が起動します:
- Gazeboシミュレーション環境にJEDYロボット
- AMCL（適応型モンテカルロ位置推定）
- Navigation2スタック
- RViz2

#### ステップ2: 初期位置の設定

RViz2で:
1. 上部ツールバーの「2D Pose Estimate」ボタンをクリック
2. 地図上でロボットの実際の位置と向きをクリック&ドラッグで設定
3. AMCLがロボットの位置を推定し始めます

#### ステップ3: ナビゲーションゴールの設定

RViz2で:
1. 上部ツールバーの「Nav2 Goal」ボタンをクリック
2. 地図上の目標位置をクリック&ドラッグで設定
3. ロボットが自律的に目標に向かって移動します

## 利用可能なセンサー

JEDYロボットには以下のセンサーが搭載されています:

### LiDAR
- トピック: `/scan`
- 型: `sensor_msgs/msg/LaserScan`
- フレーム: `base_laser`
- 仕様:
  - 360サンプル
  - 範囲: 0.12m - 10.0m
  - 視野角: 180度（-90度 ~ +90度）
  - 更新レート: 10Hz

### IMU
- トピック: `/imu`
- 型: `sensor_msgs/msg/Imu`
- フレーム: `real_base_link`
- 仕様:
  - 角速度（ジャイロスコープ）
  - 線形加速度（加速度計）
  - 更新レート: 100Hz

### RGB-Dカメラ
- カラー画像: `/camera/color/image_rect_raw`
- 深度画像: `/camera/depth/image_rect_raw`
- ポイントクラウド: `/camera/depth/color/points`

## 設定ファイル

### SLAM Toolbox設定
- ファイル: `config/slam/mapper_params_online_async.yaml`
- 調整可能なパラメータ:
  - `resolution`: 地図の解像度（デフォルト: 0.05m）
  - `max_laser_range`: LiDARの最大使用範囲（デフォルト: 10.0m）
  - `minimum_travel_distance`: SLAMが更新される最小移動距離（デフォルト: 0.05m）

### Navigation2設定
- ファイル: `config/nav2/nav2_params.yaml`
- 主要なコンポーネント:
  - AMCL: 位置推定
  - Controller Server: 経路追従
  - Planner Server: 経路計画
  - Costmap: 障害物マップ

## トラブルシューティング

### 1. ロボットが地図を作成しない
- `/scan`トピックがパブリッシュされているか確認:
  ```bash
  ros2 topic echo /scan
  ```
- LiDARの可視化がGazeboで有効になっているか確認

### 2. ナビゲーションが機能しない
- 初期位置が正しく設定されているか確認
- `/map`トピックがパブリッシュされているか確認:
  ```bash
  ros2 topic echo /map
  ```
- コストマップが正しく更新されているか確認

### 3. TFエラー
- TFツリーを確認:
  ```bash
  ros2 run tf2_tools view_frames
  evince frames.pdf
  ```

## 参考リンク

- [SLAM Toolbox](https://github.com/SteveMacenski/slam_toolbox)
- [Navigation2](https://navigation.ros.org/)
- [Nav2 Tutorials](https://navigation.ros.org/tutorials/index.html)

## 使用例: 完全なワークフロー

```bash
# 1. SLAMで地図作成
ros2 launch jedy_bringup jedy_gazebo_slam_demo.launch.py

# 別のターミナルで操縦
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# 地図を保存
mkdir -p ~/ros2/enshu/maps
cd ~/ros2/enshu/maps
ros2 run nav2_map_server map_saver_cli -f my_map

# 2. Navigation2で自律ナビゲーション
ros2 launch jedy_bringup jedy_gazebo_navigation_demo.launch.py map:=$HOME/ros2/enshu/maps/my_map.yaml
```

RViz2で初期位置とゴールを設定すれば、ロボットが自律的にナビゲーションします！
