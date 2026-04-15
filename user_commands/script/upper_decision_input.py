#!/usr/bin/env python3

from math import cos, sin
from typing import Optional

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped


class UpperDecisionPoseInput:
    def __init__(self, node, callback, default_topic: str = "/segment_pose", default_enable: bool = False, default_rate_hz: float = 10.0):
        self.node = node
        self.callback = callback
        self.enable_upper_decision: bool = default_enable
        self.segment_pose_topic: str = default_topic
        self.subscription: Optional[object] = None
        self.input_rate_hz: float = default_rate_hz

    def setup(self) -> None:
        self.node.declare_parameter("enable_upper_decision", self.enable_upper_decision)
        self.node.declare_parameter("segment_pose_topic", self.segment_pose_topic)
        self.node.declare_parameter("input_rate_hz", self.input_rate_hz)
        self.enable_upper_decision = bool(
            self.node.get_parameter("enable_upper_decision").value
        )
        self.segment_pose_topic = str(
            self.node.get_parameter("segment_pose_topic").value
        )
        self.input_rate_hz = float(
            self.node.get_parameter("input_rate_hz").value
        )

        if self.enable_upper_decision:
            self.subscription = self.node.create_subscription(
                PoseStamped, self.segment_pose_topic, self.callback, self.input_rate_hz
            )
            self.node.get_logger().info(
                f"upper decision input enabled on topic {self.segment_pose_topic}"
            )
        else:
            self.node.get_logger().info("upper decision input disabled")


try:
    from decision_process import run_decision_process
except ImportError:
    # Fallback used if decision_process.py is not available in some runtime path.
    def run_decision_process(elapsed_sec: float):
        radius = 0.05
        omega = 0.3
        return {
            "x": 0.35 + radius * cos(omega * elapsed_sec),
            "y": radius * sin(omega * elapsed_sec),
            "z": 0.35,
            "qx": 0.0,
            "qy": 0.0,
            "qz": 0.0,
            "qw": 1.0,
            "frame_id": "Link_0",
        }

def make_decision(elapsed_sec: float) -> PoseStamped:
    """Call the external decision process and convert result to PoseStamped."""
    decision = run_decision_process(elapsed_sec)

    msg = PoseStamped()
    msg.header.frame_id = str(decision.get("frame_id", "Link_0"))
    msg.pose.position.x = float(decision.get("x", 0.35))
    msg.pose.position.y = float(decision.get("y", 0.0))
    msg.pose.position.z = float(decision.get("z", 0.35))
    msg.pose.orientation.x = float(decision.get("qx", 0.0))
    msg.pose.orientation.y = float(decision.get("qy", 0.0))
    msg.pose.orientation.z = float(decision.get("qz", 0.0))
    msg.pose.orientation.w = float(decision.get("qw", 1.0))
    return msg


class UpperDecisionPublisher(Node):
    """Publish upper-layer decision pose to /segment_pose periodically."""

    def __init__(self, decision_rate_hz: float = 10.0, topic_name: str = "/segment_pose", enable_upper_decision: bool = True):
        super().__init__("upper_decision_publisher")
        self.decision_rate_hz = decision_rate_hz

        self.declare_parameter("enable_upper_decision", enable_upper_decision)
        if enable_upper_decision:
            self.declare_parameter("segment_pose_topic", topic_name)
            self.declare_parameter("decision_rate_hz", self.decision_rate_hz)

        self.segment_pose_topic = str(self.get_parameter("segment_pose_topic").value)
        self.decision_rate_hz = float(self.get_parameter("decision_rate_hz").value)
        self.enable_upper_decision = bool(self.get_parameter("enable_upper_decision").value)

        if self.decision_rate_hz <= 0.0:
            self.decision_rate_hz = 10.0

        if self.enable_upper_decision:
            self.publisher = self.create_publisher(PoseStamped, self.segment_pose_topic, self.decision_rate_hz)
            self.start_time = self.get_clock().now()
            period = 1.0 / self.decision_rate_hz
            self.timer = self.create_timer(period, self._on_timer)

            self.get_logger().info(
                f"upper decision publisher started, topic={self.segment_pose_topic}, rate={self.decision_rate_hz}Hz"
            )
        else:
            self.get_logger().info("upper decision publisher disabled")

    def _on_timer(self) -> None:
        now = self.get_clock().now()
        elapsed = (now - self.start_time).nanoseconds / 1e9
        msg = make_decision(elapsed)
        msg.header.stamp = now.to_msg()
        self.publisher.publish(msg)


def run_upper_decision_publisher() -> None:
    rclpy.init()
    node = UpperDecisionPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    run_upper_decision_publisher()