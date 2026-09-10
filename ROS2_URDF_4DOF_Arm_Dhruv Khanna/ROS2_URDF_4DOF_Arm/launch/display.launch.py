"""
display.launch.py
------------------
Launches:
  - robot_state_publisher (publishes /robot_description and TF from
    joint states, using the URDF produced from the xacro file)
  - joint_state_publisher_gui (sliders to manually move each of the 4
    revolute joints, publishing /joint_states so you can see the TF
    tree/robot move live in RViz)
  - rviz2, pre-loaded with rviz/urdf_config.rviz

Usage:
    ros2 launch ros2_urdf_4dof_arm display.launch.py

To inspect the TF tree once this is running (in another terminal):
    ros2 run tf2_tools view_frames
    # or, live:
    ros2 run rqt_tf_tree rqt_tf_tree
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('ros2_urdf_4dof_arm')

    xacro_file = os.path.join(pkg_share, 'urdf', '4dof_arm.urdf.xacro')
    default_rviz_config = os.path.join(pkg_share, 'rviz', 'urdf_config.rviz')

    gui_arg = DeclareLaunchArgument(
        'use_joint_state_publisher_gui',
        default_value='true',
        description='Launch joint_state_publisher_gui to manually drive the 4 joints'
    )
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_config,
        description='Path to the RViz config file'
    )

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]),
        value_type=str
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}]
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
        condition=IfCondition(LaunchConfiguration('use_joint_state_publisher_gui'))
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')]
    )

    return LaunchDescription([
        gui_arg,
        rviz_config_arg,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node,
    ])
