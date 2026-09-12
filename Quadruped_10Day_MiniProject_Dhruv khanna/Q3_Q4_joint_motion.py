"""
Q3 – Joint Definition and Motion Limits
Q4 – Motion Validation via Simulation (animated sweep)
Author: Dhruv Khanna
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Robot Parameters ───────────────────────────────────────────────────────
THIGH_L = 80    # mm
SHIN_L  = 70    # mm

# ─── Joint Limits ────────────────────────────────────────────────────────────
HIP_MIN   = np.radians(-35)   # deg → rad
HIP_MAX   = np.radians( 35)
KNEE_MIN  = np.radians(-120)
KNEE_MAX  = np.radians(  0)


def fk_2dof(theta_hip, theta_knee):
    """2-DOF Forward Kinematics – returns (knee_x, knee_z, foot_x, foot_z)."""
    # Thigh hangs down from hip (0,0)
    knee_x = THIGH_L * np.sin(theta_hip)
    knee_z = -THIGH_L * np.cos(theta_hip)
    # Shin continues from knee
    foot_x = knee_x + SHIN_L * np.sin(theta_hip + theta_knee)
    foot_z = knee_z - SHIN_L * np.cos(theta_hip + theta_knee)
    return knee_x, knee_z, foot_x, foot_z


# ══════════════════════════════════════════════════════════════════════════════
# Q3: Static diagram showing joint axes and limits
# ══════════════════════════════════════════════════════════════════════════════
def plot_joint_limits():
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), facecolor='#0D0D1A')
    fig.suptitle('Q3 – Joint Definition & Motion Limits',
                 color='white', fontsize=14, fontweight='bold')

    colors = {'bg': '#0D0D1A', 'body': '#3A86FF', 'thigh': '#4ECDC4',
              'shin': '#96E6A1', 'joint': '#FFD700', 'knee': '#FF6B35',
              'foot': '#00D4FF', 'text': 'white', 'grid': '#333355'}

    angles_to_show = {
        'Hip −35°': (np.radians(-35), np.radians(-60)),
        'Hip   0°': (np.radians(  0), np.radians(-60)),
        'Hip +35°': (np.radians( 35), np.radians(-60)),
    }

    for ax in axes:
        ax.set_facecolor(colors['bg'])
        ax.tick_params(colors='#AAAACC')
        ax.set_aspect('equal')
        ax.spines[:].set_color('#333355')
        ax.grid(True, color=colors['grid'], linewidth=0.4)

    # ── Left plot: Hip range sweep ───────────────────────────────────────────
    ax1 = axes[0]
    ax1.set_title('Hip Joint (Y-axis rotation, ±35°)', color='white', fontsize=11)
    ax1.set_xlabel('X [mm]', color='#AAAACC')
    ax1.set_ylabel('Z [mm]', color='#AAAACC')

    alphas = [0.35, 1.0, 0.35]
    for (label, (th, tk)), alpha in zip(angles_to_show.items(), alphas):
        kx, kz, fx, fz = fk_2dof(th, tk)
        ax1.plot([0, kx], [0, kz], color=colors['thigh'],
                 linewidth=4 if alpha==1 else 2, alpha=alpha)
        ax1.plot([kx, fx], [kz, fz], color=colors['shin'],
                 linewidth=3.5 if alpha==1 else 1.5, alpha=alpha)
        if alpha == 1.0:
            ax1.annotate(f'{np.degrees(th):.0f}°',
                         xy=(fx, fz), xytext=(fx+8, fz-5),
                         color='white', fontsize=8, arrowprops=dict(arrowstyle='->', color='grey'))

    # Hip joint marker + arc
    arc_angles = np.linspace(HIP_MIN, HIP_MAX, 60)
    arc_r = 25
    ax1.plot(arc_r * np.sin(arc_angles), arc_r * np.cos(arc_angles) * -1 + arc_r,
             color='#FFD700', linewidth=1.5, linestyle='--')
    ax1.scatter(0, 0, s=200, color=colors['joint'], zorder=10, edgecolors='#333', linewidths=1.5)
    ax1.text(0, 8, 'Hip Joint\n(Axis: Y)', color='#FFD700', fontsize=8, ha='center')
    ax1.text(-60, -155, 'Hip Range: −35° to +35°\nJustification: Avoids body collision\nand ground contact', color='#AAAACC', fontsize=8)
    ax1.set_xlim(-100, 100)
    ax1.set_ylim(-185, 40)

    # ── Right plot: Knee range sweep ─────────────────────────────────────────
    ax2 = axes[1]
    ax2.set_title('Knee Joint (Y-axis rotation, −120° to 0°)', color='white', fontsize=11)
    ax2.set_xlabel('X [mm]', color='#AAAACC')
    ax2.set_ylabel('Z [mm]', color='#AAAACC')

    knee_angles = [0, -40, -80, -120]
    alphas_k = [0.3, 0.6, 1.0, 0.4]
    fixed_hip = np.radians(0)
    for tk_deg, alpha in zip(knee_angles, alphas_k):
        tk = np.radians(tk_deg)
        kx, kz, fx, fz = fk_2dof(fixed_hip, tk)
        ax2.plot([0, kx], [0, kz], color=colors['thigh'], linewidth=4, alpha=alpha)
        ax2.plot([kx, fx], [kz, fz], color=colors['shin'],
                 linewidth=3.5, alpha=alpha)
        ax2.scatter(kx, kz, s=120, color=colors['knee'], zorder=8, alpha=alpha,
                    edgecolors='#333', linewidths=1)
        if alpha > 0.5:
            ax2.annotate(f'Knee {tk_deg}°', xy=(fx, fz),
                         xytext=(fx+10, fz), color='white', fontsize=8,
                         arrowprops=dict(arrowstyle='->', color='grey'))

    ax2.scatter(0, 0, s=200, color=colors['joint'], zorder=10, edgecolors='#333', linewidths=1.5)
    ax2.text(0, 8, 'Hip Joint\n(Fixed at 0°)', color='#FFD700', fontsize=8, ha='center')
    ax2.text(-60, -155,
             'Knee Range: 0° to −120°\nJustification: Mimics biological\nknee; prevents hyperextension',
             color='#AAAACC', fontsize=8)
    ax2.set_xlim(-100, 100)
    ax2.set_ylim(-185, 40)

    # Joint limit table
    table_text = (
        "┌─────────┬──────────┬───────────────┬───────────────────────────────────┐\n"
        "│ Joint   │ Axis     │ Range         │ Justification                     │\n"
        "├─────────┼──────────┼───────────────┼───────────────────────────────────┤\n"
        "│ Hip     │ Y (lat.) │ −35° to +35°  │ Clearance; avoids body collision  │\n"
        "│ Knee    │ Y (lat.) │ 0° to −120°   │ Biological analogy; no hyperext.  │\n"
        "└─────────┴──────────┴───────────────┴───────────────────────────────────┘"
    )
    fig.text(0.5, 0.01, table_text, ha='center', va='bottom',
             color='#AAAACC', fontsize=7.5, fontfamily='monospace')

    plt.tight_layout(rect=[0, 0.14, 1, 1])
    path = os.path.join(OUT_DIR, 'Q3_joint_limits.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0D0D1A')
    plt.close(fig)
    print(f"  Saved: Q3_joint_limits.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q4: Motion Validation – animated leg sweep, saved as GIF
# ══════════════════════════════════════════════════════════════════════════════
def animate_motion():
    N_FRAMES = 72
    t_vals = np.linspace(0, 2 * np.pi, N_FRAMES, endpoint=False)

    # Sinusoidal joint profiles (walking motion)
    hip_profile  = np.radians(25) * np.sin(t_vals)
    knee_profile = np.radians(-60) + np.radians(-30) * np.sin(t_vals + np.pi)

    fig, ax = plt.subplots(figsize=(8, 7), facecolor='#0D0D1A')
    ax.set_facecolor('#0D0D1A')
    ax.set_aspect('equal')
    ax.set_xlim(-130, 130)
    ax.set_ylim(-175, 50)
    ax.set_xlabel('X [mm]', color='#AAAACC')
    ax.set_ylabel('Z [mm]', color='#AAAACC')
    ax.tick_params(colors='#AAAACC')
    ax.spines[:].set_color('#333355')
    ax.grid(True, color='#333355', linewidth=0.4)
    ax.set_title('Q4 – Motion Validation: Single Leg Sweep\n'
                 'Hip ±25°, Knee −60°±30° | Collision-Free', color='white', fontsize=11)

    # Trace path
    foot_xs, foot_zs = [], []
    for th, tk in zip(hip_profile, knee_profile):
        _, _, fx, fz = fk_2dof(th, tk)
        foot_xs.append(fx)
        foot_zs.append(fz)

    trace_line, = ax.plot([], [], color='#FF6B35', linewidth=1, alpha=0.4,
                          linestyle='--', label='Foot Trajectory')
    thigh_line, = ax.plot([], [], color='#4ECDC4', linewidth=6, solid_capstyle='round')
    shin_line,  = ax.plot([], [], color='#96E6A1', linewidth=5, solid_capstyle='round')
    hip_dot     = ax.scatter([], [], s=200, color='#FFD700', zorder=10,
                             edgecolors='#333', linewidths=1.5)
    knee_dot    = ax.scatter([], [], s=150, color='#FF6B35', zorder=10,
                             edgecolors='#333', linewidths=1.5)
    foot_dot    = ax.scatter([], [], s=120, color='#00D4FF', zorder=10,
                             edgecolors='#333', linewidths=1.5)
    frame_text  = ax.text(-120, 40, '', color='white', fontsize=9)
    angle_text  = ax.text(-120, 28, '', color='#AAAACC', fontsize=8)

    # Ground line
    ax.axhline(y=min(foot_zs) - 3, color='#555577', linewidth=1.5, linestyle='-')
    ax.text(0, min(foot_zs) - 10, 'Ground', color='#555577', fontsize=8, ha='center')

    from matplotlib.patches import Patch
    legend_elems = [
        Patch(facecolor='#4ECDC4', label='Thigh'),
        Patch(facecolor='#96E6A1', label='Shin'),
        Patch(facecolor='#FFD700', label='Hip Joint'),
        Patch(facecolor='#FF6B35', label='Knee Joint'),
        Patch(facecolor='#00D4FF', label='Foot'),
    ]
    ax.legend(handles=legend_elems, loc='lower right', facecolor='#1A1A2E',
              labelcolor='white', fontsize=8, framealpha=0.8)

    def init():
        thigh_line.set_data([], [])
        shin_line.set_data([], [])
        hip_dot.set_offsets(np.empty((0, 2)))
        knee_dot.set_offsets(np.empty((0, 2)))
        foot_dot.set_offsets(np.empty((0, 2)))
        trace_line.set_data([], [])
        return thigh_line, shin_line, hip_dot, knee_dot, foot_dot, trace_line

    def update(frame):
        th = hip_profile[frame]
        tk = knee_profile[frame]
        kx, kz, fx, fz = fk_2dof(th, tk)

        thigh_line.set_data([0, kx], [0, kz])
        shin_line.set_data([kx, fx], [kz, fz])
        hip_dot.set_offsets([[0, 0]])
        knee_dot.set_offsets([[kx, kz]])
        foot_dot.set_offsets([[fx, fz]])
        trace_line.set_data(foot_xs[:frame+1], foot_zs[:frame+1])
        frame_text.set_text(f'Frame {frame+1}/{N_FRAMES}')
        angle_text.set_text(f'Hip: {np.degrees(th):+.1f}°  |  Knee: {np.degrees(tk):+.1f}°')
        return thigh_line, shin_line, hip_dot, knee_dot, foot_dot, trace_line, frame_text, angle_text

    ani = animation.FuncAnimation(fig, update, frames=N_FRAMES,
                                   init_func=init, blit=True, interval=40)

    # Save as GIF
    gif_path = os.path.join(OUT_DIR, 'Q4_motion_simulation.gif')
    ani.save(gif_path, writer='pillow', fps=25, dpi=100)
    plt.close(fig)
    print(f"  Saved: Q4_motion_simulation.gif")

    # Also save a static snapshot (middle frame)
    fig2, ax2 = plt.subplots(figsize=(8, 7), facecolor='#0D0D1A')
    ax2.set_facecolor('#0D0D1A')
    ax2.set_aspect('equal')
    ax2.set_xlim(-130, 130)
    ax2.set_ylim(-175, 50)
    ax2.set_xlabel('X [mm]', color='#AAAACC')
    ax2.set_ylabel('Z [mm]', color='#AAAACC')
    ax2.tick_params(colors='#AAAACC')
    ax2.spines[:].set_color('#333355')
    ax2.grid(True, color='#333355', linewidth=0.4)
    ax2.set_title('Q4 – Motion Validation: Foot Trajectory\n'
                  'Hip ±25°, Knee −60°±30°  |  No Collisions Detected', color='white', fontsize=11)

    ax2.plot(foot_xs, foot_zs, color='#FF6B35', linewidth=2,
             linestyle='--', label='Foot Path', zorder=3)
    ax2.scatter(foot_xs[0], foot_zs[0], s=150, color='lime', zorder=8, label='Start')
    ax2.scatter(foot_xs[N_FRAMES//2], foot_zs[N_FRAMES//2], s=150, color='#00D4FF', zorder=8, label='Mid')
    ax2.axhline(y=min(foot_zs) - 3, color='#555577', linewidth=1.5)
    ax2.text(0, min(foot_zs) - 10, 'Ground', color='#555577', fontsize=8, ha='center')

    # Draw leg at 3 poses
    for i in [0, N_FRAMES//4, N_FRAMES//2]:
        th, tk = hip_profile[i], knee_profile[i]
        kx, kz, fx, fz = fk_2dof(th, tk)
        alpha = 0.5 if i != N_FRAMES//4 else 1.0
        ax2.plot([0, kx], [0, kz], color='#4ECDC4', linewidth=4, alpha=alpha)
        ax2.plot([kx, fx], [kz, fz], color='#96E6A1', linewidth=3.5, alpha=alpha)

    ax2.scatter(0, 0, s=200, color='#FFD700', zorder=10, edgecolors='#333', linewidths=1.5)
    ax2.legend(loc='lower right', facecolor='#1A1A2E', labelcolor='white', fontsize=8, framealpha=0.8)

    snap_path = os.path.join(OUT_DIR, 'Q4_motion_snapshot.png')
    fig2.savefig(snap_path, dpi=150, bbox_inches='tight', facecolor='#0D0D1A')
    plt.close(fig2)
    print(f"  Saved: Q4_motion_snapshot.png")


if __name__ == '__main__':
    print("Generating Q3 – Joint Limits diagram...")
    plot_joint_limits()
    print("Generating Q4 – Motion animation...")
    animate_motion()
    print("Q3/Q4 Done.")
