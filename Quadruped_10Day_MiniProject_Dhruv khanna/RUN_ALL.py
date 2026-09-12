# -*- coding: utf-8 -*-
"""
RUN_ALL.py - Master build script
Runs all Q1-Q7 scripts and generates the final PDF report.
Author: Dhruv Khanna
Usage: python RUN_ALL.py
"""

import subprocess
import sys
import os
import time
import io

# Force UTF-8 output so special chars from subprocesses don't crash
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))

scripts = [
    ('Q1 & Q2 – Robot Visualization',  'Q1_Q2_robot_visualization.py'),
    ('Q3 & Q4 – Joint Limits + Motion', 'Q3_Q4_joint_motion.py'),
    ('Q5     – Gait Calculation',       'Q5_gait_calculation.py'),
    ('Q6     – Stability Check',        'Q6_stability_check.py'),
    ('Report – PDF Generator',          'generate_report.py'),
]

print("=" * 62)
print("  QUADRUPED ROBOT PROJECT - FULL BUILD")
print("  Dhruv Khanna | CAD/CAM Assignment")
print("=" * 62)
print()

all_ok = True
for label, script in scripts:
    path = os.path.join(BASE, script)
    print(f">>  Running: {label}")
    t0 = time.time()
    result = subprocess.run([sys.executable, path],
                            capture_output=True, text=True,
                            encoding='utf-8', errors='replace')
    elapsed = time.time() - t0
    if result.returncode == 0:
        # Print output lines (indented)
        for line in result.stdout.strip().splitlines():
            print(f"   {line}")
        print(f"   [OK] Done in {elapsed:.1f}s\n")
    else:
        print(f"   [FAIL] FAILED ({elapsed:.1f}s)")
        print(result.stdout)
        print(result.stderr)
        all_ok = False
        print()

print("=" * 62)
if all_ok:
    print("  ALL DONE! Your project files are ready.")
    print()
    print("  Generated files:")
    for f in sorted(os.listdir(BASE)):
        if f.endswith(('.png', '.gif', '.pdf')) and not f.startswith('_'):
            size_kb = os.path.getsize(os.path.join(BASE, f)) // 1024
            print(f"    - {f}  ({size_kb} KB)")
    print()
    print("  Upload the entire folder to Google Drive as:")
    print("     Quadruped_10Day_MiniProject_Dhruv khanna")
else:
    print("  WARNING: Some steps failed. Check errors above.")
print("=" * 62)
