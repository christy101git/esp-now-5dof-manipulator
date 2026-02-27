# ESP-NOW Enabled 5-DOF Robotic Manipulator with Teleoperation Glove

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Hardware](https://img.shields.io/badge/Hardware-ESP32%20%7C%20MG995-orange)
![Protocol](https://img.shields.io/badge/Protocol-ESP--NOW-success)

> **[Insert a high-quality GIF or Photo of the arm mimicking your hand movements here]**

## Project Overview
This repository contains the hardware designs, microcontroller firmware, and software GUI for a custom 5-Degree of Freedom (DOF) robotic manipulator arm. The system features low-latency wireless teleoperation achieved through a custom wearable sensor glove communicating via the ESP-NOW protocol. 

A dedicated desktop GUI provides real-time system monitoring, sensor feedback visualization, and manual override controls.

## Key Features
* **Low-Latency Teleoperation:** Utilizes the ESP-NOW protocol for direct, router-less communication between the sensor glove and the robotic arm, ensuring near-instantaneous response times.
* **5-DOF Kinematics:** Fully articulated 360-degree base and arm structure for complex spatial manipulation.
* **Closed-Loop Feedback:** Integration of magnetic encoders to ensure accurate positional holding and jitter reduction.
* **Custom Control Dashboard:** A dedicated Graphical User Interface (GUI) for real-time telemetry, calibration, and system diagnostics.

## Hardware Architecture & Bill of Materials

### 1. The Manipulator Arm
* **Microcontroller:** ESP32 (Receiver)
* **Actuators:** MG995 High-Torque Servos
* **Sensors:** AS5600 Magnetic Encoders (for high-precision positional feedback)
* **Structure:** Custom 3D-printed chassis and 360-degree rotating base (designed in SolidWorks)
* **Power Supply:** [Insert your power supply details, e.g., 5V 10A DC Power Supply]

### 2. The Teleoperation Glove
* **Microcontroller:** ESP32 (Transmitter)
* **Sensors:** [Insert your glove sensors, e.g., Flex Sensors / MPU6050 IMU]
* **Power:** [Insert battery type, e.g., 3.7V LiPo Battery]

## Software Architecture

### Communication Protocol (ESP-NOW)
ESP-NOW was selected over standard Wi-Fi or Bluetooth due to its peer-to-peer MAC address pairing. This bypasses the need for a local network router, vastly reducing latency and making the system highly portable for field demonstrations.

### GUI Control Center
* **Framework:** [Insert your GUI framework, e.g., Python Tkinter / PyQt5]
* **Features:** Live joint angle visualization, connection status monitoring, and calibration modes.

##  Repository Structure
```text
├── 3D_Models/               # .stl files and SolidWorks parts for the arm structure
├── Code_Transmitter_Glove/  # ESP32 C++ code for reading glove sensors and sending data
├── Code_Receiver_Arm/       # ESP32 C++ code for receiving data and driving MG995 servos
├── GUI_Dashboard/           # Python scripts for the desktop interface
├── Schematics/              # Circuit diagrams and wiring guides
└── README.md                # Project documentation
```
Getting Started
Prerequisites
Arduino IDE (with ESP32 board manager installed)

Python 3.x (for the GUI)

Required Arduino Libraries: esp_now.h, WiFi.h, [Add any servo/encoder libraries you used]

Installation & Flashing
Clone the repository:

Bash
git clone [https://github.com/christy101git/esp-now-5dof-manipulator.git](https://github.com/christy101git/esp-now-5dof-manipulator.git)
Pairing the ESP32s:

Open the Code_Transmitter_Glove sketch.

Modify the target MAC Address variable to match your Arm's ESP32 MAC address.

Flash the code to the Glove ESP32.

Flashing the Arm:

Open the Code_Receiver_Arm sketch and flash it to the Arm ESP32.

Running the GUI:

Navigate to the GUI_Dashboard folder.

Run the control script: python main_gui.py

Challenges & Solutions
Servo Jitter Mitigation: Early iterations experienced jitter when holding heavy loads. Solution: Implemented a deadband filter in the control logic and smoothed the raw data coming from the AS5600 encoders to stabilize the MG995 holding torque.

[Insert another challenge here]: [Insert how you solved it]

Author
Christy Roy

GitHub: github.com/christy101git

Portfolio: christy101git.github.io/portfolio

LinkedIn: [Insert your LinkedIn Profile URL]

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
