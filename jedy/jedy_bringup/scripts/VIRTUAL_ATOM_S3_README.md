# Virtual Atom S3 GUI Simulator

## 概要

このツールは、物理的なAtom S3デバイスの動作を模倣するスタンドアロンGUIアプリケーションです。Gazeboシミュレータを起動せずに、ROSトピックを使ったプログラムのデバッグができます。

## 機能

### 1. ディスプレイ機能 (Subscribe)
- トピック: `/atom_s3_additional_info` (std_msgs/String)
- 動作: トピックで受信した文字列をGUI上に表示

### 2. ボタン機能 (Publish)
- トピック: `/atom_s3_button_state` (std_msgs/Int32)
- **パブリッシュ方式**: 1秒に1回、現在のボタン状態を定期的にパブリッシュ
- **重要**: パブリッシュ後、状態は即座に `0` にリセットされます（イベントは1回だけパブリッシュ）
- 動作: **OneButton.cppライブラリと同じクリックパターン検出**
  - **アイドル状態**: `0`（ボタンが押されていない状態、連続してパブリッシュ）
  - **シングルクリック**: 1回クリック → 400ms待つ → `1` を1回パブリッシュ → `0`に戻る
  - **ダブルクリック**: 2回クリック（400ms以内） → 400ms待つ → `2` を1回パブリッシュ → `0`に戻る
  - **トリプルクリック**: 3回クリック（400ms以内） → 400ms待つ → `3` を1回パブリッシュ → `0`に戻る
  - **マルチクリック**: N回クリック（400ms以内） → 400ms待つ → `N` を1回パブリッシュ（最大10まで）→ `0`に戻る
  - **長押し**: 1000ms以上押し続ける → `11` を1回パブリッシュ → `0`に戻る
  - **長押し解除**: 長押し後にボタンを離す → `12` を1回パブリッシュ → `0`に戻る

## 依存関係

必要なパッケージ:
- Python 3
- PyQt5
- ROS 2 (rclpy)
- std_msgs

### 依存関係のインストール

```bash
# PyQt5のインストール (必要に応じて)
sudo apt install python3-pyqt5

# ROS 2は既にインストールされている前提
```

## 使用方法

### 1. GUIの起動

ターミナル1で以下のコマンドを実行:

```bash
cd /home/iory/ros2/enshu/src/robot-programming/jedy/jedy_bringup/scripts
python3 virtual_atom_s3_gui.py
```

または、ROS 2ワークスペースをビルドしている場合:

```bash
ros2 run jedy_bringup virtual_atom_s3_gui.py
```

### 2. ディスプレイ機能のテスト

ターミナル2で以下のコマンドを実行して、GUI上のディスプレイに文字列を表示:

```bash
# 単発メッセージの送信
ros2 topic pub --once /atom_s3_additional_info std_msgs/msg/String "data: 'Hello Atom S3'"

# 異なるメッセージを試す
ros2 topic pub --once /atom_s3_additional_info std_msgs/msg/String "data: 'Temperature: 25°C'"
ros2 topic pub --once /atom_s3_additional_info std_msgs/msg/String "data: 'Status: OK'"
```

### 3. ボタン機能のテスト

ターミナル2で以下のコマンドを実行して、ボタンクリックのデータを確認:

```bash
# トピックのエコー
ros2 topic echo /atom_s3_button_state
```

**テストパターン:**

1. **アイドル状態**: 何もしない → `data: 0` が1秒ごとに連続表示
2. **シングルクリック**: 1回クリック → 次の1秒タイミングで `data: 1` が1回表示 → その後 `data: 0` に戻る
3. **ダブルクリック**: 素早く2回クリック → 次の1秒タイミングで `data: 2` が1回表示 → その後 `data: 0` に戻る
4. **トリプルクリック**: 素早く3回クリック → 次の1秒タイミングで `data: 3` が1回表示 → その後 `data: 0` に戻る
5. **長押し**: ボタンを1秒以上押し続ける → 次の1秒タイミングで `data: 11` が1回表示 → その後 `data: 0` に戻る
6. **長押し解除**: 長押し状態からボタンを離す → 次の1秒タイミングで `data: 12` が1回表示 → その後 `data: 0` に戻る

**出力例（シングルクリック）:**
```
data: 0
data: 0
[ここでクリック]
data: 1  ← クリックイベント（1回だけ）
data: 0
data: 0
data: 0
...
```

### 4. 双方向テスト

ターミナル2で:
```bash
ros2 topic echo /atom_s3_button_state
```

ターミナル3で:
```bash
# 1秒ごとにメッセージを送信
ros2 topic pub -r 1 /atom_s3_additional_info std_msgs/msg/String "data: 'Counter: Running'"
```

GUI上で「CLICK SCREEN」ボタンをクリックし、ターミナル2でクリック回数を確認できます。

## 実装の詳細

### スレッド安全性

- PyQtのシグナル/スロット機構を使用して、ROSコールバックからGUIを安全に更新
- `QTimer`を使用して、GUIイベントループ内でROS 2の`spin_once`を定期的に呼び出し

### 技術スタック

- **GUI**: PyQt5
- **ROS通信**: rclpy (ROS 2 Python Client Library)
- **メッセージ型**: std_msgs (String, Int32)

## トラブルシューティング

### PyQt5がインストールされていない場合

```bash
sudo apt update
sudo apt install python3-pyqt5
```

### ROS 2環境が設定されていない場合

```bash
source /opt/ros/<your-ros-distro>/setup.bash
# 例: source /opt/ros/humble/setup.bash
```

### トピックが見えない場合

別のターミナルで以下を確認:

```bash
# 利用可能なトピック一覧
ros2 topic list

# 特定のトピック情報
ros2 topic info /atom_s3_additional_info
ros2 topic info /atom_s3_button_state
```

## アーキテクチャ

```
┌─────────────────────────────────────┐
│   Virtual Atom S3 GUI Application   │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │      PyQt5 GUI Widget       │   │
│  ├─────────────────────────────┤   │
│  │  - Display Label            │   │
│  │  - Click Button             │   │
│  │  - Status Labels            │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│             │ Signal/Slot           │
│             │                       │
│  ┌──────────▼──────────────────┐   │
│  │      ROS 2 Node             │   │
│  ├─────────────────────────────┤   │
│  │  Publisher:                 │   │
│  │    /atom_s3_button_state    │───┼──► Int32
│  │                             │   │
│  │  Subscriber:                │   │
│  │    /atom_s3_additional_info │◄──┼─── String
│  └─────────────────────────────┘   │
│                                     │
│  QTimer (20Hz) ──► spin_once()     │
│                                     │
└─────────────────────────────────────┘
```

## 今後の拡張案

1. 複数のボタンのサポート (ボタンA、B、C)
2. LEDインジケーターの視覚化
3. センサーデータの表示（温度、加速度など）
4. 設定可能なトピック名
5. ログの保存機能

## ライセンス

このプロジェクトのライセンスに従います (BSD)
