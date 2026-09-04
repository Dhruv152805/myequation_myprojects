"""
verification.py
----------------
Verifies an IK solution by applying forward kinematics to the IK-derived
joint angles and comparing the resulting pose against the desired pose.
Reports position error (Euclidean, mm), orientation error (deg), and a
clear PASS/FAIL validity flag against user-defined tolerances.
"""

import numpy as np
from forward_kinematics import forward_kinematics
from inverse_kinematics import rotation_error

POSITION_TOL_M = 1e-3      # 1 mm
ORIENTATION_TOL_DEG = 0.5  # 0.5 degree


def verify_ik_solution(q_solution, T_desired,
                        position_tol=POSITION_TOL_M,
                        orientation_tol_deg=ORIENTATION_TOL_DEG):
    """
    Apply FK to q_solution and compare against T_desired.

    Returns a dict with the achieved pose, position error, orientation
    error, and an overall boolean 'valid' flag.
    """
    T_achieved = forward_kinematics(q_solution)

    pos_err_vec = T_achieved[0:3, 3] - T_desired[0:3, 3]
    pos_err = float(np.linalg.norm(pos_err_vec))

    orient_err_vec = rotation_error(T_achieved[0:3, 0:3], T_desired[0:3, 0:3])
    orient_err_deg = float(np.degrees(np.linalg.norm(orient_err_vec)))

    valid = (pos_err <= position_tol) and (orient_err_deg <= orientation_tol_deg)

    return {
        "T_achieved": T_achieved,
        "position_error_m": pos_err,
        "position_error_mm": pos_err * 1000.0,
        "orientation_error_deg": orient_err_deg,
        "position_tol_m": position_tol,
        "orientation_tol_deg": orientation_tol_deg,
        "valid": bool(valid),
    }


def report_verification(result, label="IK Verification"):
    print(f"\n{label}")
    print("-" * len(label))
    print(f"Position error:    {result['position_error_mm']:.4f} mm "
          f"(tolerance {result['position_tol_m']*1000:.2f} mm)")
    print(f"Orientation error: {result['orientation_error_deg']:.4f} deg "
          f"(tolerance {result['orientation_tol_deg']:.2f} deg)")
    print(f"IK SOLUTION VALID: {result['valid']}")


if __name__ == "__main__":
    from inverse_kinematics import inverse_kinematics

    q_true = np.radians([20, -60, 90, -75, 50, 15])
    T_target = forward_kinematics(q_true)
    ik_result = inverse_kinematics(T_target)

    v = verify_ik_solution(ik_result["q"], T_target)
    report_verification(v)
