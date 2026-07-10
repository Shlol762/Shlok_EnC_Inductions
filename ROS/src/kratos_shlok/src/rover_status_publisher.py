#!/usr/bin/env python3

import rclpy
import random
from rclpy.node import Node
# from std_msgs.msg import String, Float32, Bool

from kratos_shlok_msgs.msg import RoverStatus


class RoverStatusPublisher(Node):

    def __init__(self):
        super().__init__('rover_status_publisher')

        self.get_logger().info('Hello from RoverStatusPublisher!')

        self.rover_status_pub_ = self.create_publisher(RoverStatus, '/rover_status', 10)

        self.create_timer(0.5, self.timer_callback)

    def timer_callback(self):
        """
        Publishes random values for battery percentage, velocity, emergency stop, and mode, in the /rover_status topic, at 2 Hz.

        Args:
            None
        Returns:
            None
        """
        rover_status = RoverStatus()
        rover_status.battery_percentage = random.uniform(0.0, 100.0)
        rover_status.velocity = random.uniform(0.0, 5.0)
        rover_status.emergency_stop = random.choice([True, False])
        rover_status.mode = random.choice(['IDLE', 'MOVING', 'STOPPED'])

        self.rover_status_pub_.publish(rover_status)
        self.get_logger().info(f'Published: bat %: {rover_status.battery_percentage:<5.2f} | vel: {rover_status.velocity:<3.2f} | emergency stop: {str(rover_status.emergency_stop):<5} | mode: {rover_status.mode:<5}')

def main(args = None):
    rclpy.init(args=args)

    rover_status_publisher = RoverStatusPublisher()

    rclpy.spin(rover_status_publisher)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
