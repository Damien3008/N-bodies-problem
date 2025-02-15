from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class CelestialBody:
    name: str
    mass: float
    position: np.ndarray
    velocity: np.ndarray

class SystemData:
    def __init__(self, system_name: str):
        """Initialize system from data file"""
        self.system_name = system_name
        self.bodies = []
        self._load_system()
    
    def _load_system(self):
        """Load system data from file"""
        with open(f'data/{self.system_name}_values.txt', 'r') as file:
            lines = [line.strip() for line in file.readlines()]
            
            # Determine system bodies
            if self.system_name == 'Voyager 2':
                names = ['Voyager 2', 'Sun', 'Earth', 'Saturn', 'Jupiter']
            elif self.system_name == 'solar system':
                names = ['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 
                        'Jupiter', 'Saturn', 'Uranus', 'Neptun', 'Moon', 'Ceres']
            elif self.system_name == 'halley':
                names = ['Halley comet', 'Sun']
            elif self.system_name == 'Voyager 1':
                names = ['Voyager 1', 'Sun', 'Earth', 'Saturn', 'Jupiter']
            
            n = len(names)
            
            # Read masses
            masses = []
            for i in range(n):
                masses.append(float(lines[i]))
            
            # Initialize state array
            T = np.zeros((6 * n))
            
            # Read positions and velocities
            for i in range(n, 6 * n + n):
                T[i - n] = float(lines[i])
            
            # Create bodies
            for i in range(n):
                pos = np.array([
                    T[6*i + 3],
                    T[6*i + 4],
                    T[6*i + 5]
                ])
                vel = np.array([
                    T[6*i],
                    T[6*i + 1],
                    T[6*i + 2]
                ])
                
                self.bodies.append(CelestialBody(
                    name=names[i],
                    mass=masses[i],
                    position=pos,
                    velocity=vel
                ))
    
    def get_initial_state(self) -> np.ndarray:
        """Returns initial state vector [positions, velocities]"""
        state = np.zeros(6 * len(self.bodies))
        for i, body in enumerate(self.bodies):
            # Positions
            state[3*i:3*i + 3] = body.position
            # Velocities
            state[3*len(self.bodies) + 3*i:3*len(self.bodies) + 3*i + 3] = body.velocity
        return state
    
    def get_masses(self) -> np.ndarray:
        """Returns array of masses"""
        return np.array([body.mass for body in self.bodies]) 