#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
# from std_msgs.msg import String, Float32, Bool

from kratos_shlok_msgs.msg import RoverStatus


class RoverStatusSubscriber(Node):

    def __init__(self):
        super().__init__('rover_status_subscriber')

        self.get_logger().info('Hello from RoverStatusSubscriber!')
        self.create_subscription(RoverStatus, 'rover_status', self.status_callback, 10)

    def status_callback(self, msg):
        self.get_logger().info(f'Received : bat %: {msg.battery_percentage:<5.2f} | vel: {msg.velocity:<5.2f} | emergency stop: {str(msg.emergency_stop):<5} | mode: {msg.mode:<5}')



def main(args = None):
    rclpy.init(args=args)

    rover_status_subscriber = RoverStatusSubscriber()

    rclpy.spin(rover_status_subscriber)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
