#!/usr/bin/env python3

import math
import threading
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class ArmController(Node):
    def __init__(self):
        super().__init__('arm_controller_node')
        
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        self.joint_names = [
            'base_yaw_joint', 
            'shoulder_joint', 
            'elbow_joint', 
            'wrist_pitch_joint', 
            'wrist_roll_joint', 
            'gripper_servo_joint'
        ]
        
        self.base_height = 0.17       # base_plate (0.02) + yaw_column (0.15)
        self.link_upper = 0.35        # upper_arm_link
        self.link_forearm = 0.42      # forearm_link (0.35) + wrist_bracket (0.07)
        
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = self.base_height + self.link_upper + self.link_forearm # 0.94m - initialise fully extended 
        
        # Current joint positions (angles) state
        self.current_joints = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        self.timer = self.create_timer(0.05, self.publish_joint_states)
        
        self.input_thread = threading.Thread(target=self.user_interface_loop, daemon=True)
        self.input_thread.start()
        
        self.get_logger().info("IK Controller Node initialized successfully.")
        self.print_current_pose()

    def print_current_pose(self):
        """Displays the current internal coordinates of the end effector to the user."""
        print("\n" + "="*40)
        print("Current End Effector Position:")
        print(f"  x = {self.current_x:.3f}")
        print(f"  y = {self.current_y:.3f}")
        print(f"  z = {self.current_z:.3f}")
        print("="*40)

    def publish_joint_states(self):
        """Timer callback that continuously broadcasts the active joint state matrix to RViz."""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = self.current_joints
        self.joint_pub.publish(msg)

    def inverse_kinematics(self, x, y, z):
        """
        Compute the target joint angles (theta1: base swivel, theta2: shoulder, theta3: elbow) for the arm.

        Args:
            x (float): Target X position in world coordinate frame.
            y (float): Target Y position in world coordinate frame.
            z (float): Target Z position in world coordinate frame.

        Returns:
            tuple: (t1: base swivel, t2: shoulder, t3: elbow) if coordinates are valid and reachable, else None.
        """
        t1 = math.atan2(y, x) # base cylinder rotation angle (theta1)
        
        # solve for theta 3
        r = math.sqrt(x**2 + y**2)
        z_prime = z - self.base_height
        
        cos_t3 = (r**2 + z_prime**2 - self.link_upper**2 - self.link_forearm**2) / (2 * self.link_upper * self.link_forearm)

        if abs(cos_t3) > 1.0: # indicates unreachable target position
            return None
            
        sin_t3 = math.sqrt(1.0 - cos_t3**2) # picking elbow up config
        t3 = math.atan2(sin_t3, cos_t3)
        
        # solving for theta 2
        A = self.link_upper + self.link_forearm * cos_t3
        B = self.link_forearm * sin_t3
        t2 = math.atan2(A * r - B * z_prime, A * z_prime + B * r)
        
        # check joint travel safety limits from URDF rules
        if not (-1.5708 <= t2 <= 1.5708) or not (-2.3562 <= t3 <= 2.3562):
            return None
            
        return t1, t2, t3

    def calculate_displacement_limits(self, axis):
        """
        Scans outward from the current position along the selected axis to find
        the exact maximum and minimum allowable displacements before hitting boundaries.
        Gemini implementation. Small bug with the resolution of the allowed input range. Displayed range may be slightly larger than the actual reachable range due to the coarse scanning step size.
        
        Args:
            axis (str): 'x', 'y', or 'z'
            
        Returns:
            tuple: (min_displacement, max_displacement)
        """
        def is_valid(disp):
            tx = self.current_x + (disp if axis == 'x' else 0.0)
            ty = self.current_y + (disp if axis == 'y' else 0.0)
            tz = self.current_z + (disp if axis == 'z' else 0.0)
            return self.inverse_kinematics(tx, ty, tz) is not None

        coarse_step = 0.01  # 1 cm scanning intervals
        max_search = 1.5    # Absolute maximum envelope search limit (meters)
        
        # 1. Find Positive Displacement Limit
        pos_limit = 0.0
        d = coarse_step
        while d <= max_search:
            if not is_valid(d):
                # Edge found! Bisect between last valid step and first invalid step
                low, high = d - coarse_step, d
                for _ in range(10):  # Refines down to ~0.01mm precision
                    mid = (low + high) / 2.0
                    if is_valid(mid):
                        low = mid
                    else:
                        high = mid
                pos_limit = low
                break
            d += coarse_step
        else:
            pos_limit = max_search

        # 2. Find Negative Displacement Limit
        neg_limit = 0.0
        d = -coarse_step
        while d >= -max_search:
            if not is_valid(d):
                # Edge found! Bisect between last valid step and first invalid step
                low, high = d + coarse_step, d
                for _ in range(10):
                    mid = (low + high) / 2.0
                    if is_valid(mid):
                        low = mid
                    else:
                        high = mid
                neg_limit = low
                break
            d -= coarse_step
        else:
            neg_limit = -max_search

        return neg_limit, pos_limit

    def user_interface_loop(self):
        """Handle inputs without freezing program."""
        import time
        time.sleep(1.0)
        
        while rclpy.ok():
            try:
                axis = input("\nEnter axis to move (x/y/z) or 'q' to quit: ").strip().lower()
                if axis == 'q':
                    break
                if axis not in ['x', 'y', 'z']:
                    print("Invalid axis. Please use x, y, or z.")
                    continue
                
                # Dynamically calculate physical movement boundaries
                neg_lim, pos_lim = self.calculate_displacement_limits(axis)
                print(f"--> Allowed displacement range for '{axis.upper()}': [{neg_lim:.3f} m to {pos_lim:.3f} m]")
                    
                disp_str = input(f"Enter displacement in m: ").strip()
                try:
                    displacement = float(disp_str)
                except ValueError:
                    print("Invalid format.")
                    continue
                
                # Check boundaries directly before running IK
                if not (neg_lim <= displacement <= pos_lim):
                    print(f"\nERROR!!! Input {displacement:.3f}m is outside allowed limits [{neg_lim:.3f}m, {pos_lim:.3f}m]!")
                    self.print_current_pose()
                    continue
                
                target_x = self.current_x + (displacement if axis == 'x' else 0.0)
                target_y = self.current_y + (displacement if axis == 'y' else 0.0)
                target_z = self.current_z + (displacement if axis == 'z' else 0.0)
                
                ik_result = self.inverse_kinematics(target_x, target_y, target_z)
                
                if ik_result is None:
                    # Secondary fallback protection safety check
                    print("\nERROR!!! Target falls outside reachable bounds!")
                    self.print_current_pose()
                else:
                    t1, t2, t3 = ik_result
                    self.current_joints[0] = t1
                    self.current_joints[1] = t2
                    self.current_joints[2] = t3
                    
                    self.current_x = target_x
                    self.current_y = target_y
                    self.current_z = target_z
                    
                    print("\nArm position coordinates updated successfully.")
                    self.print_current_pose()
                    
            except Exception as e:
                print(f"Loop encountered error: {e}")

        raise KeyboardInterrupt  # Exit cleanly on user request

def main(args=None):
    rclpy.init(args=args)
    node = ArmController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()