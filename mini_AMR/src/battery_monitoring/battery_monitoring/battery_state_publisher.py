import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from builtin_interfaces.msg import Time
import random
import csv
import os

from robot_interfaces.msg import BatteryState


class BatteryStatePublisher(Node):
    def __init__(self):
        super().__init__('battery_state_publisher')

        self.declare_parameter('overheat_threshold', 60.0)
        self.declare_parameter('low_voltage_threshold', 42.0)
        self.declare_parameter('critical_percentage_threshold', 15.0)

        self.overheat_threshold = self.get_parameter('overheat_threshold').value
        self.low_voltage_threshold = self.get_parameter('low_voltage_threshold').value
        self.critical_percentage_threshold = self.get_parameter('critical_percentage_threshold').value

        self.add_on_set_parameters_callback(self.parameter_callback)

        self.publisher_ = self.create_publisher(BatteryState, '/battery_state', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)

        self.percentage = 100.0
        self.test_stage = False
        
        self.csv_file = 'battery_log.csv'
        self.csv_header = ['timestamp', 'voltage', 'current', 'percentage', 'temperature', 'status']

        if not os.path.exists(self.csv_file):
            try:
                with open(self.csv_file, mode='w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.csv_header)
            except Exception as e:
                self.get_logger().error(f"Failed to create CSV file: {e}")

    def parameter_callback(self, params):

        for param in params:

            if param.name == 'overheat_threshold':

                self.overheat_threshold = param.value
                self.get_logger().info(f"Updated overheat_threshold to {param.value}")
            
            elif param.name == 'low_voltage_threshold':

                self.low_voltage_threshold = param.value
                self.get_logger().info(f"Updated low_voltage_threshold to {param.value}")
            
            elif param.name == 'critical_percentage_threshold':

                self.critical_percentage_threshold = param.value
                self.get_logger().info(f"Updated critical_percentage_threshold to {param.value}")
        
        return SetParametersResult(successful=True)

    def timer_callback(self):

        msg = BatteryState()

        msg.voltage = random.uniform(40.0, 48.0)
        msg.current = random.uniform(0.0, 10.0)
        msg.temperature = random.uniform(22.0, 70.0)
        drain = random.uniform(3.0, 8.0)
        self.percentage = max(self.percentage - drain, 0.0)

        msg.percentage = self.percentage
        now = self.get_clock().now()
        msg.timestamp = now.to_msg()

        if msg.temperature > self.overheat_threshold:

            status = "OVERHEAT"
        elif msg.voltage < self.low_voltage_threshold:

            status = "SHORT"
        elif msg.percentage < self.critical_percentage_threshold:

            status = "CRITICAL"
        else:

            status = "OK"

        msg.status = status

        if self.test_stage:
            self.publisher_.publish(msg)

            self.get_logger().info(
                f"Publishing: Voltage={msg.voltage:.2f}V, Current={msg.current:.2f}A, "
                f"Percentage={msg.percentage:.2f}%, Temp={msg.temperature:.2f}C, Status={status}"
            )

            try:
                with open(self.csv_file, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        f"{msg.timestamp.sec}.{msg.timestamp.nanosec:09d}",
                        f"{msg.voltage:.2f}",
                        f"{msg.current:.2f}",
                        f"{msg.percentage:.2f}",
                        f"{msg.temperature:.2f}",
                        status
                    ])
            except Exception as e:
                self.get_logger().error(f"Failed to write to CSV file: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = BatteryStatePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
