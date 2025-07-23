import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from action_msgs.msg import GoalStatus
from robot_interfaces.action import Parking
from robot_interfaces.msg import BatteryState
from datetime import datetime
import time
import csv
import os

class ParkingActionServerNode(Node):
    def __init__(self):
        super().__init__('parking_action_server')

        self._callback_group = ReentrantCallbackGroup()
        self._action_server = ActionServer(
            self,
            Parking,
            'parking',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self._callback_group
        )

        self.log_file = 'parking_log.csv'
        if not os.path.isfile(self.log_file):
            with open(self.log_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'mode', 'state', 'report'])

        self.system_status = "CRITICAL"
        self._goal_handle = None
        self._should_abort = False

        self.create_subscription(
            BatteryState,
            '/battery_state',
            self.battery_callback,
            10,
            callback_group=self._callback_group
        )

    def goal_callback(self, goal_request):
        self.get_logger().info(f"Received goal request: mode={goal_request.mode}")

        if self._goal_handle and self._goal_handle.is_active:
            self.get_logger().warn("Preempting current goal due to new goal request.")
            self._should_abort = True  

        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info("Cancel requested by client.")
        self._should_abort = True
        return CancelResponse.ACCEPT

    def battery_callback(self, msg):
        self.system_status = getattr(msg, 'status', 'OK')
        self.get_logger().info(f"[Battery Callback] Status = {self.system_status}")

        if self.system_status == "OK" and self._goal_handle and self._goal_handle.is_active:
            self.get_logger().warn("Battery recovered to OK — initiating abort.")
            self._should_abort = True

    def execute_callback(self, goal_handle):
        self._goal_handle = goal_handle
        self._should_abort = False

        mode = goal_handle.request.mode
        feedback_msg = Parking.Feedback()
        result = Parking.Result()

        self.log_parking_event(mode, "started", "Parking initiated")

        steps = [
            ("Aligning to parking spot...", 20),
            ("Moving into slot...", 60),
            ("Adjusting position...", 90),
            ("Parking complete!", 100)
        ]

        interval = 0.2 if mode == "emergency" else 0.5

        for status, percent in steps:
            start_time = time.time()

            while (time.time() - start_time) < interval:
                if self._should_abort or goal_handle.is_cancel_requested:
                    result.parked = False
                    if goal_handle.is_cancel_requested:
                        result.report = "Parking canceled by client request."
                        return self.finalize_goal(goal_handle, result, mode, "canceled")
                    else:
                        result.report = "Parking aborted due to battery recovery or preemption."
                        return self.finalize_goal(goal_handle, result, mode, "aborted")

                time.sleep(0.1)

            feedback_msg.status = status
            feedback_msg.percent_complete = percent
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f"[{mode}] Feedback: {status} ({percent}%)")

        result.parked = True
        result.report = "Vehicle parked successfully."
        return self.finalize_goal(goal_handle, result, mode, "completed")

    def finalize_goal(self, goal_handle, result, mode, state):
        try:
            if state == "canceled":
                goal_handle.canceled()
            elif state == "aborted":
                goal_handle.abort()
            else:
                goal_handle.succeed()
        except Exception as e:
            self.get_logger().error(f"Goal finalization failed: {e}")

        self.log_parking_event(mode, state, result.report)
        self._goal_handle = None
        return result

    def log_parking_event(self, mode, state, report):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(self.log_file, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, mode, state, report])
        except Exception as e:
            self.get_logger().error(f"Log write failed: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = ParkingActionServerNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
