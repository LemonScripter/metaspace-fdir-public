# 🔄 MetaSpace Szimulációs Folyamat - Lépésről Lépésre Dokumentáció

## ❓ Kérdés
Ha egy szimulációt futtatok, akkor születik-e validációs jegyzőkönyv is?

## ✅ Válasz: **NEM, jelenleg NEM generálódik automatikusan**

---

## 📋 SZIMULÁCIÓS FOLYAMAT - LÉPÉSRŐL LÉPÉSRE

### 1. **FRONTEND - Szimuláció Indítása**

#### Lépés 1.1: Felhasználó bemenet
```
Felhasználó:
├─ Scenario kiválasztása (dropdown)
│  ├─ "nominal" (nincs hiba)
│  ├─ "solar_panel" (napelem hiba)
│  ├─ "battery_failure" (akkumulátor hiba)
│  ├─ "gps_antenna" (GPS antenna hiba)
│  └─ "imu_drift" (IMU sodródás)
│
└─ Duration beállítása (30-1825 nap)
```

#### Lépés 1.2: "Run Simulation" gomb megnyomása
```javascript
// static/js/main.js - runSimulation()
fetch('/api/simulation', {
    method: 'POST',
    body: JSON.stringify({ 
        scenario: scenario, 
        duration: duration 
    })
})
```

**Mit generál:**
- ✅ HTTP POST kérés a backend-hez
- ❌ **NEM generál validációs jegyzőkönyvet**

---

### 2. **BACKEND - API FOGADÁS**

#### Lépés 2.1: Flask Route kezelés
```python
# app.py - /api/simulation
@app.route('/api/simulation', methods=['POST'])
def run_simulation():
    data = request.json
    sim_id = simulator.run(
        data.get('scenario', 'nominal'), 
        int(data.get('duration', 60))
    )
    results = simulator.get_results(sim_id)
    return jsonify({"status": "success", "sim_id": sim_id, "data": results})
```

**Mit generál:**
- ✅ Szimuláció ID (UUID)
- ✅ Eredmények JSON formátumban
- ❌ **NEM generál validációs jegyzőkönyvet**

---

### 3. **SIMULATOR ENGINE - Szimuláció Futtatása**

#### Lépés 3.1: Modell Inicializálás
```python
# backend/modules/simulator.py - run()
sim_id = str(uuid.uuid4())
satellite = Landsat9Model()  # Fizikai modell
ekf_solver = EKFSimulator(satellite)  # EKF logika
metaspace_solver = MetaSpaceSimulator(satellite)  # MetaSpace logika
```

**Mit generál:**
- ✅ Landsat-9 fizikai modell
- ✅ EKF szimulátor
- ✅ MetaSpace szimulátor
- ❌ **NEM generál validációs jegyzőkönyvet**

#### Lépés 3.2: Hiba Generálás
```python
# Véletlenszerű hiba generálása
failure_types = ['solar_panel', 'battery_failure', 'gps_antenna', 'imu_drift']
selected_failure = random.choice(failure_types)
failure_day = random.randint(int(duration * 0.2), int(duration * 0.8))
```

**Mit generál:**
- ✅ Hiba típusa
- ✅ Hiba időpontja (20-80% a szimulációból)
- ❌ **NEM generál validációs jegyzőkönyvet**

#### Lépés 3.3: Szimulációs Ciklus
```python
# Minden órában (60 perc)
for t in range(0, total_minutes, dt_minutes):
    # 1. Fizikai szimuláció
    telemetry = satellite.simulate_step(dt_minutes, current_failure=active_failure)
    
    # 2. EKF frissítés
    ekf_solver.update()
    
    # 3. MetaSpace frissítés
    metaspace_solver.update()
    
    # 4. Telemetria adatok gyűjtése
    history.append({
        'time': t,
        'ekf_reliability': ekf_solver.confidence,
        'metaspace_integrity': metaspace_solver.mission_feasibility,
        'battery_percent': satellite.battery_level,
        'gps_error': satellite.gps_error,
        'power_generation_w': satellite.power_generation_w,
        # ...
    })
```

**Mit generál:**
- ✅ Telemetria adatok (minden órában)
- ✅ EKF reliability értékek
- ✅ MetaSpace integrity értékek
- ❌ **NEM generál validációs jegyzőkönyvet**

#### Lépés 3.4: Eredmények Mentése
```python
# backend/modules/simulator.py - run()
result_package = {
    'sim_id': sim_id,
    'status': 'success',
    'telemetry_log': history,
    'components': self._extract_components(last_state),
    'bio_logs': bio_logs,
    'timestamp': datetime.now().isoformat(),
    'scenario': scenario,
    'duration': duration
}

# Mentés fájlba
result_file = os.path.join(self.results_dir, f"sim_{sim_id}.json")
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(result_package, f, indent=2, ensure_ascii=False)
```

**Mit generál:**
- ✅ **Szimulációs eredmény fájl** (`results/sim_*.json`)
- ✅ Telemetria log
- ✅ Komponens állapotok
- ✅ Bio logok
- ❌ **NEM generál validációs jegyzőkönyvet**

---

### 4. **FRONTEND - Eredmények Megjelenítése**

#### Lépés 4.1: Adatok Feldolgozása
```javascript
// static/js/main.js - runSimulation()
const results = {
    time: log.map(p => (p.time || 0) / 1440),  // Napokban
    ekf: log.map(p => p.ekf_reliability),
    metaspace: log.map(p => p.metaspace_integrity),
    battery: log.map(p => p.battery_percent),
    failure_type: payload.failure_type,
    failure_time: payload.failure_time / 1440
};
```

**Mit generál:**
- ✅ Grafikon adatok
- ✅ Komponens állapotok
- ✅ Analysis szöveg
- ❌ **NEM generál validációs jegyzőkönyvet**

#### Lépés 4.2: Grafikon Renderelés
```javascript
renderChart(results, scenario);  // Chart.js grafikon
updateComponentGrid(payload.components);  // Komponens mátrix
interpretResults(results, scenario, payload);  // Analysis box
```

**Mit generál:**
- ✅ Grafikon megjelenítés
- ✅ Komponens állapot megjelenítés
- ✅ Eredmény értelmezés
- ❌ **NEM generál validációs jegyzőkönyvet**

---

## 🔍 ÖSSZEFOGLALÁS: MIT GENERÁL ÉS MIT NEM?

### ✅ **AMIT GENERÁL:**

1. **Szimulációs Eredmény Fájl**
   - Helye: `results/sim_*.json`
   - Tartalom:
     - Telemetria log (minden órában)
     - Komponens állapotok
     - Bio logok
     - Hiba információk
     - Timestamp

2. **Frontend Megjelenítés**
   - Grafikon (Chart.js)
   - Komponens Health Matrix
   - Analysis Box
   - Invariant Verification Stream

### ❌ **AMIT NEM GENERÁL:**

1. **Validációs Jegyzőkönyv**
   - ❌ Nincs automatikus generálás
   - ❌ Nincs validációs teszt futtatás
   - ❌ Nincs unit teszt ellenőrzés
   - ❌ Nincs integrációs teszt ellenőrzés

---

## 🛠️ HOGYAN LEHET VALIDÁCIÓS JEGYZŐKÖNYVET GENERÁLNI?

### 1. **Parancssorból (Terminál)**

```bash
# Validáció futtatása
python backend/modules/validation_runner.py
```

**Eredmény:**
- ✅ Unit tesztek futtatása
- ✅ Integrációs tesztek futtatása
- ✅ **Validációs jegyzőkönyv generálása** (`validation_reports/validation_report_*.json`)

### 2. **API-n keresztül**

```bash
# Validáció futtatása
curl -X POST http://localhost:5000/api/validation/run
```

**Eredmény:**
- ✅ Validációs jegyzőkönyv JSON formátumban
- ✅ API válaszban visszaadva

### 3. **Integráció a Szimulációba (JAVASLAT)**

**Jelenleg:** Nincs automatikus integráció

**Javaslat:** Hozzáadni a `simulator.py`-hoz:

```python
# backend/modules/simulator.py - run() végén
def run(self, scenario, duration):
    # ... szimuláció futtatása ...
    
    # Validáció futtatása (opcionális)
    if os.environ.get('AUTO_VALIDATE', 'false').lower() == 'true':
        from backend.modules.validation_runner import run_validation
        validation_report = run_validation()
        result_package['validation_report'] = validation_report
```

---

## 🔒 MIT JELENT EZ A RENDSZER 100%-OS BIZTONSÁGOS MŰKÖDÉSÉBEN?

### 1. **Jelenlegi Állapot**

#### ✅ **AMIT BIZTOSÍT:**

1. **Szimulációs Eredmények**
   - Telemetria adatok mentése
   - Komponens állapotok rögzítése
   - Hiba információk dokumentálása

2. **Frontend Megjelenítés**
   - EKF vs MetaSpace összehasonlítás
   - Reakcióidők megjelenítése
   - Költséghatás számítás

#### ❌ **AMIT NEM BIZTOSÍT:**

1. **Validációs Garancia**
   - ❌ Nincs automatikus validáció
   - ❌ Nincs unit teszt ellenőrzés
   - ❌ Nincs integrációs teszt ellenőrzés
   - ❌ Nincs formális verifikáció

2. **Biztonsági Garancia**
   - ❌ Nincs automatikus biztonsági ellenőrzés
   - ❌ Nincs invariáns sértés detektálás
   - ❌ Nincs rendszer integritás validálás

### 2. **100%-os Biztonság Elérése**

#### Réteg 1: Szimulációs Eredmények ✅ (Van)
- Telemetria adatok
- Komponens állapotok
- Hiba információk

#### Réteg 2: Validációs Jegyzőkönyv ⚠️ (Nincs automatikus)
- Unit tesztek
- Integrációs tesztek
- **Jelenleg:** Csak manuálisan generálható

#### Réteg 3: Formális Verifikáció ❌ (Nincs)
- SMT Solver bizonyítások
- Matematikai garanciák
- **Jelenleg:** Nincs implementálva

#### Réteg 4: Valós Adatok Validálása ❌ (Nincs)
- Landsat-9 telemetria összehasonlítás
- FMEA adatbázis validálás
- **Jelenleg:** Nincs implementálva

### 3. **Biztonsági Szintek**

| Szint | Leírás | Jelenlegi Állapot | 100% Biztonság |
|-------|--------|-------------------|----------------|
| **1. Szimuláció** | Adatok generálása | ✅ Van | ⚠️ Részben |
| **2. Validáció** | Tesztek futtatása | ⚠️ Manuális | ❌ Nincs automatikus |
| **3. Verifikáció** | Matematikai bizonyítás | ❌ Nincs | ❌ Nincs |
| **4. Validálás** | Valós adatok | ❌ Nincs | ❌ Nincs |

---

## 📊 JELENLEGI BIZTONSÁGI ÁLLAPOT

### ✅ **AMIT BIZTOSÍT:**
- Szimulációs eredmények mentése
- Telemetria adatok rögzítése
- Komponens állapotok dokumentálása

### ⚠️ **AMIT RÉSZBEN BIZTOSÍT:**
- Validációs jegyzőkönyv (csak manuálisan)
- Unit tesztek (csak manuálisan)
- Integrációs tesztek (csak manuálisan)

### ❌ **AMIT NEM BIZTOSÍT:**
- Automatikus validáció
- Formális verifikáció
- Valós adatok validálása

---

## 🎯 JAVASLATOK 100%-OS BIZTONSÁG ELÉRÉSÉHEZ

### 1. **Rövid távú (1-2 hét)**

#### A. Automatikus Validáció Integrálása
```python
# backend/modules/simulator.py
def run(self, scenario, duration):
    # ... szimuláció futtatása ...
    
    # Automatikus validáció (opcionális flag)
    if os.environ.get('AUTO_VALIDATE', 'false').lower() == 'true':
        from backend.modules.validation_runner import run_validation
        validation_report = run_validation()
        result_package['validation_report'] = validation_report
```

#### B. Validációs Flag Hozzáadása
```python
# app.py - /api/simulation
@app.route('/api/simulation', methods=['POST'])
def run_simulation():
    data = request.json
    auto_validate = data.get('auto_validate', False)
    
    sim_id = simulator.run(...)
    results = simulator.get_results(sim_id)
    
    if auto_validate:
        from backend.modules.validation_runner import run_validation
        validation_report = run_validation()
        results['validation_report'] = validation_report
    
    return jsonify({"status": "success", "data": results})
```

### 2. **Közép távú (1 hónap)**

#### C. Formális Verifikáció
- SMT Solver integráció
- Invariánsok matematikai bizonyítása
- 100% determinizmus garancia

#### D. Valós Adatok Validálása
- Landsat-9 telemetria összehasonlítás
- FMEA adatbázis validálás

### 3. **Hosszú távú (3+ hónap)**

#### E. Folyamatos Validáció
- CI/CD integráció
- Automatikus validáció minden szimuláció után
- Validációs jegyzőkönyv automatikus generálása

---

## 📝 ÖSSZEFOGLALÁS

### **Jelenlegi Folyamat:**

1. ✅ Szimuláció futtatása → **Szimulációs eredmény fájl generálása**
2. ❌ Validációs jegyzőkönyv → **NEM generálódik automatikusan**
3. ⚠️ Validáció → **Csak manuálisan futtatható**

### **100%-os Biztonság Elérése:**

1. ✅ Szimulációs eredmények (Van)
2. ⚠️ Validációs jegyzőkönyv (Manuális)
3. ❌ Formális verifikáció (Nincs)
4. ❌ Valós adatok validálása (Nincs)

### **Javaslat:**

1. **Automatikus validáció integrálása** a szimulációba
2. **Validációs flag** hozzáadása az API-hoz
3. **Formális verifikáció** implementálása
4. **Valós adatok validálása** implementálása

---

**Dátum:** 2025. január  
**Verzió:** v1.4  
**Státusz:** ⚠️ Validációs jegyzőkönyv NEM generálódik automatikusan szimuláció futtatásakor

