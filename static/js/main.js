let combinedChart = null;
let simInterval = null;

async function runSimulation() {
    const scenario = document.getElementById('scenario-select').value;
    const duration = document.getElementById('duration-input').value;
    const btn = document.getElementById('sim-btn');
    const logDiv = document.getElementById('bio-stream');
    const explDiv = document.getElementById('narrative-box');
    const reportDiv = document.getElementById('final-report');

    btn.disabled = true;
    btn.innerText = "SZÁMÍTÁS FOLYAMATBAN...";
    logDiv.innerHTML = ">>> Kapcsolódás a Secure Core-hoz...\n";
    explDiv.innerHTML = "<strong>Rendszer állapota:</strong> Inicializálás...<br><span style='color:#aaa'>Fizikai modellek betöltése...</span>";
    reportDiv.innerHTML = "<div style='padding:20px; text-align:center; color:#666;'>Az elemzés a szimuláció után jelenik meg...</div>";

    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario: scenario, duration: parseInt(duration) })
        });

        const res = await response.json();

        if (res.status === 'success') {
            logDiv.innerHTML += `>>> HIBA NAPJA GENERÁLVA: ${res.failure_day}. nap\n`;
            logDiv.innerHTML += ">>> ADATOK FOGADVA. FELDOLGOZÁS...\n";
            
            drawComparisonChart(res.data);
            try { generateFinalReport(res.data); } catch (err) { console.error(err); }
            playBackSimulation(res.data);
            
        } else {
            logDiv.innerHTML += `!!! SZERVER HIBA: ${res.message}\n`;
        }

    } catch (e) {
        console.error(e);
        logDiv.innerHTML += `!!! HÁLÓZATI HIBA: ${e}\n`;
    } finally {
        btn.disabled = false;
        btn.innerText = "ÚJ SZIMULÁCIÓ INDÍTÁSA";
    }
}

function drawComparisonChart(data) {
    const ctx = document.getElementById('feasibilityChart').getContext('2d');
    if (combinedChart) combinedChart.destroy();
    
    const labels = data.metaspace.timeline.map(d => `Nap ${d.day}`);
    
    combinedChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'MetaSpace Védelem (Vele)',
                    data: data.metaspace.timeline.map(d => d.feasibility),
                    borderColor: '#66fcf1', backgroundColor: 'rgba(102, 252, 241, 0.1)',
                    tension: 0.1, borderWidth: 2, order: 1
                },
                {
                    label: 'Hagyományos EKF (Nélküle)',
                    data: data.ekf.timeline.map(d => d.feasibility),
                    borderColor: '#e74c3c', borderDash: [5, 5],
                    tension: 0.4, borderWidth: 2, order: 2
                }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            scales: { 
                y: { min: -5, max: 105, title: {display: true, text: 'Adatgyűjtés Megbízhatósága (%)', color: '#aaa'}, grid: { color: '#333' } },
                x: { grid: { display: false } }
            },
            plugins: { legend: { labels: { color: '#fff' } } }, animation: false
        }
    });
}

function playBackSimulation(data) {
    const explDiv = document.getElementById('narrative-box');
    const statusDiv = document.getElementById('live-status');
    const logDiv = document.getElementById('bio-stream');
    
    let i = 0;
    const totalDays = data.metaspace.timeline.length;
    
    if (simInterval) clearInterval(simInterval);
    
    simInterval = setInterval(() => {
        if (i >= totalDays) {
            clearInterval(simInterval);
            statusDiv.innerHTML = "BEFEJEZVE";
            statusDiv.style.color = "#fff";
            return;
        }
        
        const msDay = data.metaspace.timeline[i];
        const ekfDay = data.ekf.timeline[i];
        
        const gpsError = parseFloat(msDay.gps_error);
        const batLevel = parseFloat(msDay.battery_level);
        const imuError = parseFloat(msDay.imu_error || 0);

        let narrative = `<strong>Nap ${msDay.day} / ${totalDays}:</strong> `;
        let isFaulty = false;
        let faultType = "";
        let faultDesc = "";

        // HIBA DETEKTÁLÁS (Prioritás)
        if (batLevel < 20.0) {
            isFaulty = true;
            faultType = "KRITIKUS ENERGIAHIÁNY";
            faultDesc = `Akku szint: ${batLevel.toFixed(1)}%`;
        } else if (batLevel < 99.0 && batLevel > 20.0 && data.scenario === 'solar_panel') {
             isFaulty = true;
             faultType = "NEGATÍV ENERGIAMÉRLEG (Napelem)";
             faultDesc = `Szint: ${batLevel.toFixed(1)}% (Csökken!)`;
        } else if (gpsError > 50.0) {
            isFaulty = true;
            faultType = "GPS JEL HIBA";
            faultDesc = `Pozíció eltérés: ${gpsError.toFixed(1)}m`;
        } else if (imuError > 0.5) {
            isFaulty = true;
            faultType = "IMU SODRÓDÁS";
            faultDesc = `Drift: ${imuError.toFixed(3)}`;
        }

        if (!isFaulty) {
            narrative += `Rendszer stabil.<br><span style="color:#aaa;">Akku: ${batLevel.toFixed(1)}% | Szenzorok: OK</span>`;
            statusDiv.innerHTML = "ADATGYŰJTÉS OK";
            statusDiv.style.color = "#0f0";
        } else {
            narrative += `<span style="color:orange"><strong>⚠️ ${faultType}!</strong> ${faultDesc}</span><br>`;
            narrative += `<div style="margin-top:8px; display:grid; grid-template-columns: 1fr 1fr; gap:10px; font-size: 0.9em;">`;
            
            // EKF
            narrative += `<div style="border-right:1px solid #444;">`;
            narrative += `<strong style="color:#e74c3c">Hagyományos EKF:</strong><br>`;
            if (ekfDay.feasibility > 90) {
                narrative += `Nem látja a hibát (100%).<br><strong>VESZÉLY: Selejt adat / Műhold elvesztés.</strong>`;
            } else {
                narrative += `Bizonytalan.<br><strong>Késői reakció.</strong>`;
            }
            narrative += `</div>`;

            // MetaSpace
            narrative += `<div>`;
            narrative += `<strong style="color:#66fcf1">MetaSpace.bio:</strong><br>`;
            if (msDay.mode === 'SAFE_MODE') {
                 narrative += `Azonnal blokkolt (0%).<br><strong>VÉDELEM: Adatbázis/Hardver védve.</strong>`;
                 statusDiv.innerHTML = "VÉDELEM AKTÍV";
                 statusDiv.style.color = "#66fcf1";
            } else if (batLevel < 40 && batLevel > 20) {
                 narrative += `DEGRADED MÓD (Figyelmeztetés).<br><strong>Felkészülés a leállásra.</strong>`;
            } else {
                 narrative += `Elemzés...`;
            }
            narrative += `</div></div>`;
        }
        
        explDiv.innerHTML = narrative;
        if (msDay.mode === 'SAFE_MODE') {
             logDiv.innerHTML += `<span style="color:red">[DAY ${i}] ALERT: ${faultType}! PROTECTION ENGAGED.</span>\n`;
             logDiv.scrollTop = logDiv.scrollHeight;
        }
        
        i++;
    }, 100);
}

function generateFinalReport(data) {
    const reportDiv = document.getElementById('final-report');
    
    let isScenarioNominal = true;
    let failureStartDay = -1;
    let failureType = "Nincs";
    let isEnergyFailure = false;

    // Hiba keresése
    for(let i=0; i<data.metaspace.timeline.length; i++) {
        const d = data.metaspace.timeline[i];
        if (parseFloat(d.gps_error) > 50) { isScenarioNominal = false; failureStartDay = i; failureType = "GPS Hiba"; break; }
        if (parseFloat(d.battery_level) < 20) { isScenarioNominal = false; failureStartDay = i; failureType = "Kritikus Energia"; isEnergyFailure = true; break; }
        if (parseFloat(d.imu_error) > 0.5) { isScenarioNominal = false; failureStartDay = i; failureType = "IMU Drift"; break; }
    }

    if (isScenarioNominal) {
        reportDiv.innerHTML = `<div style="padding:15px; border-left:4px solid #0f0;"><strong>✅ Teszt Siker:</strong> Nem történt hiba. Hatékonyság: 100%.</div>`;
        return;
    }

    const msFailDay = data.metaspace.timeline.findIndex(d => d.mode === 'SAFE_MODE');
    const ekfFailDay = data.ekf.timeline.findIndex(d => d.feasibility < 60);
    const totalDuration = data.metaspace.timeline.length;
    
    // Kárbecslés
    let ekfWaste = (ekfFailDay === -1) ? (totalDuration - failureStartDay) : (ekfFailDay - failureStartDay);
    ekfWaste = Math.max(0, ekfWaste);

    // Döntés a konklúzió szövegéről a hiba típusa alapján
    let conclusionText = "";
    let riskText = "";
    
    if (isEnergyFailure) {
        // ENERGIA HIBA ESETÉN
        riskText = "MŰHOLD ELVESZTÉSE (Dead Bus)";
        conclusionText = `<strong>Üzleti Érték:</strong> A MetaSpace beavatkozása nélkül a műhold teljesen lemerült volna ("Dead Bus"), ami a <strong>teljes küldetés és a hardver elvesztését</strong> jelentette volna. A MetaSpace "Survival Mode"-ba kapcsolva megmentette az eszközt.`;
    } else {
        // ADAT HIBA ESETÉN (GPS/IMU)
        riskText = "Szennyezett Adatbázis (Selejt)";
        conclusionText = `<strong>Üzleti Érték:</strong> A MetaSpace használatával elkerültük ${ekfWaste} napnyi felesleges adattárolást és feldolgozást, valamint megvédtük a tudományos adatbázis integritását (Selejt szűrés).`;
    }

    let html = `
        <h3 style="color:#66fcf1; margin-top:0;">Hiba Elemzés: ${failureType} (${failureStartDay}. nap)</h3>
        <table style="width:100%; font-size:13px; margin-top:10px; border-collapse:collapse;">
            <tr style="color:#aaa; border-bottom:1px solid #666;">
                <th style="text-align:left; padding:5px;">Mutató</th>
                <th style="color:#e74c3c">Hagyományos EKF</th>
                <th style="color:#66fcf1">MetaSpace</th>
            </tr>
            <tr>
                <td style="padding:5px;">Reakcióidő</td>
                <td style="color:#e74c3c">${ekfFailDay === -1 ? "SOHA" : "Késleltetett"}</td>
                <td style="color:#66fcf1; font-weight:bold;">AZONNALI</td>
            </tr>
            <tr>
                <td style="padding:5px;">Kockázat</td>
                <td style="color:#e74c3c; font-weight:bold;">${riskText}</td>
                <td style="color:#66fcf1">Kockázat elhárítva</td>
            </tr>
        </table>
        <div style="margin-top:15px; padding:10px; background:rgba(102, 252, 241, 0.1); border-radius:5px; font-size:12px; line-height:1.4;">
            ${conclusionText}
        </div>
    `;
    reportDiv.innerHTML = html;
}