import numpy as np
from ..utils.constants import G  # Must be in correct units: AU^3 / (M_sun · day^2)

def n_body_acceleration(positions: np.ndarray, masses: np.ndarray) -> np.ndarray:
    """
    Calculate gravitational accelerations for an N-body system in 3D.
    positions: shape (n, 3) in AU
    masses: shape (n,) in Solar masses
    Returns: shape (n, 3) accelerations in AU/day^2
    """
    n = len(masses)
    acc = np.zeros_like(positions)
    
    for i in range(n):
        for j in range(n):
            if i != j:
                r_vec = positions[j] - positions[i]     # Vector from i to j
                dist = np.linalg.norm(r_vec)
                acc[i] += G * masses[j] * r_vec / dist**3
    
    return acc

def n_body_derivative(t: float, state: np.ndarray, masses: np.ndarray) -> np.ndarray:
    """
    Returns the time derivative of the state [pos, vel].
    state: shape (6*n,) -> first 3*n are positions, last 3*n are velocities
    masses: shape (n,)
    """
    n = len(masses)
    # Split positions, velocities
    positions = state[:3*n].reshape(n, 3)
    velocities = state[3*n:].reshape(n, 3)
    
    # Compute accelerations
    accelerations = n_body_acceleration(positions, masses)
    
    # Derivative of [pos, vel] = [vel, acc]
    return np.concatenate([velocities.flatten(), accelerations.flatten()])