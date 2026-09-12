"""
main.py
-------
End-to-end demonstration of the UR5 Inverse Kinematics Verification Tool:

  1. DH parameter table
  2. Forward kinematics for a given joint vector
  3. Inverse kinematics for a desired end-effector pose (numerical, DLS)
  4. Verification of the IK solution via forward kinematics
  5. Jacobian computation and singularity check

Run:  python3 main.py
Writes a machine-readable summary to ../results/results.json and a
human-readable summary to ../results/results.txt
"""

import json
import numpy as np

from dh import dh_table
from forward_kinematics import forward_kinematics, position, rotation, pretty_print_pose
from jacobian import geometric_jacobian, is_singular, numerical_jacobian
from inverse_kinematics import inverse_kinematics, inverse_kinematics_multi_start
from verification import verify_ik_solution, report_verification


def mat_list(a):
    return np.round(a, 6).tolist()


def main():
    log_lines = []

    def log(*args):
        s = " ".join(str(a) for a in args)
        print(s)
        log_lines.append(s)

    results = {}

    # ------------------------------------------------------------------
    # 1. DH Parameter Table
    # ------------------------------------------------------------------
    log("=" * 70)
    log("1. DH PARAMETER TABLE (Standard DH, UR5)")
    log("=" * 70)
    q_demo = np.radians([30, -45, 60, -90, 45, 20])
    table = dh_table(q_demo)
    log(f"{'i':>2} {'a_i (m)':>10} {'alpha_i (rad)':>14} {'d_i (m)':>10} {'theta_i (rad)':>14}")
    for i, row in enumerate(table, start=1):
        log(f"{i:>2} {row['a']:>10.5f} {row['alpha']:>14.5f} {row['d']:>10.5f} {row['theta']:>14.5f}")
    results["dh_table_demo_q_deg"] = np.degrees(q_demo).tolist()
    results["dh_table"] = [{k: float(v) for k, v in row.items()} for row in table]

    # ------------------------------------------------------------------
    # 2. Forward Kinematics
    # ------------------------------------------------------------------
    log("\n" + "=" * 70)
    log("2. FORWARD KINEMATICS")
    log("=" * 70)
    log(f"q (deg) = {np.degrees(q_demo).round(3).tolist()}")
    T_fk = forward_kinematics(q_demo)
    log("T_0_6 =")
    log(np.array2string(T_fk, precision=5, suppress_small=True))
    p = position(T_fk)
    log(f"End-effector position (m): x={p[0]:.5f}, y={p[1]:.5f}, z={p[2]:.5f}")
    results["fk_demo"] = {
        "q_deg": np.degrees(q_demo).tolist(),
        "T_0_6": mat_list(T_fk),
        "position_m": mat_list(p),
    }

    # ------------------------------------------------------------------
    # 3. Inverse Kinematics
    # ------------------------------------------------------------------
    log("\n" + "=" * 70)
    log("3. INVERSE KINEMATICS")
    log("=" * 70)
    # Desired pose = FK of a known "true" joint vector (so we can check
    # the IK solver recovers a configuration reproducing the same pose).
    q_true = np.radians([15, -70, 100, -95, 60, -10])
    T_desired = forward_kinematics(q_true)
    log(f"Desired pose T_desired generated from q_true (deg) = "
        f"{np.degrees(q_true).round(3).tolist()}")
    log("T_desired =")
    log(np.array2string(T_desired, precision=5, suppress_small=True))

    ik_result = inverse_kinematics_multi_start(T_desired, n_starts=8)
    log(f"\nIK solver: damped least-squares (Levenberg-Marquardt) on geometric Jacobian")
    log(f"Converged: {ik_result['converged']}   Iterations: {ik_result['iterations']}")
    log(f"Final pose-error norm during solve: {ik_result['final_error']:.3e}")
    log(f"IK solution q (deg) = {np.degrees(ik_result['q']).round(3).tolist()}")
    results["ik_demo"] = {
        "q_true_deg": np.degrees(q_true).tolist(),
        "T_desired": mat_list(T_desired),
        "q_solution_deg": np.degrees(ik_result["q"]).tolist(),
        "converged": ik_result["converged"],
        "iterations": ik_result["iterations"],
        "solver_final_error": ik_result["final_error"],
    }

    # ------------------------------------------------------------------
    # 4. IK Verification
    # ------------------------------------------------------------------
    log("\n" + "=" * 70)
    log("4. IK VERIFICATION (FK applied to IK solution)")
    log("=" * 70)
    v = verify_ik_solution(ik_result["q"], T_desired)
    log(f"Achieved pose T_achieved =")
    log(np.array2string(v["T_achieved"], precision=5, suppress_small=True))
    log(f"Position error:    {v['position_error_mm']:.5f} mm "
        f"(tolerance {v['position_tol_m']*1000:.2f} mm)")
    log(f"Orientation error: {v['orientation_error_deg']:.5f} deg "
        f"(tolerance {v['orientation_tol_deg']:.2f} deg)")
    log(f"IK SOLUTION VALID: {v['valid']}")
    results["verification_demo"] = {
        "T_achieved": mat_list(v["T_achieved"]),
        "position_error_mm": v["position_error_mm"],
        "orientation_error_deg": v["orientation_error_deg"],
        "valid": v["valid"],
    }

    # ------------------------------------------------------------------
    # 5. Jacobian and Singularity Analysis
    # ------------------------------------------------------------------
    log("\n" + "=" * 70)
    log("5. JACOBIAN AND SINGULARITY ANALYSIS")
    log("=" * 70)
    J = geometric_jacobian(q_demo)
    log(f"Geometric Jacobian J(q) at q (deg) = {np.degrees(q_demo).round(3).tolist()}")
    log(np.array2string(J, precision=5, suppress_small=True))

    Jp_num = numerical_jacobian(q_demo)
    fd_err = float(np.max(np.abs(Jp_num - J[0:3, :])))
    log(f"\nCross-check vs finite-difference linear Jacobian, max abs error: {fd_err:.3e}")

    sing_demo = is_singular(q_demo)
    log(f"\nSingularity check at demo configuration:")
    log(f"  singular values: {[round(s,5) for s in sing_demo['singular_values']]}")
    log(f"  manipulability index: {sing_demo['manipulability']:.6f}")
    log(f"  flagged as singular: {sing_demo['singular']}")

    # Known singular configuration: fully-extended arm (elbow straight,
    # q2 = q3 = 0) -> loses a degree of freedom in the reach direction.
    q_singular_case = np.radians([0, 0, 0, 0, 0, 0])
    sing_case = is_singular(q_singular_case)
    log(f"\nSingularity check at straight-arm configuration q=[0,0,0,0,0,0]:")
    log(f"  singular values: {[round(s,5) for s in sing_case['singular_values']]}")
    log(f"  manipulability index: {sing_case['manipulability']:.6f}")
    log(f"  flagged as singular: {sing_case['singular']}")

    # Wrist singularity: q5 = 0 aligns joint-4 and joint-6 axes
    q_wrist_singular = np.radians([10, -50, 80, -30, 0, 15])
    sing_wrist = is_singular(q_wrist_singular)
    log(f"\nSingularity check at wrist-aligned configuration "
        f"(q5=0): q = {np.degrees(q_wrist_singular).round(2).tolist()}")
    log(f"  singular values: {[round(s,5) for s in sing_wrist['singular_values']]}")
    log(f"  manipulability index: {sing_wrist['manipulability']:.6f}")
    log(f"  flagged as singular: {sing_wrist['singular']}")

    results["jacobian_demo"] = {
        "q_deg": np.degrees(q_demo).tolist(),
        "J": mat_list(J),
        "finite_difference_check_max_error": fd_err,
        "singularity_at_demo_q": sing_demo,
        "singularity_at_straight_arm": sing_case,
        "singularity_at_wrist_aligned": sing_wrist,
    }

    # ------------------------------------------------------------------
    # Save results
    # ------------------------------------------------------------------
    with open("../results/results.json", "w") as f:
        json.dump(results, f, indent=2)
    with open("../results/results.txt", "w") as f:
        f.write("\n".join(log_lines))

    log("\nSaved: ../results/results.json and ../results/results.txt")


if __name__ == "__main__":
    main()
