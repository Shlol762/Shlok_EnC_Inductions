#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray


class DoubleAckermannController(Node):
    def __init__(self):
        super().__init__('double_ackermann_controller')

        # Subscribe to teleop/joystick commands
        self.cmd_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            10
        )

        # Publisher for the 4 steering hinges (Position in Radians)
        # Order matches YAML: [fl_steer, fr_steer, rl_steer, rr_steer]
        self.steer_pub = self.create_publisher(
            Float64MultiArray,
            '/steering_controller/commands',
            10
        )

        # Publisher for the 4 wheel axles (Velocity in Rad/s)
        # Order matches YAML: [fl_drive, fr_drive, rl_drive, rr_drive]
        self.drive_pub = self.create_publisher(
            Float64MultiArray,
            '/drive_controller/commands',
            10
        )

        self.wheelbase = 0.4
        self.track_width = 0.6
        self.wheel_radius = 0.12

        self.last_linear_x = 1e-5

        self.get_logger().info("Double Ackermann Controller Node Started. Waiting for /cmd_vel...")

    def wrap_to_90(self, angle):
        """Wrap a steering angle into the (-pi/2, pi/2] range.

        Repeatedly adds or subtracts pi so the resulting angle stays
        within the physically meaningful steering limits of ±90 degrees.

        Args:
            angle (float): The raw steering angle in radians.

        Returns:
            float: The equivalent angle wrapped into (-pi/2, pi/2].
        """
        while angle > math.pi / 2:
            angle -= math.pi
        while angle <= -math.pi / 2:
            angle += math.pi
        return angle

    def cmd_callback(self, msg):
        """Handle incoming velocity commands and publish steering and drive outputs.

        Converts a Twist message (linear.x, angular.z) into individual
        wheel steering angles and drive velocities using a double-Ackermann
        kinematic model, then publishes them on the respective topics.

        Args:
            msg (geometry_msgs.msg.Twist): The commanded velocity containing
                linear.x (m/s) and angular.z (rad/s).
        """
        linear_x = msg.linear.x
        angular_z = msg.angular.z

        if abs(angular_z) < 1e-5:
            # Straight line: every wheel points forward and spins at the same rate.
            fl_angle = fr_angle = rl_angle = rr_angle = 0.0
            fl_vel = fr_vel = rl_vel = rr_vel = linear_x / self.wheel_radius
            self.last_linear_x = linear_x
        else:
            turn_vel = self.last_linear_x if abs(linear_x) < 1e-5 else linear_x
            turning_radius = turn_vel / angular_z

            sgn = 1.0 if angular_z >= 0 else -1.0

            l_denom = 2 * turning_radius - self.track_width
            fl_raw = math.atan2(sgn * self.wheelbase, sgn * l_denom)
            fl_angle = self.wrap_to_90(fl_raw)
            rl_angle = -fl_angle

            r_denom = 2 * turning_radius + self.track_width
            fr_raw = math.atan2(sgn * self.wheelbase, sgn * r_denom)
            fr_angle = self.wrap_to_90(fr_raw)
            rr_angle = -fr_angle
            
            fl_vel = rl_vel = angular_z * (l_denom / 2 * math.cos(fl_angle)
                                            + self.wheelbase / 2 * math.sin(fl_angle)) / self.wheel_radius
            fr_vel = rr_vel = angular_z * (r_denom / 2 * math.cos(fr_angle)
                                            + self.wheelbase / 2 * math.sin(fr_angle)) / self.wheel_radius

        # Publish Steering Commands
        steer_msg = Float64MultiArray()
        steer_msg.data = [fl_angle, fr_angle, rl_angle, rr_angle]
        self.steer_pub.publish(steer_msg)

        # Publish Drive Commands
        drive_msg = Float64MultiArray()
        drive_msg.data = [fl_vel, fr_vel, rl_vel, rr_vel]
        self.drive_pub.publish(drive_msg)


def main(args=None):
    rclpy.init(args=args)
    node = DoubleAckermannController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()