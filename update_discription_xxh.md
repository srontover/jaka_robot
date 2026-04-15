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