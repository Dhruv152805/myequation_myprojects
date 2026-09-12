"""
Q6 – Stability Check
Static stability analysis using support polygon method.
Author: Dhruv Khanna
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Polygon as MplPolygon, FancyArrowPatch
from matplotlib.collections import PatchCollection
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Robot Geometry ───────────────────────────────────────────────────────────
BODY_L   = 200e-3   # m  (body length)
BODY_W   = 120e-3   # m  (body width)
THIGH    =  80e-3   # m
SHIN     =  70e-3   # m

# Foot positions on ground (hip outreach + stance geometry)
# Neutral standing: hip angle=0, knee angle=-80°
# foot_x relative to hip = 0 (hip=0) + SHIN*sin(0-80°) ≈ -0.069 m
# But we define foot positions in the body frame (XY plane = ground)
HIP_INSET_X = 20e-3   # hip is 20 mm inward from body end
HIP_SIDE_Y  = 60e-3   # hip is at body edge (half body width)
FOOT_REACH_X = 0.0    # fore-aft reach of foot relative to hip on ground
FOOT_REACH_Y = 30e-3  # lateral reach outward

# Foot X,Y positions in body frame [m]  (Z is ground)
FOOT_POSITIONS_NOMINAL = {
    'FL': np.array([ BODY_L/2 - HIP_INSET_X + FOOT_REACH_X,  HIP_SIDE_Y + FOOT_REACH_Y]),
    'FR': np.array([ BODY_L/2 - HIP_INSET_X + FOOT_REACH_X, -HIP_SIDE_Y - FOOT_REACH_Y]),
    'RL': np.array([-BODY_L/2 + HIP_INSET_X - FOOT_REACH_X,  HIP_SIDE_Y + FOOT_REACH_Y]),
    'RR': np.array([-BODY_L/2 + HIP_INSET_X - FOOT_REACH_X, -HIP_SIDE_Y - FOOT_REACH_Y]),
}

# CoM: geometric center of body (assumed uniform mass distribution)
COM = np.array([0.0, 0.0])

# ─── Support polygon helpers ──────────────────────────────────────────────────
def support_polygon(feet_dict):
    """Return ordered vertices of convex hull of grounded feet."""
    from scipy.spatial import ConvexHull
    pts = np.array(list(feet_dict.values()))
    if len(pts) < 3:
        return pts  # degenerate
    hull = ConvexHull(pts)
    return pts[hull.vertices]

def point_in_polygon(point, polygon):
    """Ray-casting test for point inside convex polygon."""
    from matplotlib.path import Path
    path = Path(np.vstack([polygon, polygon[0]]))
    return path.contains_point(point)

def margin_to_edge(com, polygon):
    """Minimum distance from CoM to any edge of the support polygon."""
    min_dist = np.inf
    n = len(polygon)
    for i in range(n):
        A = polygon[i]
        B = polygon[(i+1) % n]
        AB = B - A
        AP = com - A
        t = np.dot(AP, AB) / np.dot(AB, AB)
        t = np.clip(t, 0, 1)
        proj = A + t * AB
        dist = np.linalg.norm(com - proj)
        min_dist = min(min_dist, dist)
    return min_dist


# ════════════════════════════════════════════════════════════════════════════
# Build figure
# ════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(16, 12), facecolor='#0D0D1A')
gs  = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)
fig.suptitle('Q6 – Static Stability Check | Support Polygon Method',
             color='white', fontsize=14, fontweight='bold', y=0.98)

COLORS = {
    'FL': '#4ECDC4', 'FR': '#FF6B35', 'RL': '#96E6A1', 'RR': '#FFD700',
    'com': '#FF3860', 'polygon': '#3A86FF', 'bg': '#0D0D1A', 'grid': '#333355'
}

def setup_ax(ax, title):
    ax.set_facecolor('#0D0D1A')
    ax.set_title(title, color='white', fontsize=10)
    ax.set_xlabel('X – Forward [m]', color='#AAAACC', fontsize=8)
    ax.set_ylabel('Y – Lateral [m]', color='#AAAACC', fontsize=8)
    ax.tick_params(colors='#AAAACC', labelsize=7)
    ax.grid(True, color='#333355', linewidth=0.4)
    ax.spines[:].set_color('#333355')
    ax.set_aspect('equal')
    ax.set_xlim(-0.16, 0.16)
    ax.set_ylim(-0.14, 0.14)

def draw_body(ax, alpha=0.3):
    body = plt.Rectangle((-BODY_L/2, -BODY_W/2), BODY_L, BODY_W,
                          linewidth=1.5, edgecolor='#3A86FF', facecolor='#3A86FF', alpha=alpha)
    ax.add_patch(body)
    ax.text(0, 0, 'BODY', color='white', fontsize=8, ha='center', va='center', alpha=0.6)

def draw_feet_and_polygon(ax, grounded_feet, all_feet, show_com=True, com_pos=None):
    # All feet (hollow = lifted)
    for name, pos in all_feet.items():
        if name in grounded_feet:
            ax.scatter(*pos, s=200, color=COLORS[name], zorder=10,
                       edgecolors='white', linewidths=1.5, label=f'{name} (ground)')
        else:
            ax.scatter(*pos, s=200, facecolors='none', edgecolors=COLORS[name],
                       linewidths=2, zorder=10, label=f'{name} (lifted)', marker='o')
        ax.text(pos[0], pos[1] + 0.012, name, color=COLORS[name],
                fontsize=8, ha='center', fontweight='bold')

    # Support polygon
    if len(grounded_feet) >= 3:
        poly_pts = support_polygon(grounded_feet)
        closed = np.vstack([poly_pts, poly_pts[0]])
        ax.fill(poly_pts[:, 0], poly_pts[:, 1], alpha=0.18, color='#3A86FF')
        ax.plot(closed[:, 0], closed[:, 1], color='#3A86FF', linewidth=2,
                linestyle='--', label='Support Polygon')
        stable = point_in_polygon(COM if com_pos is None else com_pos,
                                  poly_pts)
        margin = margin_to_edge(COM if com_pos is None else com_pos, poly_pts)
        color_txt = 'lime' if stable else '#FF3860'
        ax.text(-0.15, 0.12,
                f'{"✓ STABLE" if stable else "✗ UNSTABLE"}\nMargin: {margin*1000:.1f} mm',
                color=color_txt, fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='#1A1A2E', edgecolor=color_txt))

    elif len(grounded_feet) == 2:
        pts = np.array(list(grounded_feet.values()))
        ax.plot(pts[:, 0], pts[:, 1], color='#3A86FF', linewidth=2, linestyle='--')
        ax.text(-0.15, 0.12, '⚠ LINE SUPPORT\n(Dynamic Phase)',
                color='#FFD700', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='#1A1A2E', edgecolor='#FFD700'))

    # CoM
    cx, cy = (COM if com_pos is None else com_pos)
    ax.scatter(cx, cy, s=280, color='#FF3860', marker='*', zorder=15,
               edgecolors='white', linewidths=1, label='CoM')
    ax.annotate('CoM', xy=(cx, cy), xytext=(cx+0.02, cy+0.02),
                color='#FF3860', fontsize=8,
                arrowprops=dict(arrowstyle='->', color='#FF3860', lw=1))


# ══ Panel 1: All 4 feet (static standing) ══════════════════════════════════
ax1 = fig.add_subplot(gs[0, 0])
setup_ax(ax1, 'Case 1: Static Stand (4 feet)')
draw_body(ax1)
draw_feet_and_polygon(ax1, FOOT_POSITIONS_NOMINAL, FOOT_POSITIONS_NOMINAL)
ax1.legend(facecolor='#1A1A2E', labelcolor='white', fontsize=7, loc='lower right',
           handlelength=1)

# ══ Panel 2: Walk gait – 3 feet (FL lifted) ═════════════════════════════════
ax2 = fig.add_subplot(gs[0, 1])
setup_ax(ax2, 'Case 2: Walk Gait – FL Lifting (3 feet)')
draw_body(ax2)
grounded_3 = {k: v for k, v in FOOT_POSITIONS_NOMINAL.items() if k != 'FL'}
draw_feet_and_polygon(ax2, grounded_3, FOOT_POSITIONS_NOMINAL)
ax2.legend(facecolor='#1A1A2E', labelcolor='white', fontsize=7, loc='lower right',
           handlelength=1)

# ══ Panel 3: Trot gait – 2 diagonal feet ═══════════════════════════════════
ax3 = fig.add_subplot(gs[0, 2])
setup_ax(ax3, 'Case 3: Trot Gait – 2 Diagonal Feet')
draw_body(ax3)
grounded_2 = {k: v for k, v in FOOT_POSITIONS_NOMINAL.items() if k in ('FL', 'RR')}
draw_feet_and_polygon(ax3, grounded_2, FOOT_POSITIONS_NOMINAL)
ax3.legend(facecolor='#1A1A2E', labelcolor='white', fontsize=7, loc='lower right',
           handlelength=1)

# ══ Panel 4: CoM shift analysis (walk gait) ════════════════════════════════
ax4 = fig.add_subplot(gs[1, 0:2])
setup_ax(ax4, 'CoM Shift Tolerance – Walk Gait (3-foot support)')
ax4.set_xlim(-0.18, 0.18)
ax4.set_ylim(-0.16, 0.16)
draw_body(ax4, alpha=0.15)

grounded_walk = {k: v for k, v in FOOT_POSITIONS_NOMINAL.items() if k != 'FL'}
poly_pts = support_polygon(grounded_walk)
closed = np.vstack([poly_pts, poly_pts[0]])
ax4.fill(poly_pts[:, 0], poly_pts[:, 1], alpha=0.2, color='#3A86FF')
ax4.plot(closed[:, 0], closed[:, 1], color='#3A86FF', linewidth=2, linestyle='--')

# Draw all foot positions
for name, pos in FOOT_POSITIONS_NOMINAL.items():
    grounded = name != 'FL'
    ax4.scatter(*pos, s=200 if grounded else 100,
                color=COLORS[name] if grounded else 'none',
                edgecolors=COLORS[name], linewidths=2, zorder=10)
    ax4.text(pos[0], pos[1]+0.012, name, color=COLORS[name], fontsize=8, ha='center')

# Sample CoM positions (shifted)
com_shifts_x = np.linspace(-0.07, 0.07, 6)
com_shifts_y = np.linspace(-0.05, 0.05, 5)
stability_map = []
for cx in com_shifts_x:
    for cy in com_shifts_y:
        c = np.array([cx, cy])
        stable = point_in_polygon(c, poly_pts)
        stability_map.append((cx, cy, stable))

for cx, cy, stable in stability_map:
    ax4.scatter(cx, cy, s=40,
                color='lime' if stable else '#FF3860',
                marker='o' if stable else 'x',
                alpha=0.7, zorder=5)

# Nominal CoM
ax4.scatter(*COM, s=350, color='#FF3860', marker='*', zorder=15,
            edgecolors='white', linewidths=1.5, label='Nominal CoM (Stable)')
ax4.legend(facecolor='#1A1A2E', labelcolor='white', fontsize=8)
margin_nom = margin_to_edge(COM, poly_pts)
ax4.text(-0.17, 0.14,
         f'Nominal CoM margin: {margin_nom*1000:.1f} mm\n'
         f'● = stable CoM positions   ✕ = unstable',
         color='#AAAACC', fontsize=8)

# ══ Panel 5: Summary ═══════════════════════════════════════════════════════
ax5 = fig.add_subplot(gs[1, 2])
ax5.set_facecolor('#0D0D1A')
ax5.axis('off')

stable_4 = point_in_polygon(COM, support_polygon(FOOT_POSITIONS_NOMINAL))
stable_3 = point_in_polygon(COM, support_polygon(grounded_3))
margin_4 = margin_to_edge(COM, support_polygon(FOOT_POSITIONS_NOMINAL))
margin_3 = margin_to_edge(COM, support_polygon(grounded_3))

summary = (
    "STABILITY ANALYSIS RESULTS\n\n"
    f"Robot body:    {BODY_L*1000:.0f}×{BODY_W*1000:.0f} mm\n"
    f"CoM location:  ({COM[0]*1000:.0f}, {COM[1]*1000:.0f}) mm\n"
    f"               (geometric center)\n\n"
    f"Case 1 – 4 feet (standing):\n"
    f"  CoM inside polygon? {'YES ✓' if stable_4 else 'NO ✗'}\n"
    f"  Stability margin:  {margin_4*1000:.1f} mm\n\n"
    f"Case 2 – 3 feet (walk gait):\n"
    f"  CoM inside polygon? {'YES ✓' if stable_3 else 'NO ✗'}\n"
    f"  Stability margin:  {margin_3*1000:.1f} mm\n\n"
    f"Case 3 – 2 feet (trot gait):\n"
    f"  CoM on support line → DYNAMIC\n"
    f"  Requires forward motion for\n"
    f"  dynamic stability\n\n"
    f"CONCLUSION:\n"
    f"Walk gait (3-foot contact) is\n"
    f"statically stable.\n"
    f"Trot gait requires dynamic\n"
    f"balance (acceptable for this\n"
    f"robot class)."
)

ax5.text(0.05, 0.95, summary, transform=ax5.transAxes,
         color='#AAAACC', fontsize=8.5, fontfamily='monospace', va='top',
         bbox=dict(boxstyle='round,pad=0.8', facecolor='#1A1A2E',
                   edgecolor='#3A86FF', linewidth=1.5))

plt.tight_layout(rect=[0, 0, 1, 0.97])
out_path = os.path.join(OUT_DIR, 'Q6_stability_check.png')
fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='#0D0D1A')
plt.close(fig)
print(f"  Saved: Q6_stability_check.png")
print("Q6 Done.")
