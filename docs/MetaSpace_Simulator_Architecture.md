# MetaSpace Simulator: Modular Architecture Plan
## HTML + Python Stack for Commercial Satellite Mission Simulation

**Purpose:** Design specification for a web-based, modular simulator  
**Target:** Engineers, researchers, decision-makers  
**Tech Stack:** HTML5 + Python (Flask) + JavaScript (D3.js)  
**Date:** December 27, 2025  
**Status:** Architecture planning phase

---

## ARCHITECTURE OVERVIEW

### The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (HTML5)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Dashboard | Scenarios | Results | Timeline | Charts  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          ↓ API Calls (JSON) ↑ Real-time Updates (WebSocket)
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (Python Flask)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ API Routes | Simulation Engine | Data Processing    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          ↓ Import ↑ Export
┌─────────────────────────────────────────────────────────────┐
│            DATA LAYER (CSV, JSON, SQLite)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Config Files | Simulation State | Results Database  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## MODULE 1: FRONTEND (HTML5 + JavaScript)

### 1.1 File Structure

```
frontend/
├── index.html              (Main dashboard)
├── css/
│   ├── style.css           (Global styling)
│   ├── dashboard.css       (Dashboard layout)
│   ├── charts.css          (Chart styling)
│   └── responsive.css      (Mobile friendly)
├── js/
│   ├── app.js              (Main application logic)
│   ├── api.js              (API communication)
│   ├── simulator.js        (Simulation control)
│   ├── charts.js           (D3.js visualization)
│   ├── timeline.js         (Timeline rendering)
│   └── utils.js            (Helper functions)
└── html/
    ├── dashboard.html      (Main view)
    ├── scenarios.html      (Scenario selection)
    ├── results.html        (Results view)
    ├── timeline.html       (Timeline detail)
    └── settings.html       (Configuration)
```

### 1.2 Key Components

**Dashboard (index.html):**
```html
<!DOCTYPE html>
<html>
<head>
  <title>MetaSpace Simulator</title>
  <link rel="stylesheet" href="css/style.css">
  <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
  <div id="header">
    <h1>MetaSpace Simulator - Landsat 9</h1>
    <div id="status">Ready</div>
  </div>
  
  <div id="main">
    <div id="left-panel">
      <!-- Scenario selection -->
      <div class="panel">
        <h3>Simulation Settings</h3>
        <label>Mission Duration:</label>
        <input type="range" id="duration" min="30" max="1825" value="365">
        <span id="duration-display">365 days</span>
        
        <label>Failure Injection:</label>
        <select id="scenario">
          <option value="gps_antenna">GPS Antenna Damage</option>
          <option value="imu_drift">IMU Calibration Drift</option>
          <option value="star_tracker">Star Tracker Degradation</option>
          <option value="battery_failure">Battery Cell Failure</option>
          <option value="thermal_radiator">Thermal Radiator Delamination</option>
          <option value="xband_antenna">X-band Antenna Corrosion</option>
          <option value="reaction_wheel">Reaction Wheel Bearing Friction</option>
          <option value="solar_panel">Solar Panel Micro-crack</option>
          <option value="sband_lna">S-band LNA Failure</option>
          <option value="multi_component">Multi-Component Cascade</option>
        </select>
        
        <button id="run-simulation">Run Simulation</button>
      </div>
    </div>
    
    <div id="center-panel">
      <!-- Real-time visualization -->
      <div id="timeline-container"></div>
      <div id="metrics-display"></div>
    </div>
    
    <div id="right-panel">
      <!-- Comparison metrics -->
      <div class="metric">
        <h4>EKF Detection</h4>
        <p id="ekf-detection">-- ms</p>
      </div>
      <div class="metric">
        <h4>MetaSpace Detection</h4>
        <p id="metaspace-detection">-- ms</p>
      </div>
      <div class="metric">
        <h4>Data Loss (EKF)</h4>
        <p id="ekf-loss">-- %</p>
      </div>
      <div class="metric">
        <h4>Data Loss (MetaSpace)</h4>
        <p id="metaspace-loss">-- %</p>
      </div>
      <div class="metric">
        <h4>Mission Success (EKF)</h4>
        <p id="ekf-success">-- %</p>
      </div>
      <div class="metric">
        <h4>Mission Success (MetaSpace)</h4>
        <p id="metaspace-success">-- %</p>
      </div>
    </div>
  </div>
  
  <script src="js/app.js"></script>
</body>
</html>
```

**API Communication (js/api.js):**
```javascript
// API wrapper for backend communication

class SimulatorAPI {
  constructor(baseURL = 'http://localhost:5000') {
    this.baseURL = baseURL;
  }
  
  // Run simulation
  async runSimulation(config) {
    const response = await fetch(`${this.baseURL}/api/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    return response.json();
  }
  
  // Get scenario details
  async getScenario(scenarioName) {
    const response = await fetch(
      `${this.baseURL}/api/scenarios/${scenarioName}`
    );
    return response.json();
  }
  
  // Get results
  async getResults(simulationId) {
    const response = await fetch(
      `${this.baseURL}/api/results/${simulationId}`
    );
    return response.json();
  }
  
  // Stream real-time updates
  subscribeToUpdates(simulationId, callback) {
    const eventSource = new EventSource(
      `${this.baseURL}/api/stream/${simulationId}`
    );
    eventSource.onmessage = (event) => {
      callback(JSON.parse(event.data));
    };
    return eventSource;
  }
}

// Usage
const api = new SimulatorAPI();
```

**Timeline Visualization (js/timeline.js):**
```javascript
// D3.js-based timeline visualization

class TimelineRenderer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.svg = d3.select(this.container).append('svg');
  }
  
  render(ekfTimeline, metaspaceTimeline) {
    const margin = { top: 20, right: 30, bottom: 30, left: 60 };
    const width = 1000 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;
    
    // Create timeline groups
    const g = this.svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // EKF timeline
    g.selectAll('.ekf-point')
      .data(ekfTimeline)
      .enter()
      .append('circle')
      .attr('class', 'ekf-point')
      .attr('cx', d => d.time)
      .attr('cy', 50)
      .attr('r', 5)
      .style('fill', d => d.type === 'detection' ? 'red' : 'orange');
    
    // MetaSpace timeline
    g.selectAll('.metaspace-point')
      .data(metaspaceTimeline)
      .enter()
      .append('circle')
      .attr('class', 'metaspace-point')
      .attr('cx', d => d.time)
      .attr('cy', 150)
      .attr('r', 5)
      .style('fill', d => d.type === 'detection' ? 'green' : 'lightgreen');
    
    // Add labels
    g.append('text').attr('x', -40).attr('y', 55).text('EKF');
    g.append('text').attr('x', -40).attr('y', 155).text('MetaSpace');
  }
}
```

---

## MODULE 2: BACKEND (Python Flask)

### 2.1 Project Structure

```
backend/
├── app.py                  (Flask application)
├── config.py               (Configuration)
├── requirements.txt        (Dependencies)
├── modules/
│   ├── __init__.py
│   ├── simulator.py        (Main simulation engine)
│   ├── ekf_model.py        (EKF implementation)
│   ├── metaspace.py        (MetaSpace.bio logic)
│   ├── landsat9.py         (Landsat 9 model)
│   ├── failure.py          (Failure injection)
│   ├── metrics.py          (Metrics calculation)
│   └── database.py         (Data persistence)
├── scenarios/
│   ├── gps_antenna.json
│   ├── imu_drift.json
│   ├── star_tracker.json
│   ├── battery_failure.json
│   ├── thermal_radiator.json
│   ├── xband_antenna.json
│   ├── reaction_wheel.json
│   ├── solar_panel.json
│   ├── sband_lna.json
│   └── multi_component.json
├── data/
│   ├── landsat9_config.csv
│   ├── sensor_specs.csv
│   └── results.sqlite
└── tests/
    ├── test_ekf.py
    ├── test_metaspace.py
    └── test_scenarios.py
```

### 2.2 Main Application (app.py)

```python
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import time
from modules.simulator import SimulationEngine
from modules.database import ResultsDB

app = Flask(__name__)
CORS(app)

# Initialize simulator
simulator = SimulationEngine()
db = ResultsDB()

# Configuration
@app.route('/api/config', methods=['GET'])
def get_config():
    """Get simulator configuration"""
    return jsonify({
        'mission_duration_min': 30,
        'mission_duration_max': 1825,
        'available_scenarios': [
            'gps_antenna',
            'imu_drift',
            'star_tracker',
            'battery_failure',
            'thermal_radiator',
            'xband_antenna',
            'reaction_wheel',
            'solar_panel',
            'sband_lna',
            'multi_component'
        ]
    })

# Scenario endpoints
@app.route('/api/scenarios/<scenario_name>', methods=['GET'])
def get_scenario(scenario_name):
    """Get scenario details"""
    with open(f'scenarios/{scenario_name}.json') as f:
        return jsonify(json.load(f))

# Simulation endpoints
@app.route('/api/simulate', methods=['POST'])
def run_simulation():
    """Run simulation with given configuration"""
    config = request.json
    
    # Validate configuration
    if not config.get('scenario') or not config.get('duration'):
        return jsonify({'error': 'Missing scenario or duration'}), 400
    
    # Run simulation
    sim_id = simulator.run(
        scenario=config['scenario'],
        duration=config['duration'],
        seed=config.get('seed', None)
    )
    
    # Return simulation ID and initial results
    results = simulator.get_results(sim_id)
    return jsonify({
        'simulation_id': sim_id,
        'status': 'running',
        'results': results
    })

# Results endpoints
@app.route('/api/results/<sim_id>', methods=['GET'])
def get_results(sim_id):
    """Get simulation results"""
    results = simulator.get_results(sim_id)
    if not results:
        return jsonify({'error': 'Simulation not found'}), 404
    return jsonify(results)

@app.route('/api/timeline/<sim_id>', methods=['GET'])
def get_timeline(sim_id):
    """Get detailed timeline for visualization"""
    timeline = simulator.get_timeline(sim_id)
    return jsonify(timeline)

# Real-time streaming
@app.route('/api/stream/<sim_id>')
def stream_updates(sim_id):
    """Stream real-time updates during simulation"""
    def generate():
        while simulator.is_running(sim_id):
            update = simulator.get_update(sim_id)
            yield f"data: {json.dumps(update)}\n\n"
            time.sleep(0.1)
    
    return Response(generate(), mimetype='text/event-stream')

# Export results
@app.route('/api/export/<sim_id>/<format>', methods=['GET'])
def export_results(sim_id, format):
    """Export results in various formats"""
    results = simulator.get_results(sim_id)
    
    if format == 'csv':
        # Convert to CSV
        csv_data = simulator.to_csv(results)
        return send_file(
            io.BytesIO(csv_data.encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'simulation_{sim_id}.csv'
        )
    elif format == 'json':
        return send_file(
            io.BytesIO(json.dumps(results).encode()),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'simulation_{sim_id}.json'
        )
    else:
        return jsonify({'error': 'Unsupported format'}), 400

# Health check
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### 2.3 Simulation Engine (modules/simulator.py)

```python
import json
import random
from datetime import datetime, timedelta
from .ekf_model import EKFSimulator
from .metaspace import MetaSpaceSimulator
from .landsat9 import Landsat9Model
from .failure import FailureInjector
from .metrics import MetricsCalculator

class SimulationEngine:
    def __init__(self):
        self.simulations = {}
        self.results = {}
    
    def run(self, scenario, duration, seed=None):
        """Run a complete simulation"""
        if seed:
            random.seed(seed)
        
        sim_id = self._generate_id()
        
        # Load scenario
        with open(f'scenarios/{scenario}.json') as f:
            scenario_config = json.load(f)
        
        # Initialize models
        landsat9 = Landsat9Model()
        failure_injector = FailureInjector(scenario_config)
        
        # Run parallel simulations
        ekf_results = self._run_ekf_simulation(
            landsat9, failure_injector, duration
        )
        metaspace_results = self._run_metaspace_simulation(
            landsat9, failure_injector, duration
        )
        
        # Calculate metrics
        metrics = MetricsCalculator.compare(
            ekf_results, metaspace_results
        )
        
        # Store results
        self.results[sim_id] = {
            'simulation_id': sim_id,
            'scenario': scenario,
            'duration': duration,
            'timestamp': datetime.now().isoformat(),
            'ekf': ekf_results,
            'metaspace': metaspace_results,
            'metrics': metrics
        }
        
        return sim_id
    
    def _run_ekf_simulation(self, landsat9, failure_injector, duration):
        """Run EKF-based simulation"""
        ekf = EKFSimulator(landsat9)
        
        results = {
            'detection_times': [],
            'decision_times': [],
            'data_loss': 0,
            'scenes_collected': 0,
            'anomalies_detected': 0,
            'timeline': []
        }
        
        # Simulate day by day
        for day in range(duration):
            # Inject failures
            failures = failure_injector.get_failures_for_day(day)
            for failure in failures:
                ekf.inject_failure(failure)
            
            # Run EKF logic
            ekf.update()
            
            # Collect metrics
            if ekf.anomaly_detected:
                results['detection_times'].append(ekf.detection_latency)
                results['anomalies_detected'] += 1
            
            results['scenes_collected'] += ekf.scenes_today
            results['data_loss'] += ekf.data_loss_today
            
            # Record timeline
            results['timeline'].append({
                'day': day,
                'ekf_confidence': ekf.gps_confidence,
                'scenes': ekf.scenes_today,
                'data_loss': ekf.data_loss_today
            })
        
        return results
    
    def _run_metaspace_simulation(self, landsat9, failure_injector, duration):
        """Run MetaSpace.bio simulation"""
        metaspace = MetaSpaceSimulator(landsat9)
        
        results = {
            'detection_times': [],
            'decision_times': [],
            'data_loss': 0,
            'scenes_collected': 0,
            'anomalies_detected': 0,
            'timeline': [],
            'feasibility_percent': []
        }
        
        # Simulate day by day
        for day in range(duration):
            # Inject failures
            failures = failure_injector.get_failures_for_day(day)
            for failure in failures:
                metaspace.inject_failure(failure)
            
            # Run MetaSpace logic
            metaspace.update()
            
            # Collect metrics
            if metaspace.anomaly_detected:
                results['detection_times'].append(metaspace.detection_latency)
                results['decision_times'].append(metaspace.decision_latency)
                results['anomalies_detected'] += 1
            
            results['scenes_collected'] += metaspace.scenes_today
            results['data_loss'] += metaspace.data_loss_today
            results['feasibility_percent'].append(metaspace.mission_feasibility)
            
            # Record timeline
            results['timeline'].append({
                'day': day,
                'feasibility': metaspace.mission_feasibility,
                'mode': metaspace.execution_mode,
                'scenes': metaspace.scenes_today,
                'data_loss': metaspace.data_loss_today
            })
        
        return results
    
    def get_results(self, sim_id):
        """Get simulation results"""
        if sim_id not in self.results:
            return None
        
        return self.results[sim_id]
    
    def get_timeline(self, sim_id):
        """Get detailed timeline"""
        results = self.get_results(sim_id)
        if not results:
            return None
        
        return {
            'ekf_timeline': results['ekf']['timeline'],
            'metaspace_timeline': results['metaspace']['timeline']
        }
    
    def _generate_id(self):
        """Generate unique simulation ID"""
        return f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
```

### 2.4 EKF Model (modules/ekf_model.py)

```python
import numpy as np
from datetime import datetime

class EKFSimulator:
    def __init__(self, landsat9_model):
        self.landsat9 = landsat9_model
        
        # State vector (15 elements)
        self.x = np.zeros(15)
        self.P = np.eye(15)  # Covariance matrix
        
        # Measurement noise
        self.R = np.diag([10, 10, 10, 0.05, 0.05, 0.05, 0.001, 0.001, 0.001, 0.001, 0.001, 0.01, 1, 0.01])
        
        # Process noise
        self.Q = np.diag([0.1, 0.1, 0.1, 0.01, 0.01, 0.01, 0.001, 0.001, 0.001, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01])
        
        # Confidence levels
        self.gps_confidence = 100.0
        self.imu_confidence = 100.0
        
        # Daily metrics
        self.scenes_today = 0
        self.data_loss_today = 0
        self.anomaly_detected = False
        self.detection_latency = 0
    
    def update(self):
        """Run EKF update for one day"""
        # Prediction step
        self.x = self._predict(self.x)
        self.P = self.P + self.Q
        
        # Get measurements
        gps_meas = self.landsat9.get_gps_measurement()
        imu_meas = self.landsat9.get_imu_measurement()
        
        # Update step with GPS
        self.x, self.P = self._update(self.x, self.P, gps_meas)
        
        # Health assessment
        self._assess_health()
        
        # Science data collection
        self.scenes_today = 700 * (self.gps_confidence / 100.0)
        self.data_loss_today = 100 - self.scenes_today
    
    def _predict(self, x):
        """Prediction step of EKF"""
        # Simple motion model
        F = np.eye(15)
        F[0:3, 3:6] = np.eye(3) * 1.0  # dt = 1 day
        return F @ x
    
    def _update(self, x, P, measurement):
        """Update step of EKF"""
        # Measurement model
        H = np.zeros((3, 15))
        H[0:3, 0:3] = np.eye(3)
        
        # Innovation
        y = measurement - H @ x
        
        # Innovation covariance
        S = H @ P @ H.T + self.R[0:3, 0:3]
        
        # Kalman gain
        K = P @ H.T @ np.linalg.inv(S)
        
        # Update state
        x = x + K @ y
        
        # Update covariance
        P = (np.eye(15) - K @ H) @ P
        
        return x, P
    
    def _assess_health(self):
        """Assess sensor health"""
        # GPS confidence decreases if covariance is high
        if self.P[0, 0] > 100:
            self.gps_confidence -= 10
        elif self.P[0, 0] < 10:
            self.gps_confidence += 5
        
        self.gps_confidence = max(0, min(100, self.gps_confidence))
        
        # Check for anomalies
        if self.P[0, 0] > 1000:
            self.anomaly_detected = True
            self.detection_latency = 5000  # 5 seconds
    
    def inject_failure(self, failure):
        """Inject a failure into the system"""
        if failure['type'] == 'gps_antenna':
            # Increase GPS measurement noise
            self.R[0:3, 0:3] *= 10
```

### 2.5 MetaSpace Logic (modules/metaspace.py)

```python
class MetaSpaceSimulator:
    def __init__(self, landsat9_model):
        self.landsat9 = landsat9_model
        
        # Health status for each component
        self.health = {
            'gps': 2,  # 2=MISSION_CAPABLE, 1=DEGRADED, 0=FAULT
            'imu': 2,
            'thermal': 2,
            'power': 2,
            'comm': 2
        }
        
        # Mission feasibility
        self.mission_feasibility = 100
        self.execution_mode = 'FULL_MISSION'
        
        # Metrics
        self.scenes_today = 0
        self.data_loss_today = 0
        self.anomaly_detected = False
        self.detection_latency = 0
        self.decision_latency = 0
    
    def update(self):
        """Run MetaSpace update for one day"""
        # Level 2: Chip-level checks (1ms)
        self._level2_checks()
        
        # Level 1: Module health checks (10ms)
        self._level1_assessment()
        
        # Level 0: Master arbiter decision (100ms)
        self._level0_arbiter()
        
        # Adapt execution
        self._adapt_execution()
        
        # Science data collection
        if self.execution_mode == 'FULL_MISSION':
            self.scenes_today = 700
            self.data_loss_today = 0
        elif self.execution_mode == 'PARTIAL_MISSION':
            self.scenes_today = int(700 * (self.mission_feasibility / 100))
            self.data_loss_today = 700 - self.scenes_today
        else:
            self.scenes_today = 0
            self.data_loss_today = 700
    
    def _level2_checks(self):
        """Chip-level sensor validation"""
        # Check for timeouts, CRC errors, etc.
        gps_data = self.landsat9.get_gps_measurement()
        imu_data = self.landsat9.get_imu_measurement()
        
        # Validate data
        if not self._validate_data(gps_data):
            self.health['gps'] = 0  # FAULT
            self.detection_latency = 50
        if not self._validate_data(imu_data):
            self.health['imu'] = 0
    
    def _level1_assessment(self):
        """Module-level health assessment"""
        for sensor in ['gps', 'imu', 'thermal', 'power', 'comm']:
            if self.health[sensor] == 0:
                # Already detected as FAULT
                pass
            elif self.health[sensor] == 1:
                # DEGRADED
                pass
            else:
                # MISSION_CAPABLE
                pass
    
    def _level0_arbiter(self):
        """Master arbiter feasibility calculation"""
        # Navigation points (0-20)
        nav_points = 0
        nav_points += 10 if self.health['gps'] == 2 else (5 if self.health['gps'] == 1 else 0)
        nav_points += 5 if self.health['imu'] == 2 else (2 if self.health['imu'] == 1 else 0)
        nav_points += 5  # Radar always OK in this model
        
        # Observation points (0-30)
        obs_points = 30  # Both cameras OK
        
        # Power points (0-20)
        power_points = 20 if self.health['power'] == 2 else (10 if self.health['power'] == 1 else 0)
        
        # Propulsion points (0-15)
        prop_points = 15
        
        # Communication points (0-15)
        comm_points = 15 if self.health['comm'] == 2 else (10 if self.health['comm'] == 1 else 0)
        
        # Calculate total feasibility
        self.mission_feasibility = (
            (nav_points * 20) +
            (obs_points * 30) +
            (power_points * 20) +
            (prop_points * 15) +
            (comm_points * 15)
        ) / 100
        
        self.decision_latency = 200  # 200 ms decision
    
    def _adapt_execution(self):
        """Adapt execution mode based on feasibility"""
        if self.mission_feasibility >= 100:
            self.execution_mode = 'FULL_MISSION'
        elif self.mission_feasibility >= 30:
            self.execution_mode = 'PARTIAL_MISSION'
        elif self.mission_feasibility >= 5:
            self.execution_mode = 'MINIMAL_PARTIAL'
        else:
            self.execution_mode = 'SAFE_RETURN'
    
    def inject_failure(self, failure):
        """Inject a failure"""
        if failure['type'] == 'gps_antenna':
            self.health['gps'] = 0
            self.anomaly_detected = True
```

---

## MODULE 3: DATA & CONFIGURATION

### 3.1 Scenario Configuration (scenarios/gps_antenna.json)

```json
{
  "name": "GPS Antenna Damage",
  "description": "Meteor impact damages GPS antenna, 70% gain loss",
  "failure_day": 150,
  "failure_type": "gps_antenna",
  "parameters": {
    "gps_gain_loss": 0.7,
    "gps_timeout": 1.0
  },
  "expected_ekf_detection": "5000 ms",
  "expected_metaspace_detection": "100 ms",
  "expected_ekf_data_loss": "30-40%",
  "expected_metaspace_data_loss": "0%"
}
```

### 3.2 Landsat 9 Configuration (data/landsat9_config.csv)

```
parameter,value,unit
mass,2900,kg
power_nominal,5,kW
data_rate_xband,800,Mbps
orbital_altitude,705,km
inclination,98.2,deg
scene_width,185,km
scene_length,180,km
scenes_per_day,700,count
battery_capacity,50,Ah
design_life,5,years
```

---

## MODULE 4: DEPLOYMENT STRUCTURE

### 4.1 Development Setup

```bash
# Create project structure
mkdir metaspace-simulator
cd metaspace-simulator

# Frontend
mkdir frontend
cd frontend
touch index.html
mkdir css js html
# ... create files

# Backend
cd ..
mkdir backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install flask flask-cors numpy

# Create modules
mkdir modules scenarios data tests
touch app.py config.py requirements.txt

# requirements.txt
Flask==2.3.0
flask-cors==4.0.0
numpy==1.24.0
Werkzeug==2.3.0
```

### 4.2 Running the Simulator

```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate
python app.py

# Terminal 2: Open frontend
cd frontend
python -m http.server 8000  # or use any simple HTTP server

# Visit http://localhost:8000 in browser
```

---

## MODULE 5: WORKFLOW

### 5.1 User Interaction Flow

```
1. USER OPENS SIMULATOR
   └─ Frontend loads (index.html)
   └─ JavaScript initializes (app.js)
   └─ Fetches configuration from backend (GET /api/config)

2. USER SELECTS SCENARIO
   └─ Chooses from dropdown (GPS Antenna, IMU Drift, etc.)
   └─ Sets mission duration (30-1825 days)
   └─ Clicks "Run Simulation"

3. FRONTEND SENDS REQUEST
   └─ POST /api/simulate with config
   └─ Returns simulation_id

4. BACKEND RUNS SIMULATION
   └─ Initializes EKF simulator
   └─ Initializes MetaSpace simulator
   └─ Runs both in parallel for each day
   └─ Collects metrics

5. FRONTEND DISPLAYS RESULTS (Real-time)
   └─ Subscribes to /api/stream/sim_id
   └─ Receives updates every 100ms
   └─ Renders timeline visualization

6. RESULTS AVAILABLE
   └─ GET /api/results/sim_id returns complete data
   └─ User can export as CSV/JSON
   └─ User can view detailed timeline
```

### 5.2 Simulation Flow

```
DAY 0:
  ├─ Load scenario config
  ├─ Initialize models
  └─ Start iteration

DAY 1-N:
  ├─ [EKF Path]
  │  ├─ Run EKF prediction
  │  ├─ Run EKF update
  │  ├─ Assess health (confidence levels)
  │  └─ Record metrics
  │
  ├─ [MetaSpace Path]
  │  ├─ Level 2 checks (1ms)
  │  ├─ Level 1 assessment (10ms)
  │  ├─ Level 0 arbiter (100ms)
  │  ├─ Calculate feasibility %
  │  ├─ Select execution mode
  │  └─ Record metrics
  │
  └─ Compare & log

FINAL:
  ├─ Calculate statistics
  ├─ Generate comparison metrics
  └─ Save results
```

---

## MODULE 6: KEY IMPLEMENTATION DETAILS

### 6.1 Modular Design Principles

```
SEPARATION OF CONCERNS:
  ├─ Frontend: UI, visualization, user interaction
  ├─ Backend: Simulation logic, data processing
  ├─ Data: Configuration, scenarios, results
  └─ Tests: Validation of each component

SCALABILITY:
  ├─ Easy to add new scenarios
  ├─ Easy to add new failure modes
  ├─ Easy to modify Landsat 9 parameters
  └─ Easy to create new visualizations

REUSABILITY:
  ├─ EKF module can be used independently
  ├─ MetaSpace module can be used independently
  ├─ Metrics calculator is generic
  └─ Database layer is abstracted
```

### 6.2 Testing Strategy

```python
# tests/test_ekf.py
def test_ekf_initialization():
    ekf = EKFSimulator(mock_landsat9)
    assert ekf.gps_confidence == 100
    assert ekf.scenes_today == 0

# tests/test_metaspace.py
def test_feasibility_calculation():
    ms = MetaSpaceSimulator(mock_landsat9)
    ms.health = {'gps': 0, 'imu': 2, 'thermal': 2, 'power': 2, 'comm': 2}
    ms._level0_arbiter()
    assert 70 < ms.mission_feasibility < 100

# tests/test_scenarios.py
def test_gps_antenna_scenario():
    sim = SimulationEngine()
    sim_id = sim.run('gps_antenna', duration=365)
    results = sim.get_results(sim_id)
    assert len(results['ekf']['timeline']) == 365
    assert len(results['metaspace']['timeline']) == 365
```

---

## SUMMARY: DEVELOPMENT ROADMAP

```
WEEK 1: Backend Infrastructure
  ├─ Flask app setup
  ├─ EKF model implementation
  ├─ MetaSpace model implementation
  └─ Basic API endpoints

WEEK 2: Simulation Engine
  ├─ Landsat 9 model
  ├─ Failure injection
  ├─ Metrics calculation
  └─ Results storage

WEEK 3: Frontend
  ├─ Dashboard layout
  ├─ API integration
  ├─ Basic visualization
  └─ Scenario selection

WEEK 4: Visualization & Polish
  ├─ Timeline rendering (D3.js)
  ├─ Real-time updates
  ├─ Export functionality
  └─ Testing & debugging
```

---

## CONCLUSION

This modular architecture enables:

✅ **Moduláris fejlesztés** - Párhuzamosan lehet dolgozni (FE + BE)  
✅ **Könnyű tesztelés** - Minden modul önálló testelhető  
✅ **Könnyű bővítés** - Új scenario = 1 JSON fájl  
✅ **Könnyű deployment** - Flask + static HTML  
✅ **Valós validáció** - Landsat 9 valós adatokkal  

---

**Document Version:** 1.0  
**Status:** Ready for implementation  
**Estimated development time:** 14 weeks  
**Estimated cost:** €120K-150K (simulation development)  
**Estimated value:** €100M+ (proof of concept for 3-5 spacecraft)
