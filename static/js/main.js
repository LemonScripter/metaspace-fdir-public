/**
 * MetaSpace Research Edition - Frontend Controller
 * Verzió: 1.4.5 (Enhanced Log with Fault Detection)
 *
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

/**
 * Executes the simulation by fetching data from the Python backend.
 */
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

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Computing Physics Model...';
    }
    
    if (liveStatus) {
        liveStatus.innerText = "SOLVER RUNNING...";
        liveStatus.style.color = "#f1c40f"; 
    }
    
    if(placeholder) {
        console.log("[runSimulation] Hiding placeholder");
        placeholder.style.display = 'none';
    }
    if(canvas) {
        console.log("[runSimulation] Showing canvas");
        canvas.style.display = 'block';
        console.log("[runSimulation] Canvas dimensions:", canvas.width, "x", canvas.height);
    } else {
        console.error("[runSimulation] Canvas element not found!");
    }

    fetch('/api/simulation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenario, duration: duration })
    })
    .then(response => {
        if (!response.ok) throw new Error('Server returned ' + response.status);
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            console.log("[Telemetry] Data received. Forcing extraction...");
            console.log("[Debug] Full response structure:", Object.keys(data));
            console.log("[Debug] data.data type:", typeof data.data);
            console.log("[Debug] data.data keys:", data.data ? Object.keys(data.data) : "N/A");
            
            // FIX: Brutális mélységi keresés a többszörösen becsomagolt JSON-ben
            const payload = data.data && data.data.telemetry_log ? data.data : (data.data && data.data.data ? data.data.data : (data.data || data));
            const log = payload.telemetry_log || [];

            console.log("[Debug] Payload type:", typeof payload);
            console.log("[Debug] Payload keys:", payload ? Object.keys(payload) : "N/A");
            console.log("[Debug] Telemetry log length:", log.length);

            if (log.length > 0) {
                console.log("[Debug] First log entry keys:", Object.keys(log[0]));
                console.log("[Debug] First entry ekf_reliability:", log[0].ekf_reliability);
                console.log("[Debug] First entry metaspace_integrity:", log[0].metaspace_integrity);
                
                const results = {
                    time: log.map(p => (p.time || 0) / 1440), // Átváltás napra (1440 perc = 1 nap)
                    ekf: log.map(p => p.ekf_reliability !== undefined ? p.ekf_reliability : 100),
                    metaspace: log.map(p => p.metaspace_integrity !== undefined ? p.metaspace_integrity : 100),
                    battery: log.map(p => p.battery_percent !== undefined ? p.battery_percent : 100),
                    failure_type: payload.failure_type || scenario,
                    failure_time: payload.failure_time ? payload.failure_time / 1440 : null // Átváltás napra
                };
                
                console.log("[Debug] Results object:", {
                    timeLength: results.time.length,
                    ekfLength: results.ekf.length,
                    metaspaceLength: results.metaspace.length,
                    ekfFirst5: results.ekf.slice(0, 5),
                    metaspaceFirst5: results.metaspace.slice(0, 5),
                    ekfUnique: [...new Set(results.ekf)],
                    metaspaceUnique: [...new Set(results.metaspace)]
                });
                
                console.log("[Debug] Calling renderChart...");
                renderChart(results, scenario); 
                console.log("[Debug] renderChart called successfully");
                
                // Eredmények értelmezése és megjelenítése
                interpretResults(results, scenario, payload);
            } else {
                console.error("Critical: Telemetry log not found in response.");
            }
            
            updateComponentGrid(payload.components || []);
            // A narrative-t nem írjuk felül, mert az interpretation.js már írja az Analysis dobozba
            // generateNarrative(payload.narrative || "Complete", payload.bio_logs || []);
            
            // Csak a bio-stream-et frissítjük
            const streamBox = document.getElementById('bio-stream');
            if (streamBox && Array.isArray(payload.bio_logs)) {
                streamBox.innerHTML = '';
                payload.bio_logs.forEach((log, index) => {
                    setTimeout(() => {
                        const entry = document.createElement('div');
                        entry.className = 'log-entry';
                        entry.innerHTML = `<span class="log-timestamp">[T+${index}]</span> ${log}`;
                        streamBox.appendChild(entry);
                        streamBox.scrollTop = streamBox.scrollHeight;
                    }, index * 40);
                });
            }
        }
    })
    .catch(error => {
        console.error('[System] Mapping Error:', error);
        if (liveStatus) {
            liveStatus.innerText = "ERROR";
            liveStatus.style.color = "var(--alert-red)";
        }
    })
    .finally(() => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = 'EXECUTE SIMULATION';
        }
    });
}

/**
 * Renders the Chart.js visualization with annotations and explanations.
 */
function renderChart(results, scenario) {
    console.log("[renderChart] Called with results:", results);
    const ctx = document.getElementById('feasibilityChart');
    console.log("[renderChart] Canvas element:", ctx);
    if (!ctx || !results || !results.time) {
        console.error("[renderChart] Missing requirements:", {
            ctx: !!ctx,
            results: !!results,
            time: results ? !!results.time : false
        });
        return;
    }

    console.log("[renderChart] Canvas display style before:", ctx.style.display);
    ctx.style.display = 'block';
    console.log("[renderChart] Canvas display style after:", ctx.style.display);

    if (chartInstance) {
        console.log("[renderChart] Destroying previous chart instance");
        chartInstance.destroy();
    }

    console.log("[renderChart] Creating new Chart instance...");
    console.log("[renderChart] EKF data length:", results.ekf ? results.ekf.length : 0);
    console.log("[renderChart] MetaSpace data length:", results.metaspace ? results.metaspace.length : 0);
    console.log("[renderChart] Chart.js available:", typeof Chart !== 'undefined');
    
    try {
        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: results.time,
                datasets: [
                    {
                        label: 'EKF Reliability',
                        data: results.ekf,
                        borderColor: '#ff6b6b',
                        backgroundColor: 'rgba(255, 107, 107, 0.1)',
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0,
                        tension: 0.4,
                        borderWidth: 2
                    },
                    {
                        label: 'MetaSpace',
                        data: results.metaspace,
                        borderColor: '#00f3ff',
                        backgroundColor: 'transparent',
                        fill: false,
                        pointRadius: 0,
                        pointHoverRadius: 0,
                        pointBackgroundColor: 'transparent',
                        pointBorderColor: 'transparent',
                        tension: 0.4,
                        borderWidth: 2,
                        stepped: false,
                        spanGaps: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                elements: {
                    line: {
                        tension: 0.4,
                        fill: false
                    },
                    point: {
                        radius: 0,
                        hoverRadius: 0
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                scales: {
                    y: { 
                        beginAtZero: true, 
                        max: 110, 
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#ccc' },
                        title: {
                            display: true,
                            text: 'Reliability / Integrity (%)',
                            color: '#ccc',
                            font: { family: 'Rajdhani', size: 12 }
                        }
                    },
                    x: { 
                        grid: { display: false }, 
                        ticks: { maxTicksLimit: 12, color: '#666' },
                        title: {
                            display: true,
                            text: 'Time (days)',
                            color: '#ccc',
                            font: { family: 'Rajdhani', size: 12 }
                        }
                    }
                },
                plugins: {
                    legend: { 
                        display: true,
                        labels: { 
                            color: '#ccc', 
                            font: { family: 'Rajdhani', size: 12 },
                            usePointStyle: true,
                            padding: 15
                        },
                        position: 'top'
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#00f3ff',
                        bodyColor: '#fff',
                        borderColor: '#00f3ff',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            title: function(context) {
                                return `Time: ${parseFloat(context[0].label).toFixed(2)} days`;
                            },
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y.toFixed(1);
                                return `${label}: ${value}%`;
                            },
                            afterBody: function(context) {
                                if (results.failure_time !== null && context[0].parsed.x >= results.failure_time) {
                                    return '⚠ Failure Active';
                                }
                                return '';
                            }
                        }
                    }
                }
            }
        });
        console.log("[renderChart] Chart instance created successfully");
        console.log("[renderChart] Chart data:", chartInstance.data);
        console.log("[renderChart] Chart datasets:", chartInstance.data.datasets.map(d => ({
            label: d.label,
            dataLength: d.data.length,
            first5: d.data.slice(0, 5)
        })));
    } catch (error) {
        console.error("[renderChart] Error creating chart:", error);
        throw error;
    }
}

/**
 * Updates the health matrix grid.
 */
function updateComponentGrid(components) {
    const grid = document.getElementById('component-grid');
    if (!grid || !Array.isArray(components)) return;
    
    grid.innerHTML = '';
    components.forEach(comp => {
        const card = document.createElement('div');
        card.className = 'component-card';
        const sColor = comp.status === 'HEALTHY' ? 'var(--success-green)' : 'var(--alert-red)';
        const description = comp.description || 'Komponens részletei nem elérhetők.';
        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <span style="font-size:13px; color:#666;">ID: ${comp.id}</span>
                <span class="status-dot" style="background:${sColor}; width:10px; height:10px; border-radius:50%; box-shadow:0 0 8px ${sColor};"></span>
            </div>
            <div style="font-weight:bold; margin-bottom:10px; font-size:16px; color:#eee;">${comp.name}</div>
            <div style="font-size:13px; text-transform:uppercase; color:${sColor}; margin-bottom:14px; font-weight:bold;">${comp.status}</div>
            <div style="font-size:13px; color:#aaa; line-height:1.6; flex:1; overflow-y:auto;">${description}</div>
        `;
        grid.appendChild(card);
    });
}

/**
 * Generates narrative and bio-logs.
 */
function generateNarrative(text, logs) {
    const navBox = document.getElementById('narrative-box');
    const streamBox = document.getElementById('bio-stream');
    
    if (navBox) navBox.innerHTML = `<span>></span> ${text}`;
    
    if (streamBox && Array.isArray(logs)) {
        streamBox.innerHTML = '';
        logs.forEach((log, index) => {
            setTimeout(() => {
                const entry = document.createElement('div');
                entry.className = 'log-entry';
                entry.innerHTML = `<span class="log-timestamp">[T+${index}]</span> ${log}`;
                streamBox.appendChild(entry);
                streamBox.scrollTop = streamBox.scrollHeight;
            }, index * 40);
        });
    }
}

function closeModalAndRun() {
    const modal = document.getElementById('intro-modal');
    if (modal) modal.style.display = 'none';
    runSimulation();
}

window.onclick = function(event) {
    const modal = document.getElementById('intro-modal');
    if (event.target == modal) modal.style.display = "none";
};

// End of Controller Stack
console.log("[System] Controller Verified.");

/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */