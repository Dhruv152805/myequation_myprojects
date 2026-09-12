"""
forward_kinematics.py
----------------------
Computes the forward kinematics (base -> end-effector transform) of the
UR5 robot from a joint vector q, by chaining the individual DH transforms.
"""

import numpy as np
from dh import all_transforms, N_JOINTS


def forward_kinematics(q, return_intermediate=False):
    """
    Compute the end-effector pose T_0_6 for joint vector q.

    Parameters
    ----------
    q : array-like, shape (6,)
        Joint angles in radians.
    return_intermediate : bool
        If True, also return the list of cumulative transforms
        [T_0_1, T_0_2, ..., T_0_6] (needed by the Jacobian module).

    Returns
    -------
    T : (4,4) ndarray
        Homogeneous transform of the end-effector w.r.t. the base frame.
    (optional) T_list : list of (4,4) ndarray
        Cumulative transforms from base to each joint frame.
    """
    A_list = all_transforms(q)
    T = np.eye(4)
    T_list = []
    for A in A_list:
        T = T @ A
        T_list.append(T.copy())

    if return_intermediate:
        return T, T_list
    return T


def position(T):
    """Extract the (x, y, z) position from a homogeneous transform."""
    return T[0:3, 3]


def rotation(T):
    """Extract the 3x3 rotation matrix from a homogeneous transform."""
    return T[0:3, 0:3]


def rpy_from_rotation(R):
    """
    Convert a rotation matrix to roll-pitch-yaw (XYZ extrinsic / ZYX
    intrinsic) Euler angles, in radians. Used only for human-readable
    reporting, not for internal computation.
    """
    sy = np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
    singular = sy < 1e-8
    if not singular:
        roll = np.arctan2(R[2, 1], R[2, 2])
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = np.arctan2(R[1, 0], R[0, 0])
    else:
        roll = np.arctan2(-R[1, 2], R[1, 1])
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = 0.0
    return np.array([roll, pitch, yaw])


def pretty_print_pose(T, label="End-effector pose"):
    p = position(T)
    rpy = np.degrees(rpy_from_rotation(rotation(T)))
    print(f"\n{label}")
    print("Position (m):     x={:.5f}  y={:.5f}  z={:.5f}".format(*p))
    print("Orientation (deg): roll={:.3f}  pitch={:.3f}  yaw={:.3f}".format(*rpy))
    print("Homogeneous transform T:")
    print(np.array2string(T, precision=5, suppress_small=True))


if __name__ == "__main__":
    q_test = np.radians([30, -45, 60, -90, 45, 0])
    T = forward_kinematics(q_test)
    pretty_print_pose(T, label=f"FK for q(deg) = {np.degrees(q_test)}")
