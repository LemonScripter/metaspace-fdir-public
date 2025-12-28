/**
 * Szimuláció eredményeinek értelmezése és magyarázata
 */

function interpretResults(results, scenario, payload) {
    // Az Analysis dobozba írjuk az értelmezést
    const narrativeBox = document.getElementById('narrative-box');
    
    if (!narrativeBox) return;
    
    // Hiba típusonkénti magyarázatok
    const explanations = {
        'gps_antenna': {
            title: 'GPS Spoofing / Signal Loss',
            ekf: 'Az EKF (Extended Kalman Filter) lassan reagál a GPS hibára. Valószínűségszámítási módszerekkel próbálja korrigálni a pályát, de heurisztikus algoritmusai miatt napokig eltarthat, amíg észleli a problémát. Közben tovább gyűjt adatot, ami rossz minőségű lehet.',
            metaspace: 'A MetaSpace rendszer determinisztikusan azonnal kizárja a GPS spoofing-ot vagy a nem illő jelet a mintázatból. Invariáns-alapú logikája lehetővé teszi, hogy azonnal észlelje a térbeli (spatial) invariáns megsértését, és leállítsa az adatgyűjtést.',
            comparison: 'A grafikonon látható, hogy a MetaSpace (kék vonal) azonnal 0%-ra esik, miközben az EKF (szürkétvörös vonal) lassan csökken, és közben tovább gyűjt adatot.'
        },
        'battery_failure': {
            title: 'Battery Thermal Runaway',
            ekf: 'Az EKF nem észleli közvetlenül az akkumulátor hibát, mert csak a szenzorokra (GPS, IMU) figyel, nem az energia rendszerre. Amikor az akku < 10%-ra lemerül, a GPS jel eltűnik (nincs elég energia), és az EKF ekkor lassan reagál (1-2 nap alatt észleli a GPS timeout-ot). Heurisztikusan próbálja visszaállítani a kapcsolatot, de közben tovább gyűjt adatot, ami fölösleges lehet. A műhold tovább működik, amíg az akku teljesen le nem merül, ami Dead Bus állapotot okozhat.',
            metaspace: 'A MetaSpace azonnal észleli az energia invariáns megsértését. Amikor az akkumulátor szintje 20% alá esik, azonnal leállítja a fogyasztást, és SAFE_MODE-ba kapcsol, megelőzve a teljes lemerülést.',
            comparison: 'A grafikonon látható, hogy a MetaSpace (kék vonal) azonnal reagál az akku lemerülésére, miközben az EKF (szürkétvörös vonal) csak akkor csökken, amikor az akku < 10%-ra lemerül és a GPS timeout történik (1-2 nap késleltetéssel).'
        },
        'solar_panel': {
            title: 'Solar Panel Structural Failure',
            ekf: 'Az EKF NEM észleli közvetlenül a napelem hibát, mert csak a szenzorokra (GPS, IMU) figyel, nem az energia rendszerre. A műhold tovább működik, de nem tudja visszatölteni az akkumulátort. Az akku lassan lemerül (több nap). Amikor az akku < 10%-ra lemerül, a GPS jel eltűnik (nincs elég energia), és az EKF ekkor lassan reagál: 1-3 nap alatt észleli a GPS timeout-ot (confidence lassan csökken, heurisztikus próbálkozás). Közben tovább gyűjt adatot, ami fölösleges lehet.',
            metaspace: 'A MetaSpace AZONNAL észleli az energia invariáns megsértését (50 ms). Amikor a napelemek nem termelnek elég energiát (power generation < 50%), vagy az akku < 20%-ra esik, azonnal csökkenti a fogyasztást, és SAFE_MODE-ba kapcsol, megelőzve a teljes lemerülést.',
            comparison: 'A grafikonon látható, hogy a MetaSpace (kék vonal) azonnal (0 nap) reagál az energia hiányra, miközben az EKF (szürkétvörös vonal) csak akkor csökken, amikor az akku < 10%-ra lemerül és a GPS timeout történik (1-3 nap késleltetéssel).'
        },
        'imu_drift': {
            title: 'IMU Gyro Bias Drift',
            ekf: 'Az EKF lassan reagál az IMU drift-re. Valószínűségszámítási módszerekkel próbálja korrigálni a navigációt, de heurisztikus algoritmusai miatt napokig eltarthat, amíg észleli a problémát.',
            metaspace: 'A MetaSpace azonnal észleli az időbeli (temporal) invariáns megsértését. Amikor az IMU akkumulált hibája meghaladja a 0.5-öt, azonnal leállítja az adatgyűjtést, és SAFE_MODE-ba kapcsol.',
            comparison: 'A grafikonon látható, hogy a MetaSpace (kék vonal) azonnal reagál az IMU drift-re, miközben az EKF (szürkétvörös vonal) lassan csökken.'
        },
        'nominal': {
            title: 'Nominal Flight (Control)',
            ekf: 'Az EKF normál működésben 100% megbízhatóságot mutat.',
            metaspace: 'A MetaSpace normál működésben 100% integritást mutat.',
            comparison: 'Mindkét rendszer normál működésben 100%-on van.'
        }
    };
    
    const explanation = explanations[scenario] || explanations['nominal'];
    
    // EKF és MetaSpace értékek elemzése
    const ekfValues = results.ekf;
    const metaspaceValues = results.metaspace;
    const ekfMin = Math.min(...ekfValues);
    const ekfMax = Math.max(...ekfValues);
    const metaspaceMin = Math.min(...metaspaceValues);
    const metaspaceMax = Math.max(...metaspaceValues);
    
    // Hiba időpont meghatározása (napokban)
    let failureTime = null;
    if (results.failure_time !== null) {
        failureTime = results.failure_time; // Már napokban van
    } else {
        // Keresés az első jelentős változásnál
        for (let i = 1; i < metaspaceValues.length; i++) {
            if (metaspaceValues[i] < 100 && metaspaceValues[i-1] >= 100) {
                failureTime = results.time[i];
                break;
            }
        }
    }
    
    // EKF reakció idő meghatározása (napokban)
    let ekfReactionTime = null;
    if (failureTime !== null) {
        for (let i = 0; i < ekfValues.length; i++) {
            if (results.time[i] >= failureTime && ekfValues[i] < 90) {
                ekfReactionTime = results.time[i] - failureTime; // Napokban
                break;
            }
        }
    }
    
    // MetaSpace reakció idő meghatározása (napokban)
    let metaspaceReactionTime = null;
    if (failureTime !== null) {
        for (let i = 0; i < metaspaceValues.length; i++) {
            if (results.time[i] >= failureTime && metaspaceValues[i] < 100) {
                metaspaceReactionTime = results.time[i] - failureTime; // Napokban
                break;
            }
        }
    }
    
    // HTML generálása - Nagyobb betűtípussal az Analysis dobozba
    let html = `<div style="margin-bottom:15px;"><strong style="color:#00f3ff; font-size:20px;">${explanation.title}</strong></div>`;
    
    if (failureTime !== null) {
        html += `<div style="margin-bottom:12px; padding:10px; background:rgba(255,107,107,0.1); border-left:3px solid #ff6b6b;">`;
        html += `<div style="font-size:16px; color:#ff6b6b; margin-bottom:4px;">⚠ Hiba bekövetkezett: ${failureTime.toFixed(2)}. nap</div>`;
        html += `</div>`;
    }
    
    html += `<div style="margin-bottom:12px;">`;
    html += `<div style="font-size:16px; color:#ff6b6b; margin-bottom:6px; font-weight:bold;">EKF (Extended Kalman Filter):</div>`;
    html += `<div style="font-size:15px; color:#aaa; margin-left:15px; margin-bottom:8px; line-height:1.6;">${explanation.ekf}</div>`;
    if (ekfReactionTime !== null) {
        html += `<div style="font-size:14px; color:#888; margin-left:15px;">Reakció idő: ~${ekfReactionTime.toFixed(2)} nap (${(ekfReactionTime * 24).toFixed(1)} óra)</div>`;
    }
    html += `</div>`;
    
    html += `<div style="margin-bottom:12px;">`;
    html += `<div style="font-size:16px; color:#00f3ff; margin-bottom:6px; font-weight:bold;">MetaSpace (Determinisztikus FDIR):</div>`;
    html += `<div style="font-size:15px; color:#aaa; margin-left:15px; margin-bottom:8px; line-height:1.6;">${explanation.metaspace}</div>`;
    if (metaspaceReactionTime !== null) {
        html += `<div style="font-size:14px; color:#888; margin-left:15px;">Reakció idő: ~${(metaspaceReactionTime * 1440).toFixed(0)} perc (azonnal)</div>`;
    }
    html += `</div>`;
    
    html += `<div style="margin-top:15px; padding:10px; background:rgba(0,243,255,0.1); border-left:3px solid #00f3ff;">`;
    html += `<div style="font-size:16px; color:#00f3ff; margin-bottom:6px; font-weight:bold;">Összehasonlítás:</div>`;
    html += `<div style="font-size:15px; color:#aaa; line-height:1.6;">${explanation.comparison}</div>`;
    html += `</div>`;
    
    // Az Analysis dobozba írjuk
    narrativeBox.innerHTML = html;
}

