# update discription

This is the discription of the update.

## 2026-4-15
### what was done

- add `UpperDecisionPoseInput` in `user_commands/script/upper_decision_input.py`.
- it listens to upper decision layer output (`PoseStamped`) and forwards target pose to the motion control flow.
- add switch parameter `enable_upper_decision` to control whether upper-layer input is enabled.
- default value is `False` for input side.
- add parameter `segment_pose_topic` to configure the target topic name.
- default topic is `/segment_pose`.
- add decision entry function `make_decision(elapsed_sec)`.
- this function calls external decision process and converts result to `PoseStamped`.
- add external decision process file `user_commands/script/decision_process.py`.
- function `run_decision_process(elapsed_sec)` is used as the upper-layer decision hook.
- add publisher node class `UpperDecisionPublisher` in `upper_decision_input.py`.
- it publishes decision pose messages to `/segment_pose` with configurable rate.
- add runnable script `user_commands/script/upper_decision_publisher.py`.
- it starts the upper decision publisher node directly.
- update `user_commands/CMakeLists.txt` to install the new decision scripts.

### to do

- consider about how to connect publisher and subscriber
- input the pose information to moveit-planner

## 2026-4-22
### what was done
- add `HeadlessDecisionExecutor` class in `user_commands/script/headless_decision_executor.py`.
- it executes the decision process in headless mode.
- add runnable script `user_commands/script/headless_decision_executor.py`.
- it starts the headless decision executor node directly, you can start it in simulation('use_sim_time:=True') or real world('use_sim_time:=False').
- update `user_commands/CMakeLists.txt` to install the new headless decision executor script.
- tackle the problem of state synchronization between headless decision executor and motion control flow.
- if you want to control the rate of decision process, you can add parameter `decision_rate` in `upper_decision_input.py`.
- input from of terminal's rotation changes from only quaternion to both quaternion and euler angles.
### to do
- test it in real world
- add a input form that add motion to last state.
