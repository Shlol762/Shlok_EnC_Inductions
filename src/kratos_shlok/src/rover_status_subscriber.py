#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32, Bool


class RoverStatusSubscriber(Node):

    def __init__(self):
        super().__init__('rover_status_subscriber')

        self.get_logger().info('Hello from RoverStatusSubscriber!')
        self.create_subscription(String, 'rover_mode', self.status_callback, 10)
        self.create_subscription(Float32, 'battery_level', self.battery_callback, 10)
        self.create_subscription(Bool, 'emergency_stop', self.emergency_callback, 10)

    def status_callback(self, msg):
        self.get_logger().info(f'Rover mode: {msg.data}')

    def battery_callback(self, msg):
        self.get_logger().info(f'Battery level: {msg.data:.2f}')

    def emergency_callback(self, msg):
        self.get_logger().info(f'Emergency stop: {msg.data}')


def main(args = None):
    rclpy.init(args=args)

    rover_status_subscriber = RoverStatusSubscriber()

    rclpy.spin(rover_status_subscriber)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
