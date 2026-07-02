#!/usr/bin/env python3

import rclpy
import random
from rclpy.node import Node
from std_msgs.msg import String, Float32, Bool


class RoverStatusPublisher(Node):

    def __init__(self):
        super().__init__('rover_status_publisher')

        self.get_logger().info('Hello from RoverStatusPublisher!')

        self.bat_lvl_pub_ = self.create_publisher(Float32, '/battery_level', 10)
        self.rvr_mod_pub_ = self.create_publisher(String, '/rover_mode', 10)
        self.emy_stp_pub_ = self.create_publisher(Bool, '/emergency_stop', 10)

        self.create_timer(1, self.timer_callback)

    def timer_callback(self):
        bat = Float32()
        bat.data = random.uniform(0.0, 100.0)  # Example battery level

        rvr_mod = String()
        rvr_mod.data = random.choice(['point turn', 'crab walk', 'normal'])  # Example rover mode

        emy_stp = Bool()
        emy_stp.data = random.choice([True, False])  # Example emergency stop status

        self.bat_lvl_pub_.publish(bat)
        self.rvr_mod_pub_.publish(rvr_mod)
        self.emy_stp_pub_.publish(emy_stp)

        self.get_logger().info(f'Published battery level: {bat.data:.2f}, rover mode: {rvr_mod.data}, emergency stop: {emy_stp.data}')


def main(args = None):
    rclpy.init(args=args)

    rover_status_publisher = RoverStatusPublisher()

    rclpy.spin(rover_status_publisher)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
