import launch
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([

        Node(
            package='battery_monitoring',
            executable='battery_publisher',
            name='battery_publisher',
            output='screen',
            parameters=[{
                'overheat_threshold': 60.0, 
                'low_voltage_threshold': 42.0, 
                'critical_percentage_threshold': 15.0
            }]
        ),

        Node(
            package='battery_monitoring',
            executable='diagnostics_subscriber',
            name='diagnostics_subscriber',
            output='screen',
        ),

        Node(
            package='robot_action',
            executable='parking_action_server',
            name='parking_action_server',
            output='screen',
        ),
    ])