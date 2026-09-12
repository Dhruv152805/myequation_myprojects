"""
render_arm_schematic.py
------------------------
Renders a 3D schematic of the 4-DOF arm directly from the same joint
origins / axes / link geometry defined in 4dof_arm.urdf.xacro, at a
chosen joint configuration. This is NOT a substitute for a real RViz
screenshot (that requires an actual ROS 2 + RViz2 environment, which
this sandbox does not have) -- it is a geometry-accurate cross-check
used only in the report to illustrate the expected pose, generated
directly from the design data so it cannot drift out of sync with the
URDF.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# link "reach" lengths (m), taken directly from urdf.xacro properties
BASE_LENGTH = 0.05
LINK1_LENGTH = 0.15
LINK2_LENGTH = 0.35
LINK3_LENGTH = 0.30
LINK4_LENGTH = 0.10
TOOL_LENGTH = 0.02


def rot_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def rot_y(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def chain_points(q1, q2, q3, q4):
    """Return the list of joint/frame origins in the world frame."""
    T = np.eye(4)
    pts = [T[:3, 3].copy()]  # world

    def apply(Tm, R, t):
        A = np.eye(4)
        A[:3, :3] = R
        A[:3, 3] = t
        return Tm @ A

    T = apply(T, np.eye(3), [0, 0, 0])            # world -> base_link
    pts.append(T[:3, 3].copy())
    T = apply(T, np.eye(3), [0, 0, BASE_LENGTH])  # base top
    pts.append(T[:3, 3].copy())

    T = apply(T, rot_z(q1), [0, 0, 0])            # joint1
    T = apply(T, np.eye(3), [0, 0, LINK1_LENGTH])  # link1 top
    pts.append(T[:3, 3].copy())

    T = apply(T, rot_y(q2), [0, 0, 0])            # joint2
    T = apply(T, np.eye(3), [0, 0, LINK2_LENGTH])
    pts.append(T[:3, 3].copy())

    T = apply(T, rot_y(q3), [0, 0, 0])            # joint3
    T = apply(T, np.eye(3), [0, 0, LINK3_LENGTH])
    pts.append(T[:3, 3].copy())

    T = apply(T, rot_y(q4), [0, 0, 0])            # joint4
    T = apply(T, np.eye(3), [0, 0, LINK4_LENGTH])
    pts.append(T[:3, 3].copy())

    T = apply(T, np.eye(3), [0, 0, TOOL_LENGTH])  # tool_link
    pts.append(T[:3, 3].copy())

    return np.array(pts)


def render(q_deg, title, out_path):
    q1, q2, q3, q4 = np.radians(q_deg)
    pts = chain_points(q1, q2, q3, q4)

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='3d')

    # thick line segments colored per link, roughly matching URDF materials
    seg_colors = ['#333333', '#333333', '#999999', '#ff7300', '#ff7300', '#999999', '#111111']
    seg_widths = [10, 6, 6, 10, 10, 8, 6]
    for i in range(len(pts) - 1):
        ax.plot(*zip(pts[i], pts[i + 1]), color=seg_colors[i % len(seg_colors)],
                linewidth=seg_widths[i % len(seg_widths)], solid_capstyle='round')

    # joint markers
    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], color='#1b4d6b', s=40, depthshade=True)

    labels = ['world', 'base_link', '(base top)', 'link1', 'link2', 'link3', 'link4', 'tool_link']
    for p, lab in zip(pts, labels):
        ax.text(p[0] + 0.01, p[1] + 0.01, p[2] + 0.01, lab, fontsize=7)

    max_range = 0.6
    ax.set_xlim(-max_range / 2, max_range / 2)
    ax.set_ylim(-max_range / 2, max_range / 2)
    ax.set_zlim(0, max_range)
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title(title, fontsize=11)
    ax.view_init(elev=18, azim=-60)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved {out_path}")


if __name__ == "__main__":
    render([0, 0, 0, 0], "4-DOF Arm - Home Configuration (q = [0,0,0,0] deg)\n"
                          "(geometry schematic derived from URDF, not a live RViz capture)",
            "report_assets/arm_home_config.png")
    render([45, -30, 60, -25], "4-DOF Arm - Sample Bent Configuration\n"
                                "(q1=45, q2=-30, q3=60, q4=-25 deg)\n"
                                "(geometry schematic derived from URDF, not a live RViz capture)",
            "report_assets/arm_bent_config.png")
