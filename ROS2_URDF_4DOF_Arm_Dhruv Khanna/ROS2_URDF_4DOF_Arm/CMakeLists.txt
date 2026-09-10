cmake_minimum_required(VERSION 3.8)
project(ros2_urdf_4dof_arm)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf launch rviz meshes
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
