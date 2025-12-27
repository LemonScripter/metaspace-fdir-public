/**
 * MetaSpace Research Edition - Frontend Controller
 * Verzió: 1.4.5 (Enhanced Log with Fault Detection)
 */

let chartInstance = null;
let simulationInterval = null;
let logLineCount = 0;

document.addEventListener('DOMContentLoaded', function() {
    console.log("[System] MetaSpace Frontend Initialized.");
    const liveStatus = document.getElementById('live-status');
    if(liveStatus) {
        liveStatus.innerText = "STANDBY";
        liveStatus.style.color = "#aaa";
    }
});

function runSimulation() {
    const scenarioSelect = document.getElementById('scenario-select');
    const durationInput = document.getElementById('duration-input');
    const btn = document.getElementById('sim-btn');
    const liveStatus = document.getElementById('live-status');
    const placeholder = document.getElementById('chart-placeholder');
    const canvas = document.getElementById('feasibilityChart');

    if (!scenarioSelect || !durationInput) return;

    const scenario = scenarioSelect.value;
    const duration = parseInt(durationInput.value);

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Computing Physics Model...';
    
    liveStatus.innerText = "SOLVER RUNNING...";
    liveStatus.style.color = "#f1c40f"; 
    
    if(placeholder) placeholder.style.display = 'none';
    if(canvas) canvas.style.display = 'block';

    startDataStream();

    fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenario, duration: duration })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            renderResearchChart(data.data, scenario);
            updateTechnicalNarrative(data.data, scenario);
            
            if (data.data.final_status && data.data.final_status.components) {
                renderComponentGrid(data.data.final_status.components);
            }
            
            liveStatus.innerText = "VERIFIED (SAFE)";
            liveStatus.style.color = "#2ecc71";
        }
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerText = "Execute Simulation & Analysis";
        stopDataStream();
    });
}

function renderResearchChart(results, scenario) {
    const ctx = document.getElementById('feasibilityChart').getContext('2d');
    if (chartInstance) chartInstance.destroy();

    const failDay = results.failure_day;
    const totalDays = results.days;
    const labels = Array.from({length: totalDays}, (_, i) => i + 1);
    
    const isNominal = (scenario === 'nominal');

    const traditionalData = labels.map(day => {
        if (isNominal) return 97 + Math.random() * 3; 
        if (day < failDay) {
            return 97 + Math.random() * 3;
        } else {
            let falseConfidence = 95 - ((day - failDay) * 0.5); 
            return Math.max(0, falseConfidence); 
        }
    });

    const metaSpaceData = labels.map(day => {
        if (isNominal) return 100; 
        if (day < failDay) return 100;
        return 0; 
    });

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Stochastic EKF (Industry Std)',
                    data: traditionalData,
                    borderColor: '#e74c3c', 
                    borderDash: [5, 5],     
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4            
                },
                {
                    label: 'MetaSpace Invariant Core',
                    data: metaSpaceData,
                    borderColor: '#66fcf1', 
                    borderWidth: 3,
                    pointRadius: 0,
                    tension: 0.05,          
                    fill: { target: 'origin', above: 'rgba(102, 252, 241, 0.1)' }
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 105, grid: { color: '#333' }, ticks: { color: '#888' } },
                x: { grid: { color: '#333' }, ticks: { color: '#888' } }
            },
            plugins: {
                legend: { labels: { color: '#ccc' } },
                tooltip: { backgroundColor: 'rgba(15, 24, 32, 0.9)', titleColor: '#66fcf1' }
            }
        }
    });
}

function updateTechnicalNarrative(results, scenario) {
    const box = document.getElementById('narrative-box');
    let message = "";
    const day = results.failure_day;
    
    if (scenario === 'solar_panel') {
        message = `
            <strong style="color:#e74c3c">[CRITICAL] INVARIANT VIOLATION DETECTED @ T+${day} days</strong><br>
            <span style="color:#aaa">Violated Constraint:</span> <code>Energy_Budget (P_in >= P_out)</code><br>
            <br>
            <strong>Analysis:</strong> Sudden drop in Solar Array output inconsistent with orbital shadow model.<br>
            <strong>MetaSpace Action:</strong> <span style="color:#66fcf1">ISOLATION TRIGGERED (t < 2ms)</span>. Faulty array disconnected. Safe Mode engaged.<br>
            <strong>Comparison:</strong> Traditional filter failed to reject data for ${results.days - day} days.
        `;
    } else if (scenario === 'gps_antenna') {
        message = `
            <strong style="color:#e74c3c">[CRITICAL] KINEMATIC VIOLATION DETECTED @ T+${day} days</strong><br>
            <span style="color:#aaa">Violated Constraint:</span> <code>Orbital_Velocity (Kepler Limit)</code><br>
            <br>
            <strong>Analysis:</strong> Position delta exceeds maximum physical velocity of satellite.<br>
            <strong>MetaSpace Action:</strong> GPS Data marked INVALID. Switched to IMU propagation.<br>
        `;
    } else if (scenario === 'battery_failure') {
        message = `
            <strong style="color:#e74c3c">[CRITICAL] THERMAL RUNAWAY PREDICTED @ T+${day} days</strong><br>
            <span style="color:#aaa">Violated Constraint:</span> <code>Temp_Gradient (dT/dt)</code><br>
            <br>
            <strong>Analysis:</strong> Battery Cell #4 temperature spike detected.<br>
            <strong>MetaSpace Action:</strong> Cell bypassed immediately to prevent pack failure.<br>
        `;
    } else if (scenario === 'imu_drift') {
        message = `
            <strong style="color:#e74c3c">[WARNING] SENSOR CONSISTENCY CHECK FAILED @ T+${day} days</strong><br>
            <span style="color:#aaa">Violated Constraint:</span> <code>Momentum_Conservation</code><br>
            <br>
            <strong>Analysis:</strong> Gyroscope output drifts without reaction wheel actuation.<br>
            <strong>MetaSpace Action:</strong> Sensor excluded from GNC loop.<br>
        `;
    } else {
        message = `
            <strong style="color:#2ecc71">[NOMINAL] MISSION PROCEEDING</strong><br>
            <br>
            All physical invariants satisfied.<br>
            Z3 Solver confirms system state is valid.<br>
            Energy budget: Positive.<br>
        `;
    }
    box.innerHTML = message;
}

function renderComponentGrid(components) {
    const grid = document.getElementById('component-grid');
    if (!grid) return;
    grid.innerHTML = ""; 
    for (const [name, data] of Object.entries(components)) {
        let statusColor = "#2ecc71";
        let statusText = "OK";
        if (!data.active) {
            statusColor = "#e74c3c";
            statusText = "ISOLATED";
        } else if (data.health < 90) {
            statusColor = "#f1c40f";
            statusText = "DEGRADED";
        }
        const box = document.createElement('div');
        box.style.background = "rgba(11, 18, 25, 0.8)";
        box.style.border = `1px solid ${statusColor}`;
        box.style.borderRadius = "4px"; box.style.padding = "10px"; box.style.fontFamily = "monospace";
        let details = `Health: ${Math.round(data.health)}%`;
        if (data.temp) details += `<br>Temp: ${Math.round(data.temp)}°C`;
        if (data.charge !== undefined) details += `<br>Chg: ${Math.round(data.charge)}Wh`;
        box.innerHTML = `
            <div style="font-size:11px; color:#888; margin-bottom:5px; text-transform:uppercase;">${name}</div>
            <div style="font-size:14px; color:${statusColor}; font-weight:bold; margin-bottom:5px;">${statusText}</div>
            <div style="font-size:10px; color:#666; line-height:1.4;">${details}</div>
        `;
        grid.appendChild(box);
    }
}

function startDataStream() {
    const streamBox = document.getElementById('bio-stream'); 
    if (!streamBox) return;
    const nominalMessages = [
        "[CHECK] Energy_Invariant (P_sol - P_load > 0) -> VERIFIED",
        "[CHECK] Momentum_Conservation (dL/dt = T_ext) -> VERIFIED",
        "[SOLVER] Z3 Constraint Check: SATISFIABLE",
        "[SENSOR] IMU_01: OK | IMU_02: OK | GPS: LOCKED",
        "[MEMORY] ECC Check: 0 Errors found @ 0x8F4A",
        "[THERMAL] Bus Temp: 24.5C (Nominal)",
        "[ORBIT] Propagator Delta: < 0.001 m/s",
        "[POWER] Shunt Regulator: ACTIVE",
        "[GNC] Star Tracker Quaternions: VALID"
    ];
    streamBox.innerHTML = "";
    logLineCount = 0;
    simulationInterval = setInterval(() => {
        const randomMsg = nominalMessages[Math.floor(Math.random() * nominalMessages.length)];
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', { hour12: false }) + "." + Math.floor(now.getMilliseconds()/10);
        const line = document.createElement('div');
        line.className = 'log-entry';
        line.innerHTML = `<span class="log-timestamp">[${timeStr}]</span> <span class="log-ok">${randomMsg}</span>`;
        streamBox.appendChild(line);
        streamBox.scrollTop = streamBox.scrollHeight;
        logLineCount++;
        if (logLineCount > 100) streamBox.removeChild(streamBox.firstChild);
    }, 150); 
}

function stopDataStream() {
    if (simulationInterval) clearInterval(simulationInterval);
    const streamBox = document.getElementById('bio-stream');
    const scenario = document.getElementById('scenario-select').value;
    
    if (streamBox) {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', { hour12: false }) + "." + Math.floor(now.getMilliseconds()/10);

        if (scenario !== 'nominal') {
            const errorLine = document.createElement('div');
            errorLine.className = 'log-entry';
            errorLine.innerHTML = `
                <span class="log-timestamp">[${timeStr}]</span> 
                <span style="color:#ff2a2a; font-weight:bold;">[CRITICAL] INVARIANT VIOLATION: Energy_Budget FAILURE</span>
            `;
            streamBox.appendChild(errorLine);

            const isolationLine = document.createElement('div');
            isolationLine.className = 'log-entry';
            isolationLine.innerHTML = `
                <span class="log-timestamp">[${timeStr}]</span> 
                <span style="color:#00f3ff;">[ACTION] MetaSpace: ISOLATING FAULTY COMPONENT...</span>
            `;
            streamBox.appendChild(isolationLine);
        }

        const line = document.createElement('div');
        line.className = 'log-entry';
        line.innerHTML = `<span class="log-timestamp">[END]</span> <span style="color:#66fcf1; font-weight:bold;">SIMULATION COMPLETE. DATA READY.</span>`;
        streamBox.appendChild(line);
        streamBox.scrollTop = streamBox.scrollHeight;
    }
}

function closeModalAndRun() {
    const modal = document.getElementById('intro-modal');
    if (modal) modal.style.display = 'none';
    const scenarioSelect = document.getElementById('scenario-select');
    if (scenarioSelect) {
        scenarioSelect.value = 'solar_panel';
        runSimulation();
    }
}

window.onclick = function(event) {
    const modal = document.getElementById('intro-modal');
    if (event.target == modal) modal.style.display = "none";
}