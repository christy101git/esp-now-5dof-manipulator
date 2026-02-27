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
* **Actuators:** MG995 360 degree modified for base. One 180 degree MG995 Servos. Three SG90 servos. 
* **Structure:** Custom 3D-printed chassis and 360-degree rotating base (designed in SolidWorks)
* **Power Supply:** Created a custom 6 V 10 A suppply using 2 3.4V 10A rechargeable LIPO cells , 2S BMS Module ,LM2596 Buck converter , PCA9685 Servo driver

### 2. The Teleoperation Glove
* **Microcontroller:** ESP8266 (Transmitter)
* **Sensors:**  MPU6050 IMU Gyro/acceleration sensor
* **Power:** 5V powerbank and a switch.

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
## Getting Started
# Prerequisites
* Arduino IDE (with ESP32 board manager installed)

* Python 3.x (for the GUI)

* Required Arduino Libraries: esp_now.h, WiFi.h, Adafruit_PWMServoDriver.h , Wire.h

# Installation & Flashing
1. Clone the repository:
git clone [https://github.com/christy101git/esp-now-5dof-manipulator.git](https://github.com/christy101git/esp-now-5dof-manipulator.git)
2. Pairing the ESP32 and ESP8266:

* Open the Code_Transmitter_Glove sketch.

* Modify the target MAC Address variable to match your Arm's ESP32 MAC address.

* Flash the code to the Glove ESP8266.

# Flashing the Arm:

* Open the Code_Receiver_Arm sketch and flash it to the Arm ESP32.

# Running the GUI:

* Navigate to the GUI_Dashboard folder.

* Run the control script: python main_gui.py

# Challenges & Solutions
Each servo was calibrated by checking the physical limits of each servos and changing the ticks in the code for the PWM servo driver.


Author
Christy Roy

GitHub: github.com/christy101git

Portfolio: christy101git.github.io/portfolio

LinkedIn: [Insert your LinkedIn Profile URL]

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
