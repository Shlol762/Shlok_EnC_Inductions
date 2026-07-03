from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='kratos_shlok',
            executable='rover_status_publisher.py',
            name='rover_status_publisher',
        ),
        Node(
            package='kratos_shlok',
            executable='rover_status_subscriber.py',
            name='rover_status_subscriber',
        )
    ])