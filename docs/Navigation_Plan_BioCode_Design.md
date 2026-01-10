# Navigációs Terv Bio-Kódba Öntésének Tervezése
## Landsat-9 Konkrét Repülési Terv Szimuláció

**Dátum:** 2025. január  
**Státusz:** Tervezési fázis  
**Cél:** Konkrét navigációs terv végrehajtásának szimulációja bio-kód vezérléssel

---

## 🎯 KONCEPCIÓ

### Alapötlet
Egy **konkrét 1 napos repülési tervet** tervezünk, amely tartalmaz:
- Konkrét orbit pozíciókat
- Konkrét imaging target-eket (földfelszíni célpontok)
- Konkrét data downlink ablakokat
- Konkrét attitude maneuver-eket
- Power és thermal management ciklusokat

**És ezt bio-kódba öntjük**, hogy a műhold **autonóm módon** tudja végrehajtani a tervet, adaptálva a rendszerállapot változásaihoz.

---

## 📋 LANDSAT-9 REPÜLÉSI TERV ELEMEI

### 1. **Orbit Paraméterek** (Valódi Landsat-9 Spec)

```
Orbit Type: Sun-synchronous
Altitude: 705 km
Inclination: 98.2°
Orbital Period: 99 minutes (~1.65 hours)
Orbits per Day: ~14.5
Scene Size: 185 km × 180 km
Daily Scenes: ~700
```

### 2. **Tipikus Napi Műveletek**

| Időpont | Orbit # | Feladat | Komponens | Kritikusság |
|---------|---------|---------|-----------|-------------|
| 00:00 UTC | 1 | Orbit start, system check | OBC, EPS | Kritikus |
| 00:15 UTC | 1 | Imaging target #1 (Amazonas) | OLI2, TIRS2 | Magas |
| 00:30 UTC | 1 | Attitude maneuver | ST_A, ST_B | Közepes |
| 00:45 UTC | 1 | Imaging target #2 (Sahara) | OLI2, TIRS2 | Magas |
| 01:00 UTC | 1 | Eclipse entry, power save | EPS | Kritikus |
| 01:15 UTC | 1 | Eclipse, minimal ops | OBC | Alacsony |
| 01:30 UTC | 1 | Eclipse exit, power restore | EPS | Kritikus |
| ... | ... | ... | ... | ... |
| 12:00 UTC | 8 | Downlink window (Alaska) | X_BAND, S_BAND | Magas |
| ... | ... | ... | ... | ... |
| 23:45 UTC | 14 | Final orbit, system check | OBC | Kritikus |

### 3. **Konkrét Imaging Target-ek** (Példa)

```
Target #1: Amazonas Rainforest
  - Coordinates: -3.4653° S, -62.2159° W
  - Priority: HIGH (deforestation monitoring)
  - Required: OLI2 + TIRS2
  - Window: 00:15-00:20 UTC (Orbit 1)

Target #2: Sahara Desert
  - Coordinates: 23.4162° N, 25.6628° E
  - Priority: MEDIUM (climate monitoring)
  - Required: OLI2
  - Window: 00:45-00:50 UTC (Orbit 1)

Target #3: Greenland Ice Sheet
  - Coordinates: 71.7069° N, -42.6043° W
  - Priority: HIGH (ice melt monitoring)
  - Required: OLI2 + TIRS2
  - Window: 08:30-08:35 UTC (Orbit 5)
```

### 4. **Data Downlink Windows** (Ground Station Kapcsolatok)

```
Station #1: Alaska (Fairbanks)
  - Window: 12:00-12:15 UTC (Orbit 8)
  - Data Rate: 800 Mbps (X-band)
  - Priority: HIGH (daily data dump)

Station #2: Svalbard (Norway)
  - Window: 18:30-18:45 UTC (Orbit 11)
  - Data Rate: 800 Mbps (X-band)
  - Priority: MEDIUM (backup)

Station #3: Wallops (Virginia, USA)
  - Window: 22:00-22:10 UTC (Orbit 13)
  - Data Rate: 150 Mbps (S-band)
  - Priority: LOW (command uplink)
```

### 5. **Power Management Ciklusok**

```
Eclipse Periods (per orbit):
  - Entry: ~35% orbit position
  - Duration: ~35 minutes
  - Exit: ~70% orbit position
  - Power Mode: Battery only, minimal ops

Sunlight Periods:
  - Solar panel orientation: Sun-tracking
  - Battery charging: Active
  - Power Mode: Full operations
```

### 6. **Attitude Maneuvers** (Képalkotáshoz)

```
Maneuver Type: Roll/Pitch adjustment
  - Purpose: Point payload at target
  - Duration: 30-60 seconds
  - Required: ST_A + ST_B (navigation)
  - Tolerance: ±0.1° accuracy
```

---

## 🔬 BIO-KÓDBA ÖNTÉS TERV

### 1. **Level 1 Bio-Code: Node Health → Task Feasibility**

**Koncepció:** Minden node health-je határozza meg, hogy egy adott feladat végrehajtható-e.

```python
# Példa: Imaging target végrehajthatóság
def check_task_feasibility(task, node_health):
    """
    task = {
        "type": "imaging",
        "target": "Amazonas",
        "required_nodes": ["OLI2", "TIRS2", "ST_A", "ST_B"],
        "priority": "HIGH",
        "window_start": "00:15:00",
        "window_end": "00:20:00"
    }
    """
    # Level 1 bio-code-ok generálása a node health-ekből
    biocodes = {}
    for node_id in task["required_nodes"]:
        health = node_health[node_id]
        biocode = generate_level1_biocode(node_id, health, get_status(health))
        biocodes[node_id] = biocode
    
    # Feasibility számítás a bio-code-okból
    min_health = min([node_health[n] for n in task["required_nodes"]])
    return min_health >= 70  # Minimum 70% health kell
```

### 2. **Level 2 Bio-Code: Module Aggregation → Task Priority**

**Koncepció:** A modulok health-je határozza meg a feladat prioritását.

```python
# Példa: Imaging task prioritás
def calculate_task_priority(task, module_health):
    """
    module_health = {
        "payload": 95,    # OLI2 + TIRS2
        "navigation": 90, # ST_A + ST_B
        "power": 85,      # EPS
        "comm": 100       # X_BAND + S_BAND
    }
    """
    # Level 2 bio-code-ok generálása
    level2_codes = {}
    for module in ["payload", "navigation", "power", "comm"]:
        biocode = generate_level2_biocode(module, level1_codes, health_history)
        level2_codes[module] = biocode
    
    # Task prioritás számítás
    if task["type"] == "imaging":
        # Imaging = payload kritikus
        priority_score = module_health["payload"] * 0.5 + \
                        module_health["navigation"] * 0.3 + \
                        module_health["power"] * 0.2
    elif task["type"] == "downlink":
        # Downlink = comm kritikus
        priority_score = module_health["comm"] * 0.6 + \
                        module_health["power"] * 0.4
    
    return priority_score
```

### 3. **Level 3 Bio-Code: Mission Decision → Task Execution**

**Koncepció:** A Level 3 bio-code határozza meg, hogy egy feladat végrehajtható-e, és milyen módban.

```python
# Példa: Task végrehajtási döntés
def execute_task_decision(task, level3_biocode):
    """
    level3_biocode dekódolása:
    - feasibility: 95%
    - action: "CONTINUE_NOMINAL"
    - safety_margin: 55
    """
    decoded = decode_level3_biocode(level3_biocode)
    
    if decoded["feasibility"] >= 90 and decoded["action"] == "CONTINUE_NOMINAL":
        # Teljes végrehajtás
        execute_task_full(task)
    elif decoded["feasibility"] >= 75 and decoded["action"] == "CONTINUE_WITH_MONITORING":
        # Csökkentett végrehajtás (pl. csak OLI2, nem TIRS2)
        execute_task_degraded(task)
    elif decoded["feasibility"] >= 40:
        # Fallback mód (pl. csak kritikus target-ek)
        execute_task_fallback(task)
    else:
        # Task kihagyása
        skip_task(task)
```

---

## 📊 KONKRÉT REPÜLÉSI TERV STRUKTÚRA

### Terv Formátum (JSON)

```json
{
  "mission_day": 150,
  "date": "2025-06-15",
  "orbits": [
    {
      "orbit_number": 1,
      "start_time": "00:00:00 UTC",
      "end_time": "01:39:00 UTC",
      "tasks": [
        {
          "task_id": "IMG_001",
          "type": "imaging",
          "target": {
            "name": "Amazonas Rainforest",
            "coordinates": {"lat": -3.4653, "lon": -62.2159},
            "priority": "HIGH"
          },
          "window": {
            "start": "00:15:00",
            "end": "00:20:00",
            "duration_seconds": 300
          },
          "required_nodes": ["OLI2", "TIRS2", "ST_A", "ST_B"],
          "required_modules": ["payload", "navigation"],
          "power_consumption_w": 1200,
          "data_production_gb": 15.2
        },
        {
          "task_id": "ATT_001",
          "type": "attitude_maneuver",
          "purpose": "Point payload at target",
          "window": {
            "start": "00:30:00",
            "end": "00:31:00",
            "duration_seconds": 60
          },
          "required_nodes": ["ST_A", "ST_B", "OBC"],
          "required_modules": ["navigation"],
          "power_consumption_w": 800
        }
      ],
      "eclipse": {
        "entry": "01:00:00",
        "exit": "01:35:00",
        "duration_minutes": 35
      }
    }
  ],
  "downlink_windows": [
    {
      "window_id": "DL_001",
      "station": "Alaska (Fairbanks)",
      "window": {
        "start": "12:00:00",
        "end": "12:15:00",
        "duration_seconds": 900
      },
      "required_nodes": ["X_BAND", "OBC"],
      "data_rate_mbps": 800,
      "priority": "HIGH"
    }
  ]
}
```

---

## 🔄 BIO-KÓD VEZÉRLÉS FOLYAMATA

### 1. **Terv Betöltése** (Mission Day Start)

```
T = 00:00:00 (Mission Day Start)
├─ Load flight plan (JSON)
├─ Parse orbits, tasks, downlink windows
├─ Initialize bio-code engine
└─ Generate initial Level 3 bio-code (feasibility check)
```

### 2. **Task Végrehajtás Előtti Ellenőrzés** (100 ms előtte)

```
T = 00:14:59.900 (100 ms before imaging task)
├─ Generate Level 1 bio-codes (all nodes)
├─ Generate Level 2 bio-codes (all modules)
├─ Generate Level 3 bio-code (mission feasibility)
├─ Decode Level 3: feasibility = 95%, action = CONTINUE_NOMINAL
└─ DECISION: Execute task FULL (all nodes operational)
```

### 3. **Task Végrehajtás** (Bio-Kód Vezérlés)

```
T = 00:15:00.000 (Imaging task start)
├─ Execute task based on Level 3 bio-code decision
├─ Monitor node health during execution
├─ Generate bio-codes every 100 ms (continuous monitoring)
└─ Adapt if health degrades (bio-code driven)
```

### 4. **Adaptív Válasz** (Ha Hiba Történik)

```
T = 00:15:30.000 (Mid-task, node failure detected)
├─ Level 2 detects: TIRS2 health drops to 45%
├─ Level 1 reports: TIRS2 FAULT
├─ Level 2 recalculates: payload module health = 72%
├─ Level 3 recalculates: feasibility = 78%, action = CONTINUE_WITH_MONITORING
└─ ADAPT: Continue with OLI2 only (TIRS2 disabled)
```

---

## 🎯 IMPLEMENTÁCIÓS KÉRDÉSEK

### 1. **Terv Tárolás**
- **Hol?** JSON fájl, vagy backend memóriában?
- **Formátum?** Strukturált JSON, vagy egyszerűbb?

### 2. **Bio-Kód Integráció**
- **Mikor generálunk bio-code-ot?** Minden task előtt? Folyamatosan?
- **Hogyan tároljuk?** Minden task-hoz egy Level 3 bio-code?

### 3. **Adaptív Végrehajtás**
- **Hogyan adaptálunk?** Task kihagyása? Degradált mód? Fallback?
- **Mikor adaptálunk?** Real-time? Task előtt?

### 4. **Vizualizáció**
- **Hogyan jelenítjük meg?** Timeline? Orbit pozíciók? Task státuszok?
- **Bio-kód megjelenítés?** Minden task-hoz megjelenítjük a bio-code-ot?

---

## 💡 KÖVETKEZŐ LÉPÉSEK

1. **Terv Struktúra Döntés**
   - JSON formátum véglegesítése
   - Tárolási hely meghatározása

2. **Bio-Kód Integráció Tervezése**
   - Mikor generálunk bio-code-ot?
   - Hogyan tároljuk a bio-code-okat a tervben?

3. **Adaptív Végrehajtás Logika**
   - Task végrehajtási módok definiálása
   - Bio-code alapú döntési fa

4. **Vizualizáció Tervezése**
   - UI elemek
   - Timeline megjelenítés
   - Bio-code megjelenítés

---

**Megjegyzés:** Ez egy **tervezési dokumentum**. Az implementáció előtt dönteni kell a fenti kérdésekben.


