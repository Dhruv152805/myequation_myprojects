"""
generate_report.py
-------------------
Builds report.pdf for the 4-DOF ROS 2 URDF project using ReportLab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, PageBreak, ListFlowable, ListItem, Image)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="H1c", parent=styles["Heading1"], spaceBefore=14, spaceAfter=8))
styles.add(ParagraphStyle(name="H2c", parent=styles["Heading2"], spaceBefore=10, spaceAfter=6, textColor=colors.HexColor("#1b4d6b")))
styles.add(ParagraphStyle(name="Body", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=6))
styles.add(ParagraphStyle(name="Mono", parent=styles["Normal"], fontName="Courier", fontSize=8, leading=10))
styles.add(ParagraphStyle(name="Center", parent=styles["Normal"], alignment=1))
styles.add(ParagraphStyle(name="TitleC", parent=styles["Title"], fontSize=19))
styles.add(ParagraphStyle(name="Note", parent=styles["Normal"], fontSize=9.5, leading=13,
                           textColor=colors.HexColor("#7a3b00"), backColor=colors.HexColor("#fff4e5"),
                           borderPadding=8, spaceBefore=6, spaceAfter=10))

story = []


def h1(t): story.append(Paragraph(t, styles["H1c"]))
def h2(t): story.append(Paragraph(t, styles["H2c"]))
def body(t): story.append(Paragraph(t, styles["Body"]))
def note(t): story.append(Paragraph(t, styles["Note"]))
def mono(t): story.append(Paragraph(t.replace("\n", "<br/>"), styles["Mono"]))
def spacer(h=6): story.append(Spacer(1, h))


def styled_table(data, col_widths, header=True):
    t = Table(data, colWidths=col_widths)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b4d6b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f8fb")]),
        ]
    t.setStyle(TableStyle(style))
    return t


# =====================================================================
# COVER
# =====================================================================
story.append(Spacer(1, 55))
story.append(Paragraph("ROS 2 URDF of 4-DOF Industrial Arm", styles["TitleC"]))
spacer(10)
story.append(Paragraph("URDF Modeling of a 4-DOF Industrial Robotic Arm in ROS 2", styles["Heading2"]))
spacer(16)
story.append(Paragraph("Project Report", styles["Heading2"]))
spacer(4)
story.append(Paragraph("Industrial Training Program on Robotics and AI", styles["Body"]))
story.append(Paragraph("Submitted by: &lt;StudentName&gt;", styles["Body"]))
story.append(Paragraph("Date: 20 July 2026", styles["Body"]))
spacer(16)
note("<b>Environment note:</b> This report, the URDF/xacro model, and the launch files were "
     "built and statically validated (well-formed XML, single-root kinematic tree, joint "
     "limit sanity checks) in an environment without ROS 2 / RViz2 installed. The images in "
     "Sections 5 and 6 below are geometry-accurate schematics generated directly from this "
     "URDF's own joint origins/axes, used as a stand-in for real RViz/TF-tree screenshots. "
     "Section 8 gives the exact commands to run on a real ROS 2 (Humble/Iron) workstation to "
     "capture the actual RViz and <code>view_frames</code> screenshots required by the "
     "submission guidelines.")
story.append(PageBreak())

# =====================================================================
# 1. PROBLEM STATEMENT
# =====================================================================
h1("1. Problem Statement")
body("Design and implement a ROS 2 URDF model of a 4-DOF industrial robotic arm that "
     "defines all links and joints correctly, includes visual and collision elements, "
     "uses proper joint types and limits, loads successfully in RViz, and displays a "
     "correct TF tree.")

# =====================================================================
# 2. Q1 ROBOT STRUCTURE DESIGN
# =====================================================================
h1("2. Robot Structure Design (Question 1)")
body("The arm is modelled as a serial kinematic chain with <b>4 revolute joints</b> "
     "(the required 4 degrees of freedom) plus 2 fixed joints used purely for mounting "
     "the base to a <code>world</code> reference frame and mounting a tool-point frame "
     "at the end effector (fixed joints do not count toward the DOF total and add no "
     "TF-tree ambiguity).")

struct_data = [
    ["Link", "Role", "Connected via joint", "Joint type", "Axis"],
    ["world", "Global reference frame", "-", "-", "-"],
    ["base_link", "Fixed pedestal", "world_to_base", "fixed", "-"],
    ["link1", "Waist / yaw stage", "joint1", "revolute", "Z"],
    ["link2", "Upper arm (shoulder)", "joint2", "revolute", "Y"],
    ["link3", "Forearm (elbow)", "joint3", "revolute", "Y"],
    ["link4", "Wrist", "joint4", "revolute", "Y"],
    ["tool_link", "End-effector / tool point", "tool_joint", "fixed", "-"],
]
story.append(styled_table(struct_data, [28*mm, 45*mm, 32*mm, 22*mm, 15*mm]))
spacer(10)
body("This gives a classic articulated-arm layout: <b>waist (yaw) &rarr; shoulder (pitch) "
     "&rarr; elbow (pitch) &rarr; wrist (pitch)</b>, which is representative of common "
     "4-DOF industrial arm configurations (e.g. pick-and-place arms), while remaining "
     "simple enough to fully hand-verify.")

h2("Kinematic Tree")
mono("world\n"
     "  base_link\n"
     "    link1   (joint1: revolute, Z)\n"
     "      link2   (joint2: revolute, Y)\n"
     "        link3   (joint3: revolute, Y)\n"
     "          link4   (joint4: revolute, Y)\n"
     "            tool_link   (tool_joint: fixed)")

# =====================================================================
# 3. Q2 URDF LINK DEFINITION
# =====================================================================
h1("3. URDF Link Definition (Question 2)")
body("Every link (except the abstract <code>world</code> frame) defines matching "
     "<code>&lt;visual&gt;</code> and <code>&lt;collision&gt;</code> geometry, plus an "
     "<code>&lt;inertial&gt;</code> block with mass and a diagonal inertia tensor computed "
     "analytically from standard solid-geometry formulas "
     "(box: I<sub>xx</sub>=m(y&sup2;+z&sup2;)/12, etc.; cylinder about its own axis: "
     "I<sub>zz</sub>=mr&sup2;/2, I<sub>xx</sub>=I<sub>yy</sub>=m(3r&sup2;+l&sup2;)/12), "
     "implemented as reusable xacro macros (<code>box_inertial</code>, "
     "<code>cylinder_inertial</code>) so every link stays consistent.")

link_data = [
    ["Link", "Geometry", "Dimensions (m)", "Mass (kg)", "Material"],
    ["base_link", "cylinder", "r=0.090, l=0.050", "1.5", "dark_grey"],
    ["link1", "cylinder", "r=0.060, l=0.150", "1.0", "grey"],
    ["link2", "box", "0.06 x 0.06 x 0.35", "1.2", "orange"],
    ["link3", "box", "0.05 x 0.05 x 0.30", "0.9", "orange"],
    ["link4", "cylinder", "r=0.035, l=0.100", "0.4", "grey"],
    ["tool_link", "box", "0.02 x 0.02 x 0.02", "0.05", "black"],
]
story.append(styled_table(link_data, [24*mm, 22*mm, 45*mm, 22*mm, 25*mm]))
spacer(10)
body("In every link, the <code>&lt;collision&gt;</code> geometry is identical to the "
     "<code>&lt;visual&gt;</code> geometry (the same primitive, same origin) &mdash; a "
     "deliberate simplification appropriate for this training project, since no meshes "
     "are used. Each link's geometry origin is offset by half its length along local Z, "
     "so that the link visually spans from its parent joint to its child joint.")

# =====================================================================
# 4. Q3 JOINT DEFINITION
# =====================================================================
h1("4. Joint Definition (Question 3)")
body("All four moving joints are <code>revolute</code>, each with an explicit "
     "<code>&lt;axis&gt;</code>, a <code>&lt;limit&gt;</code> (lower/upper in radians, "
     "plus effort in N&middot;m and velocity in rad/s), and a <code>&lt;dynamics&gt;</code> "
     "damping/friction term. Parent-child relationships follow the kinematic tree in "
     "Section 2 exactly, so the tree has a single unambiguous root (<code>world</code>).")

joint_data = [
    ["Joint", "Parent", "Child", "Type", "Axis", "Limits (deg)", "Effort / Vel."],
    ["world_to_base", "world", "base_link", "fixed", "-", "-", "-"],
    ["joint1", "base_link", "link1", "revolute", "Z", "-180 to +180", "50 N.m / 2.0 rad/s"],
    ["joint2", "link1", "link2", "revolute", "Y", "-90 to +90", "80 N.m / 1.5 rad/s"],
    ["joint3", "link2", "link3", "revolute", "Y", "-150 to +150", "60 N.m / 1.5 rad/s"],
    ["joint4", "link3", "link4", "revolute", "Y", "-90 to +90", "20 N.m / 2.0 rad/s"],
    ["tool_joint", "link4", "tool_link", "fixed", "-", "-", "-"],
]
story.append(styled_table(joint_data, [24*mm, 22*mm, 22*mm, 18*mm, 12*mm, 28*mm, 33*mm]))
spacer(10)
body("Joint origins are placed at the tip of the parent link (i.e. <code>origin xyz = "
     "\"0 0 &lt;parent_link_length&gt;\"</code>), so each joint's rotation axis passes "
     "through the physical pivot point between consecutive links, matching how the "
     "corresponding real servo/actuator would be mounted.")

# =====================================================================
# 5. Q4 ASSEMBLY VALIDATION
# =====================================================================
h1("5. Assembly Validation (Question 4)")
body("All 7 links and 6 joints are assembled into <code>4dof_arm.urdf.xacro</code> "
     "(parameterized source) and its flattened, standard-URDF equivalent "
     "<code>4dof_arm.urdf</code> (included for reference / for loading without xacro). "
     "Both were checked for XML well-formedness with <code>xmllint</code>, and the "
     "resulting robot graph was statically validated (parent/child references resolve, "
     "single connected tree with no cycles, every revolute joint has an axis and a "
     "lower&lt;upper limit, every physical link has matching visual+collision geometry). "
     "Output of that validator:")

validator_output = open("report_assets/validation_output.txt").read()
mono(validator_output)

body("On a real ROS 2 install, the standard equivalent checks are:")
mono("check_urdf 4dof_arm.urdf\n"
     "ros2 run xacro xacro 4dof_arm.urdf.xacro -o /tmp/4dof_arm.urdf   # process xacro\n"
     "check_urdf /tmp/4dof_arm.urdf                                    # validate result")

# =====================================================================
# 6. Q5 RVIZ VISUALIZATION
# =====================================================================
h1("6. RViz Visualization (Question 5)")
body("<code>launch/display.launch.py</code> starts <code>robot_state_publisher</code> "
     "(fed by <code>xacro</code> processing the model at launch time), "
     "<code>joint_state_publisher_gui</code> (sliders for the 4 revolute joints), and "
     "<code>rviz2</code> pre-loaded with <code>rviz/urdf_config.rviz</code>, which enables "
     "the RobotModel and TF displays with Fixed Frame = <code>world</code>.")
body("The two renders below are geometry-accurate schematics computed directly from this "
     "URDF's joint origins, axes, and link lengths (see "
     "<code>render_arm_schematic.py</code>) &mdash; they show exactly what RViz's "
     "RobotModel display would draw at each joint configuration, and are included here "
     "only because this build environment has no RViz2 available. Replace them with real "
     "RViz screenshots on your ROS 2 workstation per Section 8.")

story.append(Image("report_assets/arm_home_config.png", width=80*mm, height=80*mm))
spacer(4)
story.append(Image("report_assets/arm_bent_config.png", width=80*mm, height=80*mm))
spacer(8)
body("<b>Home configuration</b> (all joints at 0&deg;): the arm stands fully vertical, "
     "base &rarr; waist &rarr; upper arm &rarr; forearm &rarr; wrist all stacked along +Z. "
     "<b>Sample configuration</b> (q1=45&deg;, q2=-30&deg;, q3=60&deg;, q4=-25&deg;) shows "
     "the waist rotated about Z and the arm bending forward through the shoulder/elbow/wrist "
     "pitch joints, as expected for this kinematic design.")

# =====================================================================
# 7. Q6 TF TREE VERIFICATION
# =====================================================================
h1("7. TF Tree Verification (Question 6)")
body("With <code>robot_state_publisher</code> running, it broadcasts one TF transform per "
     "joint (fixed joints publish a constant transform; revolute joints publish a transform "
     "that updates live from <code>/joint_states</code>, as driven by "
     "<code>joint_state_publisher_gui</code>). The resulting TF tree exactly mirrors the "
     "URDF kinematic tree from Section 2:")

story.append(Image("report_assets/tf_tree.png", width=170*mm, height=170*mm*117/2252))
spacer(8)
body("This diagram matches what <code>ros2 run tf2_tools view_frames</code> (which writes "
     "<code>frames.pdf</code>) or <code>ros2 run rqt_tf_tree rqt_tf_tree</code> (live view) "
     "would render from the real running system: 7 frames, 6 edges, single root "
     "(<code>world</code>), no broken or duplicate branches &mdash; consistent with the "
     "structural validation in Section 5.")

# =====================================================================
# 8. TOOLS + HOW TO REPRODUCE ON A REAL ROS 2 SYSTEM
# =====================================================================
h1("8. Tools Used / How to Reproduce")
story.append(ListFlowable([
    ListItem(Paragraph("ROS 2 (Humble / Iron)", styles["Body"])),
    ListItem(Paragraph("URDF / Xacro", styles["Body"])),
    ListItem(Paragraph("RViz2", styles["Body"])),
    ListItem(Paragraph("robot_state_publisher, joint_state_publisher_gui", styles["Body"])),
], bulletType="bullet"))

h2("Build and launch")
mono("cd ~/ros2_ws/src\n"
     "cp -r ros2_urdf_4dof_arm .              # this package\n"
     "cd ~/ros2_ws\n"
     "colcon build --packages-select ros2_urdf_4dof_arm\n"
     "source install/setup.bash\n"
     "ros2 launch ros2_urdf_4dof_arm display.launch.py")

h2("Capture the required screenshots")
mono("# In RViz2 (opened by the launch file): Screenshot the window\n"
     "#   showing RobotModel + TF displays, Fixed Frame = world.\n"
     "\n"
     "# TF tree (in a second terminal, ROS 2 sourced, arm still running):\n"
     "ros2 run tf2_tools view_frames\n"
     "#   generates frames_<timestamp>.pdf in the current directory\n"
     "#   -- screenshot / export this as the TF tree image.\n"
     "\n"
     "# Or, for a live interactive view:\n"
     "ros2 run rqt_tf_tree rqt_tf_tree")

# =====================================================================
# 9. CONCLUSION
# =====================================================================
h1("9. Conclusion")
body("The project delivers a complete, modular ROS 2 package "
     "(<code>ros2_urdf_4dof_arm</code>) containing a parameterized xacro model of a 4-DOF "
     "industrial arm with correct link/joint definitions, visual and collision geometry, "
     "proper joint types and limits, a launch file that assembles "
     "robot_state_publisher + joint_state_publisher_gui + RViz2, and a pre-configured RViz "
     "view. The kinematic structure was statically validated to be a single, cycle-free "
     "tree with fully-specified joint limits, and the expected RViz appearance and TF tree "
     "shape were derived directly from the model's own geometry for inclusion in this "
     "report. Section 8 gives exact commands to reproduce the live RViz and "
     "<code>view_frames</code> screenshots on a ROS 2 workstation.")

doc = SimpleDocTemplate("report.pdf", pagesize=A4,
                         leftMargin=20*mm, rightMargin=20*mm,
                         topMargin=18*mm, bottomMargin=18*mm,
                         title="ROS 2 URDF 4-DOF Arm Report")
doc.build(story)
print("report.pdf generated.")
