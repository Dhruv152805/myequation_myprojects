"""
inverse_kinematics.py
----------------------
Numerical Inverse Kinematics for the UR5 using the Damped Least-Squares
(Levenberg-Marquardt) method on the geometric Jacobian.

Why numerical (vs. closed-form)?
UR5 has a spherical-wrist-less offset structure (d4, d5, d6 offsets are not
all coincident at a single wrist point in the way that permits the
classical Pieper closed-form decoupling), so a robust, general, and easy
to verify approach for a training/verification tool is the iterative
Jacobian-based method below. It converges quadratically near the solution
and degrades gracefully (via damping) near singularities, which also lets
us reuse jacobian.py directly for the verification/Jacobian requirement.

Algorithm (per iteration):
    e = pose_error(T_current, T_desired)      # 6x1 [dp; d_orientation]
    J = geometric_jacobian(q)
    dq = J^T (J J^T + lambda^2 I)^-1 e         # damped least squares
    q  = q + dq
until ||e|| < tol or max_iters reached.
"""

import numpy as np
from forward_kinematics import forward_kinematics
from jacobian import geometric_jacobian

DEFAULT_TOL = 1e-6
DEFAULT_MAX_ITERS = 500
DEFAULT_DAMPING = 1e-2
DEFAULT_STEP_CLAMP = 0.5  # rad, max joint step per iteration


def rotation_error(R_current, R_desired):
    """
    Orientation error as an axis*angle (so(3)) vector, computed from
    R_err = R_desired * R_current^T.
    """
    R_err = R_desired @ R_current.T
    # angle-axis from rotation matrix (Rodrigues' formula, robust form)
    cos_theta = (np.trace(R_err) - 1.0) / 2.0
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    theta = np.arccos(cos_theta)
    if abs(theta) < 1e-8:
        return np.zeros(3)
    axis = (1.0 / (2.0 * np.sin(theta))) * np.array([
        R_err[2, 1] - R_err[1, 2],
        R_err[0, 2] - R_err[2, 0],
        R_err[1, 0] - R_err[0, 1],
    ])
    return axis * theta


def pose_error(T_current, T_desired):
    """6x1 pose error vector [position_error(3); orientation_error(3)]."""
    p_err = T_desired[0:3, 3] - T_current[0:3, 3]
    o_err = rotation_error(T_current[0:3, 0:3], T_desired[0:3, 0:3])
    return np.concatenate([p_err, o_err])


def inverse_kinematics(T_desired, q_init=None, tol=DEFAULT_TOL,
                        max_iters=DEFAULT_MAX_ITERS,
                        damping=DEFAULT_DAMPING,
                        step_clamp=DEFAULT_STEP_CLAMP,
                        verbose=False):
    """
    Solve for joint angles q such that FK(q) ~= T_desired, using damped
    least-squares (Levenberg-Marquardt) iteration on the geometric
    Jacobian.

    Returns
    -------
    dict with keys:
        'q'          : solution joint vector (rad), wrapped to (-pi, pi]
        'converged'  : bool
        'iterations' : number of iterations used
        'final_error': norm of the final 6x1 pose error
        'error_history': list of error norms per iteration
    """
    if q_init is None:
        q = np.zeros(6)
    else:
        q = np.array(q_init, dtype=float).copy()

    error_history = []
    converged = False
    it = 0
    for it in range(1, max_iters + 1):
        T_current = forward_kinematics(q)
        e = pose_error(T_current, T_desired)
        err_norm = np.linalg.norm(e)
        error_history.append(err_norm)

        if verbose and (it % 25 == 0 or it == 1):
            print(f"iter {it:4d}  |error| = {err_norm:.3e}")

        if err_norm < tol:
            converged = True
            break

        J = geometric_jacobian(q)
        JJt = J @ J.T
        lam2I = (damping ** 2) * np.eye(6)
        dq = J.T @ np.linalg.solve(JJt + lam2I, e)

        # clamp step size for numerical stability
        dq = np.clip(dq, -step_clamp, step_clamp)
        q = q + dq

    # wrap final joint angles to (-pi, pi]
    q_wrapped = (q + np.pi) % (2 * np.pi) - np.pi

    return {
        "q": q_wrapped,
        "converged": converged,
        "iterations": it,
        "final_error": error_history[-1] if error_history else None,
        "error_history": error_history,
    }


def inverse_kinematics_multi_start(T_desired, n_starts=8, seed=42, **kwargs):
    """
    Run damped-least-squares IK from several random initial guesses and
    return the best (lowest final error, converged preferred) solution.
    Improves robustness against local minima / poor seeds.
    """
    rng = np.random.default_rng(seed)
    best = None
    for i in range(n_starts):
        q0 = rng.uniform(-np.pi, np.pi, size=6) if i > 0 else np.zeros(6)
        result = inverse_kinematics(T_desired, q_init=q0, **kwargs)
        if best is None:
            best = result
        else:
            better = (result["converged"] and not best["converged"]) or (
                result["converged"] == best["converged"] and
                result["final_error"] < best["final_error"]
            )
            if better:
                best = result
        if best["converged"] and best["final_error"] < 1e-8:
            break
    return best


if __name__ == "__main__":
    # Build a reachable target pose from a known joint vector, then solve
    # IK for it and check we recover a pose that reproduces the same T.
    q_true = np.radians([20, -60, 90, -75, 50, 15])
    T_target = forward_kinematics(q_true)

    result = inverse_kinematics(T_target, verbose=True)
    print("\nq_true (deg):    ", np.degrees(q_true))
    print("q_solution (deg):", np.degrees(result["q"]))
    print("Converged:", result["converged"], " iterations:", result["iterations"])
    print("Final error norm:", result["final_error"])
