# ROS Tasks

## Question 1: Publisher/Subscriber Setup with Standard Message Types
- **Directory**: `Q1/kratos_shlok`
- **Approach**: Created a standard publisher and subscriber node pair, where the publisher broadcasts rover data over three separate topics using standard message types, and the subscriber listens to these topics and logs the received data. The data is pseudo random.
- **Assumptions**: None.
- **Challenges**: None significant.
- **Testing**: 
    - Initially tested by running pubsub nodes in separate terminals and observing output in both nodes.
    - Used the various probing commands in `ros2 node`, `ros2 topic` and `rqt_graph` to verify the correct functioning of the nodes and topics, as seen in the [assets](./Q1/kratos_shlok/assets) folder, and uploaded videos. 
    - Later, created a launch file to run both nodes simultaneously and verified the output in a single terminal for the bonus part of the question.
- **Limitations**: The data is pseudo random and does not represent any real rover data.

## Question 2: Publisher/Subscriber Setup with Custom Message Type - RoverStatus
- **Directory**: `Q2/kratos_shlok` , `Q2/kratos_shlok_msgs`
- **Approach**: Created a custom message type `RoverStatus` with fields for battery level, rover mode, and emergency stop. Implemented a publisher node that broadcasts this custom message and a subscriber node that listens to it and logs the received data, same as previous question. The data is still pseudo random.
- **Assumptions**: None.
- **Challenges**: Figuring out how to log cleanly and also exit cleanly on keyboard interrupt.
- **Testing**: 
    - Same as previous question, initially tested by running pubsub nodes in separate terminals and observing output in both nodes.
    - Used the various probing commands in `ros2 node`, `ros2 topic` and `rqt_graph` to verify the correct functioning of the nodes and topics.
    - Later, created a launch file to run both nodes simultaneously and verified the output in a single terminal for the bonus part of the question.
- **Limitations**: The data is pseudo random and does not represent any real rover data.

---

# ROS/TFKIK Tasks

### Question 1: Submitted on paper.
## Question 2: Robotic Arm Kinematics Inverse Kinematics Controller
- **Directory**: `TFKIK/arm_humble`
- **Approach**: 
    - First used the `ros2 run tf2_tools view_frames` and `ros2 run arm display.launch.py` to understand the TF Tree hierarchy and frames of the arm. 
    - Then worked out the relevant matrix transforms on paper to get from the world frame to the end effector frame (`wrist_output_shaft_link`).
    - Had Gemini use Inverse Kinematics to derive joint angle expressions required to reach a given end effector position. Gemini created the inverse kinematics computer function and auto implemented structural limitations it picked up from the URDF file.
    - Controller node internally keeps track of the current joint angles and uses the inverse kinematics function to compute the required joint angles to reach the desired end effector position. It then publishes these joint angles to `/joint_states` to control the arm.
    - Controller takes input by separating process into another thread.