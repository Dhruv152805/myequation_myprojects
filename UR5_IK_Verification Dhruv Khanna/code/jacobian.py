"""
jacobian.py
-----------
Geometric Jacobian of the UR5 manipulator and singularity detection.

For a revolute-joint-only manipulator, the geometric Jacobian column i is:

    J_v_i = z_(i-1) x (p_e - p_(i-1))
    J_w_i = z_(i-1)

where z_(i-1) is the z-axis of frame (i-1) expressed in the base frame,
and p_(i-1) is the origin of frame (i-1) in the base frame (frame 0 is
the base itself: z_0 = [0,0,1], p_0 = [0,0,0]).
"""

import numpy as np
from forward_kinematics import forward_kinematics
from dh import N_JOINTS

SINGULARITY_MANIPULABILITY_THRESHOLD = 1e-3   # sqrt(det(J J^T))
SINGULARITY_MIN_SV_THRESHOLD = 1e-3           # smallest singular value


def geometric_jacobian(q):
    """
    Compute the 6xN geometric Jacobian at joint configuration q.

    Returns
    -------
    J : (6,6) ndarray
        Rows 0-2: linear velocity part.
        Rows 3-5: angular velocity part.
    """
    T_ee, T_list = forward_kinematics(q, return_intermediate=True)
    p_e = T_ee[0:3, 3]

    # frame 0 (base) contributes z0 = [0,0,1], p0 = [0,0,0]
    z_axes = [np.array([0.0, 0.0, 1.0])]
    origins = [np.array([0.0, 0.0, 0.0])]
    for T in T_list[:-1]:  # frames 1..5 (frame 6 not needed as a "previous" frame)
        z_axes.append(T[0:3, 2])
        origins.append(T[0:3, 3])

    J = np.zeros((6, N_JOINTS))
    for i in range(N_JOINTS):
        z_im1 = z_axes[i]
        p_im1 = origins[i]
        Jv = np.cross(z_im1, (p_e - p_im1))
        Jw = z_im1
        J[0:3, i] = Jv
        J[3:6, i] = Jw
    return J


def manipulability(J):
    """Yoshikawa manipulability measure w = sqrt(det(J J^T))."""
    JJt = J @ J.T
    det = np.linalg.det(JJt)
    return np.sqrt(max(det, 0.0))


def singular_values(J):
    return np.linalg.svd(J, compute_uv=False)


def is_singular(q, sv_threshold=SINGULARITY_MIN_SV_THRESHOLD):
    """
    Determine whether configuration q is (near) a kinematic singularity,
    using the smallest singular value of the Jacobian as the indicator.
    """
    J = geometric_jacobian(q)
    sv = singular_values(J)
    w = manipulability(J)
    flagged = sv[-1] < sv_threshold
    return {
        "singular": bool(flagged),
        "min_singular_value": float(sv[-1]),
        "manipulability": float(w),
        "singular_values": sv.tolist(),
    }


def numerical_jacobian(q, eps=1e-6):
    """
    Finite-difference Jacobian, used as an independent cross-check of the
    analytical geometric Jacobian above (position rows only, since a
    finite-difference of full orientation needs a rotation-log map).
    """
    from forward_kinematics import position
    q = np.asarray(q, dtype=float)
    Jp = np.zeros((3, N_JOINTS))
    p0 = position(forward_kinematics(q))
    for i in range(N_JOINTS):
        dq = np.zeros(N_JOINTS)
        dq[i] = eps
        p1 = position(forward_kinematics(q + dq))
        Jp[:, i] = (p1 - p0) / eps
    return Jp


if __name__ == "__main__":
    q_test = np.radians([30, -45, 60, -90, 45, 0])
    J = geometric_jacobian(q_test)
    print("Geometric Jacobian J(q):")
    print(np.array2string(J, precision=5, suppress_small=True))

    result = is_singular(q_test)
    print("\nSingularity check:", result)

    # cross-check linear part against finite-difference Jacobian
    Jp_num = numerical_jacobian(q_test)
    err = np.max(np.abs(Jp_num - J[0:3, :]))
    print(f"\nMax error vs finite-difference linear Jacobian: {err:.3e}")

    # A known near-singular UR5 pose: wrist-centered / elbow straight config
    q_sing = np.radians([0, 0, 0, 0, 0, 0])
    print("\nSingularity check at all-zero (straight arm) configuration:")
    print(is_singular(q_sing))
