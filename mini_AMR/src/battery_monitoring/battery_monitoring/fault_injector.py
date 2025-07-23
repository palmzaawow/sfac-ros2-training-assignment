import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from robot_interfaces.msg import BatteryState
from robot_interfaces.action import Parking
from builtin_interfaces.msg import Time


class FaultInjector(Node):
    def __init__(self):
        super().__init__('fault_injector')

        self.publisher_ = self.create_publisher(BatteryState, '/battery_state', 10)
        self.timer = self.create_timer(2.0, self.timer_callback)  

        self._action_client = ActionClient(self, Parking, 'parking')
        self._goal_sent = False
        self._goal_handle = None 
        self.test_stage = 0

    def timer_callback(self):
        msg = BatteryState()
        now = self.get_clock().now().to_msg()
        msg.timestamp = now

        if self.test_stage == 0:
            msg.status = "OK"
            msg.voltage = 48.0
            msg.percentage = 100.0
            msg.temperature = 30.0

        elif self.test_stage == 1:
            msg.status = "OVERHEAT"
            msg.voltage = 47.0
            msg.percentage = 75.0
            msg.temperature = 65.0

        elif self.test_stage == 2:
            msg.status = "CRITICAL"
            msg.voltage = 42.0
            msg.percentage = 10.0
            msg.temperature = 55.0

        elif self.test_stage == 3:
            msg.status = "OK"
            msg.voltage = 48.5
            msg.percentage = 90.0
            msg.temperature = 28.0

        elif self.test_stage == 4:
            self.send_parking_goal()

            msg.status = "OK"
            msg.voltage = 48.0
            msg.percentage = 90.0
            msg.temperature = 28.0

        self.get_logger().info(f"[Test] Publishing battery status: {msg.status}")
        self.publisher_.publish(msg)

        self.test_stage += 1
        if self.test_stage > 4:
            self.test_stage = 0

    def send_parking_goal(self):
        if self._goal_handle is not None:
            status = self._goal_handle.status
            if status not in [
                GoalStatus.STATUS_SUCCEEDED,
                GoalStatus.STATUS_CANCELED,
                GoalStatus.STATUS_ABORTED,
            ]:
                self.get_logger().warn("Previous goal still active. Wait or cancel before sending new goal.")
                return

        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Parking action server not available.")
            return

        goal_msg = Parking.Goal()
        goal_msg.mode = "normal"

        self.get_logger().info("Sending normal parking goal via action client...")

        send_goal_future = self._action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        try:
            goal_handle = future.result()
        except Exception as e:
            self.get_logger().error(f"Exception while sending goal: {e}")
            return

        if not goal_handle.accepted:
            self.get_logger().warn("Parking goal rejected by server")
            self._goal_sent = False
            self._goal_handle = None
            return

        self.get_logger().info("Parking goal accepted by server")
        self._goal_sent = True
        self._goal_handle = goal_handle

        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        try:
            result = future.result().result
            self.get_logger().info(f"Parking action finished: parked={result.parked}, report='{result.report}'")
        except Exception as e:
            self.get_logger().error(f"Failed to get result: {e}")

        self._goal_sent = False
        self._goal_handle = None  

def main(args=None):
    rclpy.init(args=args)
    node = FaultInjector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
