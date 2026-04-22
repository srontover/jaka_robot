#!/usr/bin/env python3

import sys
import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from jaka_msgs.msg import MyPoseCmd
from upper_decision_input import UpperDecisionPoseInput

def quat_to_euler(qx, qy, qz, qw):
    """四元数转欧拉角 (rx, ry, rz) 单位: 弧度"""
    # roll (rx)
    sinr_cosp = 2.0 * (qw * qx + qy * qz)
    cosr_cosp = 1.0 - 2.0 * (qx * qx + qy * qy)
    rx = math.atan2(sinr_cosp, cosr_cosp)
    
    # pitch (ry)
    sinp = 2.0 * (qw * qy - qz * qx)
    if abs(sinp) >= 1:
        ry = math.copysign(math.pi / 2, sinp)
    else:
        ry = math.asin(sinp)
        
    # yaw (rz)
    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    rz = math.atan2(siny_cosp, cosy_cosp)
    
    return rx, ry, rz

class HeadlessDecisionExecutor(Node):
    """
    无 UI 版本的决策执行节点。
    用于在终端后台或仿真/真机中运行，
    将 /segment_pose 的 PoseStamped (四元数) 转换为 /pose_cmd 的 MyPoseCmd (欧拉角) 下发。
    """
    def __init__(self):
        super().__init__('headless_decision_executor')
        
        # 1. 创建发布者，发给底层 JAKA 控制
        self.pose_cmd_pub = self.create_publisher(MyPoseCmd, "pose_cmd", 10)
        
        # 2. 挂载上层决策输入接口 (监听 /segment_pose)
        self.upper_decision = UpperDecisionPoseInput(
            node=self,
            callback=self.upper_decision_callback,
            default_topic="/segment_pose",
            default_enable=True, # 默认开启
            default_rate_hz=10.0
        )
        self.upper_decision.setup()
        
        self.get_logger().info("无 UI 决策执行节点已启动！正在监听 /segment_pose 并下发到 /pose_cmd")

    def upper_decision_callback(self, msg: PoseStamped):
        """当接收到决策层位姿时触发，解析并转换格式，直接下发到机器人"""
        x = msg.pose.position.x
        y = msg.pose.position.y
        z = msg.pose.position.z
        
        qx = msg.pose.orientation.x
        qy = msg.pose.orientation.y
        qz = msg.pose.orientation.z
        qw = msg.pose.orientation.w
        
        # 核心：将空间姿态（四元数）转为底层所支持的欧拉角 (rx, ry, rz)
        rx, ry, rz = quat_to_euler(qx, qy, qz, qw)
        
        # 构造 MyPoseCmd
        cmd_msg = MyPoseCmd()
        cmd_msg.x = float(x)
        cmd_msg.y = float(y)
        cmd_msg.z = float(z)
        cmd_msg.rx = float(rx)
        cmd_msg.ry = float(ry)
        cmd_msg.rz = float(rz)
        cmd_msg.cartesian_path = True
        
        # 发布给底层
        self.pose_cmd_pub.publish(cmd_msg)
        
        # 在终端打印执行状态，将米缩放为毫米便于直观调试
        self.get_logger().info(
            f"下发目标 -> x={x*1000:.1f}mm, y={y*1000:.1f}mm, z={z*1000:.1f}mm | rx={rx:.3f}, ry={ry:.3f}, rz={rz:.3f}"
        )

def main(args=None):
    rclpy.init(args=args)
    node = HeadlessDecisionExecutor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("正在退出节点...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
