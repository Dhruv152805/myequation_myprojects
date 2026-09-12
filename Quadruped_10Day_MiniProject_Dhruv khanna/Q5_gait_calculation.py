"""
Q5 - Gait Cycle Calculation
Complete kinematic gait analysis for a trot gait quadruped robot.
Author: Dhruv Khanna
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Gait Parameters ─────────────────────────────────────────────────────────
STRIDE_LENGTH = 0.15    # m  (chosen based on leg geometry)
WALK_SPEED    = 0.30    # m/s
T_CYCLE       = STRIDE_LENGTH / WALK_SPEED   # gait cycle period [s]
DUTY_FACTOR   = 0.5     # fraction of cycle foot is on ground (trot)

# Phase offsets for TROT gait (diagonal pairs swing together)
#   FL & RR → phase 0    (reference pair)
#   FR & RL → phase 0.5T (offset by half cycle)
PHASE_OFFSETS = {
    'FL': 0.0,
    'RR': 0.0,
    'FR': T_CYCLE / 2,
    'RL': T_CYCLE / 2,
}

# Joint angle amplitudes (radians)
A_HIP   = np.radians(25)    # hip swing amplitude
B_KNEE  = np.radians(30)    # knee modulation amplitude
K0_KNEE = np.radians(-60)   # knee neutral angle

print("=" * 60)
print("Q5 – GAIT CYCLE CALCULATION")
print("=" * 60)
print(f"\nStride Length  L  = {STRIDE_LENGTH*1000:.0f} mm")
print(f"Walking Speed  v  = {WALK_SPEED} m/s")
print(f"Gait Cycle Time T = L/v = {STRIDE_LENGTH*1000:.0f}/{WALK_SPEED*1000:.0f} = {T_CYCLE:.3f} s  ({1/T_CYCLE:.2f} Hz)")
print(f"Duty Factor  β    = {DUTY_FACTOR}  (trot: 50% stance, 50% swing)")
print(f"Stance time       = {DUTY_FACTOR*T_CYCLE*1000:.0f} ms")
print(f"Swing  time       = {(1-DUTY_FACTOR)*T_CYCLE*1000:.0f} ms")
print("\nPhase offsets (trot gait):")
for leg, phi in PHASE_OFFSETS.items():
    print(f"  {leg}: φ = {phi:.3f} s  ({np.degrees(2*np.pi*phi/T_CYCLE):.0f}°)")
print()

# ─── Time array ──────────────────────────────────────────────────────────────
t = np.linspace(0, 2 * T_CYCLE, 400)

def hip_angle(t_arr, phase):
    """Hip joint angle profile (sinusoidal swing)."""
    return A_HIP * np.sin(2 * np.pi * (t_arr - phase) / T_CYCLE)

def knee_angle(t_arr, phase):
    """Knee joint angle profile (sinusoidal, phase-shifted by 180° from hip)."""
    return K0_KNEE - B_KNEE * np.sin(2 * np.pi * (t_arr - phase) / T_CYCLE + np.pi)

def stance_mask(t_arr, phase):
    """Returns boolean mask: True during stance phase."""
    phase_norm = ((t_arr - phase) % T_CYCLE) / T_CYCLE  # [0,1)
    return phase_norm < DUTY_FACTOR

# Forward kinematics
THIGH = 0.080   # m
SHIN  = 0.070   # m

def foot_position(theta_h, theta_k):
    """Returns (x_foot, z_foot) relative to hip joint [m]."""
    x = THIGH * np.sin(theta_h) + SHIN * np.sin(theta_h + theta_k)
    z = -(THIGH * np.cos(theta_h) + SHIN * np.cos(theta_h + theta_k))
    return x, z

# ─── Plotting ─────────────────────────────────────────────────────────────────
COLORS = {
    'FL': '#4ECDC4', 'FR': '#FF6B35',
    'RL': '#96E6A1', 'RR': '#FFD700',
    'bg': '#0D0D1A', 'grid': '#333355'
}

fig = plt.figure(figsize=(16, 14), facecolor='#0D0D1A')
gs  = GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)
fig.suptitle('Q5 – Gait Cycle Calculation | Trot Gait | Quadruped Robot',
             color='white', fontsize=14, fontweight='bold', y=0.98)

# ── Plot 1: Hip Angle Profiles (all 4 legs) ────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor('#0D0D1A')
ax1.set_title('Hip Joint Angles – All 4 Legs', color='white', fontsize=10)
ax1.set_xlabel('Time [s]', color='#AAAACC')
ax1.set_ylabel('Hip Angle [deg]', color='#AAAACC')
ax1.tick_params(colors='#AAAACC')
ax1.grid(True, color='#333355', linewidth=0.4)
ax1.spines[:].set_color('#333355')

for leg, phase in PHASE_OFFSETS.items():
    angles = np.degrees(hip_angle(t, phase))
    ax1.plot(t, angles, color=COLORS[leg], linewidth=2, label=leg)
    mask = stance_mask(t, phase)
    ax1.fill_between(t, angles, alpha=0.15, where=mask, color=COLORS[leg])

ax1.axhline(0, color='#555577', linewidth=0.8, linestyle='--')
ax1.legend(facecolor='#1A1A2E', labelcolor='white', fontsize=8, loc='upper right')
ax1.text(0.02, 0.05, f'Amplitude: ±{np.degrees(A_HIP):.0f}°', transform=ax1.transAxes,
         color='#AAAACC', fontsize=8)

# ── Plot 2: Knee Angle Profiles ────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('#0D0D1A')
ax2.set_title('Knee Joint Angles – All 4 Legs', color='white', fontsize=10)
ax2.set_xlabel('Time [s]', color='#AAAACC')
ax2.set_ylabel('Knee Angle [deg]', color='#AAAACC')
ax2.tick_params(colors='#AAAACC')
ax2.grid(True, color='#333355', linewidth=0.4)
ax2.spines[:].set_color('#333355')

for leg, phase in PHASE_OFFSETS.items():
    angles = np.degrees(knee_angle(t, phase))
    ax2.plot(t, angles, color=COLORS[leg], linewidth=2, label=leg)
    mask = stance_mask(t, phase)
    ax2.fill_between(t, angles, alpha=0.15, where=mask, color=COLORS[leg])

ax2.legend(facecolor='#1A1A2E', labelcolor='white', fontsize=8, loc='lower right')
ax2.text(0.02, 0.05, f'Neutral: {np.degrees(K0_KNEE):.0f}°  Amp: ±{np.degrees(B_KNEE):.0f}°',
         transform=ax2.transAxes, color='#AAAACC', fontsize=8)

# ── Plot 3: Foot trajectory (one complete cycle, FL leg) ───────────────────
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_facecolor('#0D0D1A')
ax3.set_title('Foot Trajectory – FL Leg (1 Cycle)', color='white', fontsize=10)
ax3.set_xlabel('X – Forward [mm]', color='#AAAACC')
ax3.set_ylabel('Z – Vertical [mm]', color='#AAAACC')
ax3.tick_params(colors='#AAAACC')
ax3.grid(True, color='#333355', linewidth=0.4)
ax3.spines[:].set_color('#333355')
ax3.set_aspect('equal')

t_one = np.linspace(0, T_CYCLE, 200)
phase_fl = PHASE_OFFSETS['FL']
th_fl = hip_angle(t_one, phase_fl)
tk_fl = knee_angle(t_one, phase_fl)
fx_fl, fz_fl = foot_position(th_fl, tk_fl)
mask_fl = stance_mask(t_one, phase_fl)

ax3.plot(fx_fl[mask_fl]*1000,  fz_fl[mask_fl]*1000,  color='#4ECDC4', linewidth=3, label='Stance')
ax3.plot(fx_fl[~mask_fl]*1000, fz_fl[~mask_fl]*1000, color='#FF6B35', linewidth=2,
         linestyle='--', label='Swing')
ax3.scatter(fx_fl[0]*1000, fz_fl[0]*1000, s=120, color='lime', zorder=8, label='Start')
ax3.axhline(y=np.min(fz_fl)*1000, color='#555577', linewidth=1.5)
ax3.text(0, np.min(fz_fl)*1000 - 4, 'Ground', color='#555577', fontsize=8, ha='center')
ax3.legend(facecolor='#1A1A2E', labelcolor='white', fontsize=8)
ax3.text(0.02, 0.92, f'Step length: {(np.max(fx_fl)-np.min(fx_fl))*1000:.1f} mm\n'
                     f'Step height: {(np.max(fz_fl)-np.min(fz_fl))*1000:.1f} mm',
         transform=ax3.transAxes, color='#AAAACC', fontsize=8)

# ── Plot 4: Gait diagram (Gantt-style) ────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor('#0D0D1A')
ax4.set_title('Gait Diagram – Trot Gait (2 Cycles)', color='white', fontsize=10)
ax4.set_xlabel('Time [s]', color='#AAAACC')
ax4.tick_params(colors='#AAAACC')
ax4.grid(True, color='#333355', linewidth=0.4, axis='x')
ax4.spines[:].set_color('#333355')

legs_order = ['FL', 'RR', 'FR', 'RL']
y_positions = [3, 2, 1, 0]
t_gantt = np.linspace(0, 2*T_CYCLE, 1000)

for leg, y in zip(legs_order, y_positions):
    phase = PHASE_OFFSETS[leg]
    mask = stance_mask(t_gantt, phase)
    # Draw stance (filled) and swing (empty)
    for i in range(len(t_gantt)-1):
        if mask[i]:
            ax4.barh(y, t_gantt[i+1]-t_gantt[i], left=t_gantt[i],
                     color=COLORS[leg], height=0.6, alpha=0.85)
    ax4.text(-0.01, y, leg, color=COLORS[leg], fontsize=10, fontweight='bold',
             ha='right', va='center')

ax4.set_yticks([])
ax4.set_xlim(0, 2*T_CYCLE)
ax4.axvline(T_CYCLE, color='white', linewidth=1, linestyle='--', alpha=0.5)
ax4.text(T_CYCLE, 3.5, f'T={T_CYCLE:.2f}s', color='white', fontsize=8, ha='center')
ax4.text(0.5, -0.6, '■ Stance Phase  □ Swing Phase', color='#AAAACC', fontsize=8, ha='center')

# ── Plot 5: Numerical summary table ────────────────────────────────────────
ax5 = fig.add_subplot(gs[2, :])
ax5.set_facecolor('#0D0D1A')
ax5.axis('off')

summary_lines = [
    "GAIT CALCULATION SUMMARY",
    "",
    f"  Stride Length (L)          = {STRIDE_LENGTH*1000:.0f} mm",
    f"  Walking Speed (v)          = {WALK_SPEED:.2f} m/s",
    f"  Gait Cycle Period (T = L/v)= {T_CYCLE:.3f} s   →   Frequency = {1/T_CYCLE:.2f} Hz",
    f"  Duty Factor (β)            = {DUTY_FACTOR}  (Trot gait)",
    f"  Stance Duration            = β × T = {DUTY_FACTOR*T_CYCLE*1000:.0f} ms",
    f"  Swing  Duration            = (1−β) × T = {(1-DUTY_FACTOR)*T_CYCLE*1000:.0f} ms",
    "",
    f"  Hip Angle Profile    : θ_hip(t)  = {np.degrees(A_HIP):.0f}° × sin(2πt/T + φ_leg)",
    f"  Knee Angle Profile   : θ_knee(t) = {np.degrees(K0_KNEE):.0f}° − {np.degrees(B_KNEE):.0f}° × sin(2πt/T + φ_leg + π)",
    "",
    f"  Phase Offsets   FL=0°, RR=0°  |  FR=180°, RL=180°   (Diagonal pairs in trot)",
    f"  Foot Step Length  ≈ {(np.max(fx_fl)-np.min(fx_fl))*1000:.1f} mm",
    f"  Foot Step Height  ≈ {(np.max(fz_fl)-np.min(fz_fl))*1000:.1f} mm",
]

ax5.text(0.03, 0.95, '\n'.join(summary_lines),
         transform=ax5.transAxes, color='#AAAACC', fontsize=9,
         fontfamily='monospace', va='top',
         bbox=dict(boxstyle='round,pad=0.8', facecolor='#1A1A2E', edgecolor='#3A86FF', linewidth=1.5))

plt.tight_layout(rect=[0, 0, 1, 0.97])
out_path = os.path.join(OUT_DIR, 'Q5_gait_calculation.png')
fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='#0D0D1A')
plt.close(fig)
print(f"  Saved: Q5_gait_calculation.png")
print("Q5 Done.")
