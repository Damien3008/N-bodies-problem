<div align="center">

# N-Body Gravitational Simulation 🌌

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GNU-green.svg)](LICENSE)

A stunning Python-based interactive simulation of the N-body gravitational problem, featuring real astronomical data and multiple numerical integration methods. Watch the dance of planets, trace historic space missions, and explore the cosmos! 🚀

<div style="border-radius: 10px; overflow: hidden; margin: 20px 0;">
    <img src="asset/simulation_example.gif" alt="N-Body Simulation Demo" width="800"/>
</div>

</div>

## ✨ Key Features

<div align="center">

| Feature | Description |
|---------|-------------|
| 🎮 **Interactive 3D Visualization** | Dynamic real-time animation with adjustable speed |
| 🌍 **Real Astronomical Data** | Accurate planetary positions from NASA |
| 🧮 **Multiple Integration Methods** | Choose from Euler, RK2, RK4, or advanced symplectic methods |
| 🛸 **Historic Space Missions** | Simulate Voyager trajectories |
| ⚡ **High Performance** | Optimized calculations with NumPy |

</div>

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8 or higher
pip (Python package installer)
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/n-body-simulation.git
cd n-body-simulation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

#### Development Mode
```bash
python src/main.py
```

#### Production Mode
For production deployment, we use Gunicorn as our WSGI server:

1. Make the production script executable:
```bash
chmod +x run_production.sh
```

2. Create logs directory:
```bash
mkdir logs
```

3. Run the application:
```bash
./run_production.sh
```

The application will be available at `http://localhost:8050`

## 🎯 The Science Behind It

<div align="center">

### The Core Equation

$\vec{a}_i = G \sum_{j \neq i} \frac{m_j(\vec{r}_j - \vec{r}_i)}{|\vec{r}_j - \vec{r}_i|^3}$

| Parameter | Description |
|-----------|-------------|
| 🔰 G | 1.4872e-34 AU³/(M☉·day²) - Gravitational constant |
| ⭐ $m_j$ | Mass in solar masses (M☉) |
| 📏 $\vec{r}$ | Position in astronomical units (AU) |

</div>

## 🧮 Numerical Methods

| Method | Equation | Characteristics |
|--------|----------|----------------|
| **Euler** | $y_{n+1} = y_n + h f(t_n, y_n)$ | ✅ Fast computation<br>✅ Minimal memory<br>⚠️ Basic accuracy |
| **RK4** | $y_{n+1} = y_n + \frac{h}{6}(k_1 + 2k_2 + 2k_3 + k_4)$ | ✅ High accuracy<br>✅ Stable<br>⚠️ Computationally intensive |
| **Verlet** | $\vec{r}_{n+1} = \vec{r}_n + \vec{v}_n\Delta t + \frac{1}{2}\vec{a}_n\Delta t^2$ | ✅ Energy conservation<br>✅ Long-term stability<br>⚠️ Ideal for orbits |
| **Adams-Bashforth** | $y_{n+1} = y_n + \frac{h}{24}(55f_n - 59f_{n-1} + 37f_{n-2} - 9f_{n-3})$ | ✅ Efficient<br>✅ High accuracy<br>⚠️ Best for smooth systems |

## 📚 Included Scenarios


| Scenario | Features |
|----------|-----------|
| 🌞 **Solar System** | • Complete planetary system<br>• Major moons and asteroids<br>• Accurate orbital parameters |
| 🛸 **Space Missions** | • Voyager 1 & 2 trajectories<br>• Historic planetary encounters<br>• Mission timeline recreation |
| ☄️ **Cometary Orbits** | • Halley's Comet simulation<br>• Planetary perturbations<br>• Long-term orbital evolution |

## 🔧 Configuration

The production server can be configured through `run_production.sh`:
- Port: 8050 (default)
- Workers: 4 (default)
- Timeout: 120 seconds
- Log files location: `logs/` directory

## 📝 License

This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for details.