#!/usr/bin/env python3

from math import cos, sin


def run_decision_process(elapsed_sec: float):
    """Sample upper-layer decision logic.

    Replace this function with your planner/decision pipeline output.
    Returns a dict that can be converted to geometry_msgs/PoseStamped.
    """
    radius = 0.05
    omega = 0.3

    return {
        "x": 0.35 + radius * cos(omega * elapsed_sec),
        "y": radius * sin(omega * elapsed_sec),
        "z": 0.35,
        "rx": 0.0,
        "ry": 0.0,
        "rz": 0.0,
        "frame_id": "Link_0",
    }
