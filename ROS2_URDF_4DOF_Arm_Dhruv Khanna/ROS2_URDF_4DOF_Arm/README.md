# ros2_urdf_4dof_arm

ROS 2 URDF/Xacro model of a 4-DOF industrial robotic arm, with an RViz2
display launch file. Built for the *Industrial Training Program on
Robotics and AI* mini project.

## Structure

```
ros2_urdf_4dof_arm/
├── package.xml
├── CMakeLists.txt
├── urdf/
│   ├── 4dof_arm.urdf.xacro   # parameterized source (edit this)
│   └── 4dof_arm.urdf         # flattened plain URDF (reference / no-xacro fallback)
├── launch/
│   └── display.launch.py     # robot_state_publisher + joint_state_publisher_gui + rviz2
├── rviz/
│   └── urdf_config.rviz      # pre-configured RobotModel + TF display
├── report_assets/            # figures used by generate_report.py / report.pdf
├── generate_report.py        # rebuilds report.pdf from the assets above
└── report.pdf
```

## Kinematic structure

```
world -> base_link -> link1 (joint1, revolute, Z, waist)
                    -> link2 (joint2, revolute, Y, shoulder)
                    -> link3 (joint3, revolute, Y, elbow)
                    -> link4 (joint4, revolute, Y, wrist)
                    -> tool_link (tool_joint, fixed, end-effector)
```

4 revolute joints = 4 DOF. `world_to_base` and `tool_joint` are fixed
joints for mounting/tooling only.

## Build & run (ROS 2 Humble / Iron)

```bash
cd ~/ros2_ws/src
cp -r ros2_urdf_4dof_arm .
cd ~/ros2_ws
colcon build --packages-select ros2_urdf_4dof_arm
source install/setup.bash
ros2 launch ros2_urdf_4dof_arm display.launch.py
```

This opens RViz2 (RobotModel + TF displays, Fixed Frame = `world`) and
a `joint_state_publisher_gui` window with sliders for `joint1`..`joint4`
so you can drive the arm and watch the TF tree update live.

## Verifying the TF tree

With the launch file running, in a second terminal (ROS 2 sourced):

```bash
ros2 run tf2_tools view_frames      # writes frames_<timestamp>.pdf
# or, live:
ros2 run rqt_tf_tree rqt_tf_tree
```

## Validating the URDF without ROS 2

Two standalone checks (no ROS 2 required) are included at the top
level of the project bundle:

```bash
python3 flatten_xacro.py urdf/4dof_arm.urdf.xacro urdf/4dof_arm.urdf
python3 validate_urdf_structure.py urdf/4dof_arm.urdf
```

`flatten_xacro.py` expands the xacro properties/macros/math used in
this specific file into plain URDF (a stand-in for the real `xacro`
CLI when it isn't installed). `validate_urdf_structure.py` checks the
link/joint graph is a single connected, cycle-free tree with a unique
root, and that every revolute joint has an axis and valid limits.

On a real ROS 2 install, use the standard tools instead:

```bash
ros2 run xacro xacro urdf/4dof_arm.urdf.xacro -o /tmp/4dof_arm.urdf
check_urdf /tmp/4dof_arm.urdf
```

## Note on report_assets/ images

`arm_home_config.png`, `arm_bent_config.png`, and `tf_tree.png` are
geometry-accurate schematics generated directly from this URDF's own
joint origins/axes (see `render_arm_schematic.py` / the graphviz TF
diagram), used in `report.pdf` in place of real RViz/`view_frames`
screenshots because the environment used to build this project has no
ROS 2 / RViz2 installed. Replace them with real screenshots captured
on a ROS 2 workstation before final submission, per the assignment's
submission guidelines.
