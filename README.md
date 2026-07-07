# Kratos Induction Repository

This repo contains all my required KiCAD and ROS 2 Humble packages for the Kratos Induction tasks.

## Directory Structure

### [PCB Assignments (Week 2)](PCB/README.md)
* **`breakout_footprint/`**: Custom symbol and footprints for I2C Multiplexer breakout board.
* **`libs/`**: Custom symbols and footprint libraries for sensors (MPU6050, HC-SR04).
* **`mcu_breakout_board/`**: Schematic and routed PCB layout files for an ESP32 breakout board.
* **`power_dist_box/`**: Placeholder directory for the power distribution board task. (Haven't completed as of Jul 7th)

### [ROS Assignments (Week 3)](ROS/README.md)


* **`Q1/kratos_shlok`**: Node setup assignment with publisher and subscriber nodes, dealing in randomised data, using builtin message types.
* **`Q2/kratos_shlok` & `Q2/kratos_shlok_msgs`**: Node setup assignment with publisher and subscriber nodes, dealing in custom message types, using a custom message package.
* **`TFKIK/arm_humble`**: Robot arm controller using FKIK principles.
