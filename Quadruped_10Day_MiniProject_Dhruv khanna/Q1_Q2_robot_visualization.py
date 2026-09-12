"""
Q1 & Q2 – Mechanical Structure Design & CAD Assembly
Quadruped Robot 3D Visualization
Author: Dhruv Khanna
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as mpatches

# ─── Robot Parameters (all in mm) ──────────────────────────────────────────
BODY_L   = 200   # body length (X)
BODY_W   = 120   # body width  (Y)
BODY_H   =  30   # body height (Z)
THIGH_L  =  80   # upper leg (thigh) length
SHIN_L   =  70   # lower leg (shin)  length
LEG_RAD  =  10   # leg cylinder radius (visual)

# Hip offset from body corner (centred on short side)
HIP_X_OFFSET = 20   # inward from body end
HIP_Y_OFFSET = 0    # centred on body width edge

# Hip attachment height = bottom of body
HIP_Z = 0.0

# Default joint angles (neutral standing pose)
theta_hip   = np.radians(-30)   # hip: negative = swing backward
theta_knee  = np.radians(-80)   # knee: flexion


def rotation_y(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, 0, s],
                     [0, 1, 0],
                     [-s, 0, c]])

def rotation_z(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s, 0],
                     [s,  c, 0],
                     [0,  0, 1]])


def compute_leg_points(hip_pos, side_sign, th_hip, th_knee):
    """
    Returns (hip_pt, knee_pt, foot_pt) in world coordinates.
    side_sign: +1 = left, -1 = right (mirrors hip rotation about X)
    """
    # Hip joint is at hip_pos
    hip_pt = np.array(hip_pos)

    # Thigh direction: rotated by hip angle in the sagittal plane
    thigh_dir = rotation_y(th_hip) @ np.array([0, 0, -1])  # default hangs down
    knee_pt = hip_pt + thigh_dir * THIGH_L

    # Shin direction: relative to thigh, further rotated by knee angle
    shin_dir = rotation_y(th_hip + th_knee) @ np.array([0, 0, -1])
    foot_pt = knee_pt + shin_dir * SHIN_L

    return hip_pt, knee_pt, foot_pt


def draw_box(ax, center, dims, color, alpha=0.4, edgecolor='#222'):
    cx, cy, cz = center
    dx, dy, dz = dims[0]/2, dims[1]/2, dims[2]/2
    vertices = np.array([
        [cx-dx, cy-dy, cz-dz], [cx+dx, cy-dy, cz-dz],
        [cx+dx, cy+dy, cz-dz], [cx-dx, cy+dy, cz-dz],
        [cx-dx, cy-dy, cz+dz], [cx+dx, cy-dy, cz+dz],
        [cx+dx, cy+dy, cz+dz], [cx-dx, cy+dy, cz+dz],
    ])
    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],
        [vertices[4], vertices[5], vertices[6], vertices[7]],
        [vertices[0], vertices[1], vertices[5], vertices[4]],
        [vertices[2], vertices[3], vertices[7], vertices[6]],
        [vertices[0], vertices[3], vertices[7], vertices[4]],
        [vertices[1], vertices[2], vertices[6], vertices[5]],
    ]
    poly = Poly3DCollection(faces, alpha=alpha, facecolor=color, edgecolor=edgecolor, linewidth=0.5)
    ax.add_collection3d(poly)


def draw_leg(ax, hip_pos, side_sign, th_hip, th_knee, color_thigh, color_shin):
    hip_pt, knee_pt, foot_pt = compute_leg_points(hip_pos, side_sign, th_hip, th_knee)
    # Thigh
    ax.plot([hip_pt[0], knee_pt[0]],
            [hip_pt[1], knee_pt[1]],
            [hip_pt[2], knee_pt[2]],
            color=color_thigh, linewidth=6, solid_capstyle='round', zorder=5)
    # Shin
    ax.plot([knee_pt[0], foot_pt[0]],
            [knee_pt[1], foot_pt[1]],
            [knee_pt[2], foot_pt[2]],
            color=color_shin, linewidth=5, solid_capstyle='round', zorder=5)
    # Joints
    ax.scatter(*hip_pt,  s=120, color='#FFD700', zorder=10, edgecolors='#333', linewidths=1)
    ax.scatter(*knee_pt, s=100, color='#FF6B35', zorder=10, edgecolors='#333', linewidths=1)
    ax.scatter(*foot_pt, s=80,  color='#00D4FF', zorder=10, edgecolors='#333', linewidths=1)
    return hip_pt, knee_pt, foot_pt


def make_figure(elev=25, azim=-60, title_suffix=""):
    fig = plt.figure(figsize=(12, 9), facecolor='#0D0D1A')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#0D0D1A')

    # ── Body frame ──────────────────────────────────────────────────────────
    body_cx = 0
    body_cy = 0
    body_cz = THIGH_L * abs(np.sin(theta_hip)) + SHIN_L * abs(np.sin(theta_hip + theta_knee)) + BODY_H/2 + 5
    draw_box(ax, (body_cx, body_cy, body_cz), (BODY_L, BODY_W, BODY_H),
             color='#3A86FF', alpha=0.6)

    # ── Hip attachment positions (bottom of body) ────────────────────────────
    bz_bottom = body_cz - BODY_H / 2  # z level of body bottom face
    hip_positions = {
        'FL': ( BODY_L/2 - HIP_X_OFFSET,  BODY_W/2, bz_bottom),  # Front Left
        'FR': ( BODY_L/2 - HIP_X_OFFSET, -BODY_W/2, bz_bottom),  # Front Right
        'RL': (-BODY_L/2 + HIP_X_OFFSET,  BODY_W/2, bz_bottom),  # Rear Left
        'RR': (-BODY_L/2 + HIP_X_OFFSET, -BODY_W/2, bz_bottom),  # Rear Right
    }
    side_signs = {'FL': +1, 'FR': -1, 'RL': +1, 'RR': -1}

    THIGH_COLORS = {'FL': '#4ECDC4', 'FR': '#4ECDC4', 'RL': '#45B7D1', 'RR': '#45B7D1'}
    SHIN_COLORS  = {'FL': '#96E6A1', 'FR': '#96E6A1', 'RL': '#88D8B0', 'RR': '#88D8B0'}

    foot_pts = {}
    for name, pos in hip_positions.items():
        _, _, foot_pt = draw_leg(ax, pos, side_signs[name],
                                  theta_hip, theta_knee,
                                  THIGH_COLORS[name], SHIN_COLORS[name])
        foot_pts[name] = foot_pt

    # ── Ground plane ─────────────────────────────────────────────────────────
    foot_z_vals = [fp[2] for fp in foot_pts.values()]
    ground_z = min(foot_z_vals)
    gx = np.linspace(-160, 160, 3)
    gy = np.linspace(-120, 120, 3)
    GX, GY = np.meshgrid(gx, gy)
    GZ = np.full_like(GX, ground_z)
    ax.plot_surface(GX, GY, GZ, alpha=0.12, color='#8888AA', zorder=0)

    # ── Labels ───────────────────────────────────────────────────────────────
    label_offset = 12
    for name, pos in hip_positions.items():
        ax.text(pos[0], pos[1] + (label_offset if side_signs[name] > 0 else -label_offset),
                pos[2] + 8, name, color='white', fontsize=8, fontweight='bold', ha='center')

    # Dimension annotations
    ax.text(0, 0, body_cz + BODY_H, f'Body: {BODY_L}×{BODY_W}×{BODY_H} mm',
            color='#FFD700', fontsize=8, ha='center')
    ax.text(BODY_L/2 + 20, BODY_W/2, body_cz - BODY_H/4,
            f'Thigh: {THIGH_L}mm', color='#4ECDC4', fontsize=7)
    ax.text(BODY_L/2 + 20, BODY_W/2, body_cz - BODY_H,
            f'Shin: {SHIN_L}mm', color='#96E6A1', fontsize=7)

    # ── Axis styling ─────────────────────────────────────────────────────────
    ax.set_xlabel('X (mm) – Forward', color='#AAAACC', labelpad=8)
    ax.set_ylabel('Y (mm) – Lateral', color='#AAAACC', labelpad=8)
    ax.set_zlabel('Z (mm) – Vertical', color='#AAAACC', labelpad=8)
    ax.tick_params(colors='#AAAACC', labelsize=7)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('#333355')
    ax.yaxis.pane.set_edgecolor('#333355')
    ax.zaxis.pane.set_edgecolor('#333355')
    ax.grid(True, color='#333355', linewidth=0.4)

    ax.set_xlim(-160, 160)
    ax.set_ylim(-120, 120)
    ax.set_zlim(ground_z - 10, body_cz + BODY_H + 30)
    ax.view_init(elev=elev, azim=azim)

    # Legend
    legend_elems = [
        mpatches.Patch(facecolor='#3A86FF', label='Body Frame'),
        mpatches.Patch(facecolor='#4ECDC4', label='Thigh (Upper Leg)'),
        mpatches.Patch(facecolor='#96E6A1', label='Shin (Lower Leg)'),
        mpatches.Patch(facecolor='#FFD700', label='Hip Joint'),
        mpatches.Patch(facecolor='#FF6B35', label='Knee Joint'),
        mpatches.Patch(facecolor='#00D4FF', label='Foot'),
    ]
    ax.legend(handles=legend_elems, loc='upper left', facecolor='#1A1A2E',
              labelcolor='white', fontsize=7, framealpha=0.8)

    fig.suptitle(f'Quadruped Robot – CAD Structure Visualization{title_suffix}',
                 color='white', fontsize=13, fontweight='bold', y=0.97)
    ax.set_title('Body: 200×120×30 mm | Legs: 2-DOF (Hip + Knee) | 4 Identical Legs',
                 color='#AAAACC', fontsize=8, pad=4)

    plt.tight_layout()
    return fig


if __name__ == '__main__':
    import os
    out_dir = os.path.dirname(os.path.abspath(__file__))

    print("Generating Q1/Q2 Robot Visualization...")

    # Isometric view
    fig1 = make_figure(elev=25, azim=-55, title_suffix=" (Isometric View)")
    fig1.savefig(os.path.join(out_dir, 'Q1_Q2_robot_isometric.png'),
                 dpi=150, bbox_inches='tight', facecolor='#0D0D1A')
    plt.close(fig1)
    print("  Saved: Q1_Q2_robot_isometric.png")

    # Front view
    fig2 = make_figure(elev=0, azim=90, title_suffix=" (Front View)")
    fig2.savefig(os.path.join(out_dir, 'Q1_Q2_robot_front.png'),
                 dpi=150, bbox_inches='tight', facecolor='#0D0D1A')
    plt.close(fig2)
    print("  Saved: Q1_Q2_robot_front.png")

    # Side view
    fig3 = make_figure(elev=0, azim=0, title_suffix=" (Side View)")
    fig3.savefig(os.path.join(out_dir, 'Q1_Q2_robot_side.png'),
                 dpi=150, bbox_inches='tight', facecolor='#0D0D1A')
    plt.close(fig3)
    print("  Saved: Q1_Q2_robot_side.png")

    # Top view
    fig4 = make_figure(elev=90, azim=0, title_suffix=" (Top View)")
    fig4.savefig(os.path.join(out_dir, 'Q1_Q2_robot_top.png'),
                 dpi=150, bbox_inches='tight', facecolor='#0D0D1A')
    plt.close(fig4)
    print("  Saved: Q1_Q2_robot_top.png")

    print("Q1/Q2 Done.")
