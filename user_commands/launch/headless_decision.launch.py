from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os

def generate_launch_description():
    # 声明是否使用仿真的参数（默认 false, 即连接真机）
    # 在命令行可以用: ros2 launch user_commands headless_decision.launch.py use_sim:=true 切换仿真
    use_sim = LaunchConfiguration('use_sim')
    use_sim_arg = DeclareLaunchArgument(
        'use_sim',
        default_value='false',
        description='Whether to use simulation (true) or real robot (false)'
    )

    moveit_config_share = get_package_share_directory("jaka_robot_moveit_config")
    
    # 1. 启动底层 MoveIt 框架
    rviz_launch_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(moveit_config_share, "launch", "demo.launch.py")
        ),
        launch_arguments={"use_rviz_sim": use_sim}.items()
    )

    # 2. 启动执行节点 moveit_client (C++)
    moveit_client_node = Node(
        package="user_commands",
        executable="moveit_client",
        output="screen",
    )

    # 3. 启动无头通讯转换桥梁 (Python)
    headless_decision_executor_node = Node(
        package="user_commands",
        executable="headless_decision_executor.py",
        output="screen",
    )

    # 4. 启动负责画圆或上层算法的心智决策节点 (Python)
    upper_decision_publisher_node = Node(
        package="user_commands",
        executable="upper_decision_publisher.py",
        output="screen",
    )

    # 通过定时器顺序启动，防止底层没起好导致上层建立链接失败
    # MoveIt底层启动耗时，因此延迟加载上层控制节点
    start_client = TimerAction(period=2.0, actions=[moveit_client_node])
    start_executor = TimerAction(period=4.0, actions=[headless_decision_executor_node])
    start_publisher = TimerAction(period=5.0, actions=[upper_decision_publisher_node])

    return LaunchDescription([
        use_sim_arg,
        rviz_launch_node,
        start_client,
        start_executor,
        start_publisher
    ])
