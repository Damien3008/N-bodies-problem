import numpy as np
from typing import Callable

class NumericalIntegrator:
    """Base class for numerical integrators"""
    def __init__(self, func: Callable, dt: float):
        self.func = func
        self.dt = dt
    
    def step(self, t: float, y: np.ndarray) -> np.ndarray:
        raise NotImplementedError

class EulerIntegrator(NumericalIntegrator):
    def step(self, t: float, y: np.ndarray) -> np.ndarray:
        return y + self.dt * self.func(t, y)

class RK4Integrator(NumericalIntegrator):
    def step(self, t: float, y: np.ndarray) -> np.ndarray:
        k1 = self.func(t, y)
        k2 = self.func(t + 0.5*self.dt, y + 0.5*self.dt*k1)
        k3 = self.func(t + 0.5*self.dt, y + 0.5*self.dt*k2)
        k4 = self.func(t + self.dt, y + self.dt*k3)
        return y + (self.dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)

class VerletIntegrator(NumericalIntegrator):
    def step(self, t: float, y: np.ndarray) -> np.ndarray:
        pos, vel = y[:len(y)//2], y[len(y)//2:]
        acc = self.func(t, y)[len(y)//2:]
        
        new_pos = pos + vel*self.dt + 0.5*acc*self.dt**2
        new_acc = self.func(t + self.dt, np.concatenate([new_pos, vel]))[len(y)//2:]
        new_vel = vel + 0.5*(acc + new_acc)*self.dt
        
        return np.concatenate([new_pos, new_vel])

class AdamsBashforthIntegrator(NumericalIntegrator):
    def __init__(self, func: Callable, dt: float, order: int = 4):
        super().__init__(func, dt)
        self.order = order
        self.history = []
    
    def step(self, t: float, y: np.ndarray) -> np.ndarray:
        self.history.append(self.func(t, y))
        if len(self.history) < self.order:
            # Use RK4 for initial steps
            return RK4Integrator(self.func, self.dt).step(t, y)
        
        if len(self.history) > self.order:
            self.history.pop(0)
            
        coeffs = {
            2: [3/2, -1/2],
            3: [23/12, -16/12, 5/12],
            4: [55/24, -59/24, 37/24, -9/24]
        }
        
        return y + self.dt * sum(c*f for c, f in zip(coeffs[self.order], reversed(self.history))) 