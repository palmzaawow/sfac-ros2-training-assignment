
# 🤖 mini_AMR – E-car Readiness Gauntlet (Basic Level)

A ROS2 multi-package project simulating a smart, fault-tolerant Autonomous Mobile Robot (AMR) subsystem.

---

## Packages Overview

| Package Name         | Description                                                  |
|----------------------|--------------------------------------------------------------|
| `battery_monitoring` | Monitors battery status, logs data, detects and recovers from faults. |
| `robot_action`       | Implements ROS2 action server for autonomous parking. |
| `robot_interfaces`   | Contains custom ROS2 messages, services, and action definitions. |

---

## Getting Started

### Prerequisites

- ROS2 installed (Humble recommended)
- colcon build tool
- Python 3.8+

### Build and Setup

```bash
cd ~/ros2_ws/src
git clone https://github.com/yourusername/mini_AMR.git
cd ..
colcon build --packages-select battery_monitoring robot_action robot_interfaces
source install/setup.bash
```
## Running the System

### Launch Battery Monitoring Node

```bash
ros2 launch battery_monitoring battery_diagnostics.launch.py
```
### Launch Test Case
```bash
ros2 run battery_monitoring fault_injector
```
---
## Features

-  Multi-threaded ROS2 nodes with concurrent callbacks

- Parking handled via action server for asynchronous feedback

- Battery data logged continuously to CSV files

- Dynamic parameters adjustable at runtime (e.g. temperature thresholds)

- Fault simulation including battery overheating and short-circuit with recovery

- Basic automated testing node included (optional)

- Clear modular structure with reusable interfaces

---
## Dynamic Parameters Example

```bash
ros2 param set /battery_monitoring overheat_threshold 60.0
```

## Testing & Debugging Tools

- rqt_graph to visualize nodes and topics

- ros2 topic echo to monitor topic data

- Check data/battery_logs.csv for battery status and event logs

---

## Project Structure
```bash
mini_AMR/
├── battery_monitoring/
│   ├── src/
│   ├── launch/
│   ├── config/
│   └── data/battery_logs.csv
├── robot_action/
├── robot_interfaces/
├── install/  # build output
├── build/    # build output
└── log/      # runtime logs
```



