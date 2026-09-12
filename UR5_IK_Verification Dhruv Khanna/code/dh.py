"""
dh.py
-----
Standard Denavit-Hartenberg (DH) parameter model for the UR5 robotic arm.

Convention used: STANDARD DH (Distal), transform i-1 -> i:

    A_i = Rot_z(theta_i) * Trans_z(d_i) * Trans_x(a_i) * Rot_x(alpha_i)

UR5 kinematic parameters (meters, radians) - manufacturer nominal values:

    i |   a_i (m)  | alpha_i (rad) |  d_i (m)  | theta_i
    --+------------+---------------+-----------+---------
    1 |   0.00000  |   +pi/2       | 0.089159  | q1
    2 |  -0.42500  |    0          | 0.000000  | q2
    3 |  -0.39225  |    0          | 0.000000  | q3
    4 |   0.00000  |   +pi/2       | 0.10915   | q4
    5 |   0.00000  |   -pi/2       | 0.09465   | q5
    6 |   0.00000  |    0          | 0.0823    | q6
"""

import numpy as np

# UR5 fixed link parameters: (a_i, alpha_i, d_i)
UR5_A = [0.0, -0.425, -0.39225, 0.0, 0.0, 0.0]
UR5_ALPHA = [np.pi / 2, 0.0, 0.0, np.pi / 2, -np.pi / 2, 0.0]
UR5_D = [0.089159, 0.0, 0.0, 0.10915, 0.09465, 0.0823]

N_JOINTS = 6


def dh_table(q):
    """
    Return the full DH parameter table for a given joint vector q (rad),
    as a list of dicts: [{'a':..,'alpha':..,'d':..,'theta':..}, ...]
    """
    q = np.asarray(q, dtype=float).flatten()
    assert len(q) == N_JOINTS, f"Expected {N_JOINTS} joint values, got {len(q)}"
    table = []
    for i in range(N_JOINTS):
        table.append({
            "a": UR5_A[i],
            "alpha": UR5_ALPHA[i],
            "d": UR5_D[i],
            "theta": q[i],
        })
    return table


def dh_transform(a, alpha, d, theta):
    """
    Standard DH homogeneous transformation matrix A_i (4x4) built from
    a single row of DH parameters.
    """
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)

    A = np.array([
        [ct, -st * ca,  st * sa, a * ct],
        [st,  ct * ca, -ct * sa, a * st],
        [0,        sa,       ca,      d],
        [0,         0,        0,      1],
    ])
    return A


def all_transforms(q):
    """
    Return the list of individual homogeneous transforms [A1, A2, ..., A6]
    for the given joint vector q.
    """
    table = dh_table(q)
    return [dh_transform(row["a"], row["alpha"], row["d"], row["theta"]) for row in table]


if __name__ == "__main__":
    # Quick sanity print of the DH table at the zero configuration
    q0 = [0, 0, 0, 0, 0, 0]
    for i, row in enumerate(dh_table(q0), start=1):
        print(f"Joint {i}: a={row['a']:.5f}  alpha={row['alpha']:.5f}  "
              f"d={row['d']:.5f}  theta={row['theta']:.5f}")
