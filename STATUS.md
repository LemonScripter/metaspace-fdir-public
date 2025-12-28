# 📊 MetaSpace Landsat-9 Simulation - Projekt Állapot

**Dátum:** 2025. január  
**Verzió:** v1.4  
**Státusz:** ✅ Stabil működés  
**GitHub Repository:** https://github.com/LemonScripter/metaspace-landsat9-simulation

---

## 🎯 Projekt Célja

A **MetaSpace Landsat-9 Szimuláció** egy összehasonlító elemzési eszköz, amely demonstrálja a hagyományos **EKF (Extended Kalman Filter)** és az innovatív **MetaSpace.bio** determinisztikus hibakezelési rendszerek közötti különbségeket valós műholdi környezetben.

### Főbb Különbségek

| Aspektus | EKF (Hagyományos) | MetaSpace.bio (Új) |
|----------|-------------------|---------------------|
| **Működési elv** | Valószínűségi, átlagolás | Determinisztikus, invariáns-alapú |
| **Reakcióidő** | 1-5 nap | <1 ms |
| **Döntéshozatal** | Heurisztikus, lassú | Azonnali, fizikai törvények alapján |
| **Adatvesztés** | Magas (rossz adat gyűjtése) | Zéró (hibás adat blokkolása) |
| **Emberi beavatkozás** | Szükséges | Nem szükséges |

---

## ✅ Implementált Funkciók

### 1. **Szimulációs Motor**
- ✅ **Landsat-9 digitális ikerpár** (fizikai modell)
- ✅ **4 hibatípus véletlenszerű injektálása:**
  - Solar Panel Failure (Napelem meghibásodás)
  - Battery Failure (Akkumulátor hiba)
  - GPS Antenna Failure (GPS antenna hiba)
  - IMU Drift (IMU sodródás)
- ✅ **EKF modell** (valószínűségi hibakezelés szimulációja)
- ✅ **MetaSpace modell** (determinisztikus hibakezelés)
- ✅ **Dinamikus detection latency számítás** (tudományos alapokon)

### 2. **Frontend Dashboard**
- ✅ **Chart.js grafikon** - EKF vs MetaSpace összehasonlítás
  - Idő tengely: napokban
  - EKF vonal: vörös-szürke szín (#ff6b6b)
  - MetaSpace vonal: kék, nem kitöltött
  - Tooltip: napokban, hiba jelzés
- ✅ **Component Health Matrix** - Komponens állapot megjelenítés
  - 2x3 grid layout
  - Teljes mező kitöltés
  - Komponens leírások
  - Nagyobb betűméretek
  - Egyforma magasságú téglalapok
- ✅ **Invariant Verification Stream** - MetaSpace log üzenetek
  - Görgethető lista
  - Időbélyeggel ellátott bejegyzések
  - MetaSpace észlelések és módváltások
- ✅ **Analysis Box** - Részletes értelmezés
  - EKF vs MetaSpace reakcióidők
  - Költséghatás számítás (USD)
  - Magyarázó szövegek
  - Nagyobb betűméretek
  - Nincs "Tactical" előtag

### 3. **Backend Funkciók**
- ✅ **Flask webszerver** (`app.py`)
- ✅ **Simulation Engine** (`backend/modules/simulator.py`)
  - Véletlenszerű hiba generálás
  - Telemetria adatok gyűjtése
  - Komponens állapot kinyerése
  - Bio logok generálása
- ✅ **EKF Model** (`backend/modules/ekf_model.py`)
  - GPS timeout kezelés (akku < 10%)
  - Dinamikus detection latency
  - Confidence számítás
  - Data loss tracking
- ✅ **MetaSpace Model** (`backend/modules/metaspace.py`)
  - 3 szintű bio-architektúra
  - Invariáns ellenőrzés
  - Azonnali hibafelismerés
  - Mission feasibility számítás
- ✅ **Landsat-9 Model** (`backend/modules/landsat9.py`)
  - Fizikai szimuláció
  - Alrendszerek (EPS, GNC)
  - Hiba injektálás

### 4. **Adatkezelés**
- ✅ **JSON log mentés** (`results/` könyvtár)
  - Minden szimuláció mentve
  - Telemetria adatok
  - Komponens állapotok
  - Bio logok
- ✅ **Log fájl limitálás** (max 30 fájl)
  - Automatikus törlés a legrégebbiek közül
- ✅ **Cost Estimation**
  - Scene érték számítás
  - Minőségveszteség figyelembevétele
  - USD formátum

### 5. **Dokumentáció**
- ✅ **About.html oldal** (`templates/about.html`)
  - MetaSpace.bio lényegének bemutatása
  - Logic-as-Hardware paradigma
  - Homeostasis elv
  - EKF vs MetaSpace összehasonlítás
  - "Miért nem működik a valószínűségi hibakezelés?" szekció
- ✅ **README.md** - Projekt áttekintés
- ✅ **Dokumentációs fájlok** (`docs/` könyvtár)

---

## 🏗️ Technikai Architektúra

### Könyvtárszerkezet

```
metaspace-landsat9-simulation/
├── app.py                          # Flask webszerver entry point
├── requirements.txt                # Python függőségek
├── README.md                       # Projekt dokumentáció
├── STATUS.md                       # Jelenlegi állapot (ez a fájl)
│
├── backend/
│   ├── modules/
│   │   ├── simulator.py           # Szimulációs motor
│   │   ├── landsat9.py            # Landsat-9 fizikai modell
│   │   ├── metaspace.py           # MetaSpace determinisztikus logika
│   │   ├── ekf_model.py           # EKF valószínűségi modell
│   │   ├── subsystems.py          # Alrendszerek (EPS, GNC)
│   │   ├── components.py          # Komponens modell
│   │   └── failure.py             # Hiba injektálás
│   │
│   └── tests/                     # Unit tesztek
│
├── templates/
│   ├── index.html                 # Főoldal (szimulátor)
│   └── about.html                 # Dokumentáció oldal
│
├── static/
│   ├── css/
│   │   └── style.css             # Stíluslap
│   └── js/
│       ├── main.js               # Fő JavaScript logika
│       └── interpretation.js     # Eredmény értelmezés
│
├── results/                       # Generált log fájlok (JSON)
│   └── sim_*.json                 # Szimulációs eredmények
│
└── docs/                          # Dokumentációs fájlok
    ├── MetaSpace_Simulation_Spec.md
    ├── MetaSpace_Master_Audit_EN.md
    └── ...
```

### Technológiai Stack

- **Backend:**
  - Python 3.10+
  - Flask (web framework)
  - NumPy (matematikai számítások)
  
- **Frontend:**
  - HTML5
  - CSS3 (custom dark theme)
  - JavaScript (ES6+)
  - Chart.js 4.4.0 (grafikonok)

- **Adatformátum:**
  - JSON (szimulációs eredmények)
  - REST API (Flask routes)

---

## 🔧 Főbb Implementációs Részletek

### EKF Modell Viselkedés

```python
# backend/modules/ekf_model.py

# GPS timeout kezelés (akku < 10%)
if gps is None:
    self.confidence -= 2.0  # Lassan csökken (1-2 nap)

# GPS hiba esetén
if self.model.gps_error > 50.0:
    error_factor = min(2.0, (self.model.gps_error - 50.0) / 25.0)
    self.confidence -= (1.5 + error_factor)  # Lassabban csökken

# Dinamikus detection latency
def _calculate_detection_latency(self):
    if gps is None:
        return random.randint(1440, 2880)  # 1-2 nap
    if self.model.gps_error > 80.0:
        return random.randint(720, 1440)   # 0.5-1 nap
    # ...
```

### MetaSpace Modell Viselkedés

```python
# backend/modules/metaspace.py

# Napelem hiba azonnali észlelése
if power_generation_w <= 1200.0:
    self.health['power'] = 0  # FAULT
    self.mission_feasibility = 0  # Azonnali leállítás

# Detection latency: 50ms (hardver szintű)
self.detection_latency = 50  # milliszekundum
```

### Szimulációs Motor

```python
# backend/modules/simulator.py

# Véletlenszerű hiba generálás
failure_day = random.randint(
    int(duration * 0.2),  # 20% a szimulációból
    int(duration * 0.8)    # 80% a szimulációból
)

# Telemetria adatok gyűjtése
telemetry_log.append({
    'time': current_time,
    'ekf_reliability': ekf.confidence,
    'metaspace_integrity': metaspace.mission_feasibility,
    'battery_percent': satellite.battery_level,
    'gps_error': satellite.gps_error,
    'power_generation_w': satellite.power_generation_w,
    # ...
})

# Log mentés
result_file = os.path.join(self.results_dir, f"sim_{sim_id}.json")
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump(result_package, f, indent=2, ensure_ascii=False)
```

---

## 📈 Jelenlegi Funkciók Részletesen

### 1. **Hibakezelési Forgatókönyvek**

#### Solar Panel Failure
- **EKF reakció:** GPS timeout után 1-2 nap alatt észleli (akku < 10%)
- **MetaSpace reakció:** Azonnali (power_generation_w < 1200W)
- **Költséghatás:** ~$315,000 (2 napos késleltetés, 60% minőségveszteség)

#### Battery Failure
- **EKF reakció:** Lassú feszültségzuhanás észlelése
- **MetaSpace reakció:** Azonnali leállítás, fogyasztók kikapcsolása

#### GPS Antenna Failure
- **EKF reakció:** 0.5-2 nap (heurisztikus korrekció)
- **MetaSpace reakció:** <100ms (invariáns sértés észlelése)

#### IMU Drift
- **EKF reakció:** 2-5 nap (fokozatos sodródás)
- **MetaSpace reakció:** Azonnali (temporal invariáns sértés)

### 2. **Frontend Komponensek**

#### Grafikon (Chart.js)
- X tengely: Idő (napokban)
- Y tengely: Megbízhatóság/Integritás (%)
- EKF dataset: vörös-szürke, 2px szélesség
- MetaSpace dataset: kék, vonal (nem kitöltött)
- Tooltip: napokban, hiba jelzés

#### Component Health Matrix
- Grid: 2 oszlop, 3 sor
- Komponensek:
  - Solar_Left_Wing, Solar_Right_Wing
  - Main_Battery_Pack
  - ST_A, ST_B, ST_C (Star Trackers)
- Minden kártya tartalmazza:
  - Komponens ID és név
  - Állapot (HEALTHY/FAULT)
  - Leíró szöveg

#### Analysis Box
- EKF reakcióidő (napokban)
- MetaSpace reakcióidő (milliszekundum)
- Költséghatás számítás (USD)
- Magyarázó szövegek minden hibatípusra

### 3. **API Endpoints**

```
GET  /                    # Főoldal
GET  /about               # Dokumentáció oldal
POST /api/simulation      # Szimuláció futtatása
```

#### `/api/simulation` Request:
```json
{
  "duration": 60,           // Szimuláció hossza (napokban)
  "scenario": "solar_panel" // Opcionális: specifikus hiba
}
```

#### Response:
```json
{
  "telemetry_log": [...],   // Időbeli adatok
  "components": [...],       // Komponens állapotok
  "bio_logs": [...],        // MetaSpace log üzenetek
  "narrative": "...",       // Szöveges összefoglaló
  "failure_info": {...}     // Hiba információk
}
```

---

## 🐛 Ismert Problémák / Korlátok

- ❌ Nincs automatikus teszt futtatás CI/CD-ben
- ⚠️ A szimuláció hosszú időt vehet igénybe nagy duration értékeknél (>100 nap)
- ⚠️ A log fájlok száma limitálva van 30-ra (régi fájlok automatikusan törlődnek)

---

## 🚀 Következő Lépések / TODO

### Rövid távú (1-2 hét)
- [ ] Unit tesztek bővítése
- [ ] Performance optimalizálás nagy duration értékeknél
- [ ] További hibatípusok hozzáadása

### Közép távú (1 hónap)
- [ ] Batch szimulációk futtatása
- [ ] Statisztikai elemzés dashboard
- [ ] Export funkció (CSV, PDF)

### Hosszú távú (3+ hónap)
- [ ] Valós műholdi adatok integrálása
- [ ] Machine learning predikciók
- [ ] Multi-satellite szimuláció

---

## 📝 Változásnapló (Changelog)

### v1.4 (Jelenlegi)
- ✅ About.html oldal bővítése MetaSpace.bio információkkal
- ✅ "Miért nem működik a valószínűségi hibakezelés?" szekció javítása
- ✅ Cím javítása: "Miért nem működik a valószínűségi hibakezelés?"
- ✅ Log fájlok limitálása 30-ra
- ✅ Cost estimation implementálása
- ✅ Component health matrix bővítése leírásokkal
- ✅ Invariant Verification Stream görgethetővé tétele

### v1.3
- ✅ Dinamikus EKF detection latency számítás
- ✅ MetaSpace azonnali napelem hiba észlelése
- ✅ Grafikon idő tengely napokban
- ✅ Analysis box bővítése

### v1.2
- ✅ EKF GPS timeout kezelés
- ✅ Random hiba generálás
- ✅ Bio logok generálása

### v1.1
- ✅ Alapvető szimuláció
- ✅ Frontend dashboard
- ✅ EKF vs MetaSpace összehasonlítás

---

## 🔗 Kapcsolódó Linkek

- **GitHub Repository:** https://github.com/LemonScripter/metaspace-landsat9-simulation
- **MetaSpace.bio:** https://metaspace.bio
- **LemonScript:** https://lemonscript.info
- **MetaSpace-Drone-Shield:** https://github.com/lemonscripter/MetaSpace-Drone-Shield

---

## 👥 Kapcsolat

**LemonScript Laboratory**  
Citrom Média LTD  
Email: hello@lemonscript.info

---

**© 2025 MetaSpace.bio - LemonScript | Citrom Média LTD**  
*Confidential & Proprietary Simulation Data.*


