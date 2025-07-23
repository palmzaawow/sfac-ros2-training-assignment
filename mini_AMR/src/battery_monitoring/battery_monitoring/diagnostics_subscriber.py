import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from robot_interfaces.msg import BatteryState
from robot_interfaces.action import Parking
from datetime import datetime
import csv
import os

class DiagnosticsSubscriber(Node):
    def __init__(self):
        super().__init__('diagnostics_subscriber')

        self.subscription = self.create_subscription(
            BatteryState,
            '/battery_state',
            self.battery_callback,
            10
        )

        self._action_client = ActionClient(self, Parking, 'parking')

        self.event_log_file = 'event_log.csv'

        if not os.path.isfile(self.event_log_file):
            with open(self.event_log_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'status', 'action'])

        self._goal_sent = False

    def battery_callback(self, msg: BatteryState):

        status = getattr(msg, 'status', 'OK')  

        timestamp = self.get_formatted_time(msg.timestamp.sec, msg.timestamp.nanosec)

        if status != "OK":
   
            action = self.get_action_for_status(status)

            self.get_logger().warn(f"WARNING — [{timestamp}] — Status: {status} — Take Action!")

            try:

                with open(self.event_log_file, mode='a', newline='') as f:

                    writer = csv.writer(f)
                    writer.writerow([timestamp, status, action])

            except Exception as e:

                self.get_logger().error(f"Failed to write to event_log.csv: {e}")

      
            if status == "CRITICAL":

                self.get_logger().info("CRITICAL status detected — Prepare to call parking action server.")
                self.send_parking_goal()


    def send_parking_goal(self):

        if not self._action_client.server_is_ready():
            self.get_logger().warn("Parking action server not ready, waiting...")
            self._action_client.wait_for_server()

        goal_msg = Parking.Goal()
        goal_msg.mode = "emergency"

        self.get_logger().info("Sending emergency parking goal via action client...")

        send_goal_future = self._action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.get_logger().warn("Parking goal rejected by server")
            self._goal_sent = False
            return

        self.get_logger().info("Parking goal accepted by server")
        self._goal_sent = True

        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f"Parking action finished: parked={result.parked}, report='{result.report}'")
        self._goal_sent = False


    def get_action_for_status(self, status: str) -> str:

        if status == "OVERHEAT":

            return "SLOW DOWN"
        elif status == "SHORT":

            return "WATCH"
        elif status == "CRITICAL":

            return "PARK"
        else:

            return "WATCH"

    def get_formatted_time(self, sec: int, nanosec: int) -> str:
   
        dt = datetime.fromtimestamp(sec + nanosec * 1e-9)
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  

def main(args=None):
    rclpy.init(args=args)
    diagnostics_subscriber = DiagnosticsSubscriber()
    rclpy.spin(diagnostics_subscriber)
    diagnostics_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
