# Valós Szimuláció Adatfolyam - Újraértékelés

## Probléma

A jelenlegi implementációban:
- A bio-code generálás **nem** használja a valós Landsat9Model komponens health-jét
- Az EKF adatok **nem** a valós szenzorokból származnak
- A megjelenített adatok **nem** a valós fizikai szimulációból jönnek

## Mit kellene látni?

### 1. VALÓS ADATFORRÁSOK

#### Bio-code adatok:
- **Level 1**: Node health → **Landsat9Model komponensek health-jéből** (EPS, GNC, stb.)
- **Level 2**: Module health → **Landsat9Model alrendszerek aggregációjából** (payload, power, navigation, comm)
- **Level 3**: Mission feasibility → **Valós node/module health alapján számított**

#### EKF adatok:
- **Level 1**: Sensor measurements → **Landsat9Model szenzorokból** (GPS, Star Tracker, IMU)
- **Level 2**: Subsystem health → **Landsat9Model alrendszerekből** (navigation, power, payload, comm)
- **Level 3**: Mission feasibility → **Valós EKF confidence és szenzor adatok alapján**

### 2. ADATFOLYAM

```
Landsat9Model (fizikai szimuláció)
    ↓
    ├─→ Komponens health (EPS, GNC, stb.)
    │       ↓
    │   Bio-code Level 1 (node health → 64-bit)
    │       ↓
    │   Bio-code Level 2 (module aggregation → 32-bit)
    │       ↓
    │   Bio-code Level 3 (mission decision → 64-bit)
    │
    └─→ Szenzor adatok (GPS, Star Tracker, IMU)
            ↓
        EKF Level 1 (sensor measurements)
            ↓
        EKF Level 2 (subsystem health)
            ↓
        EKF Level 3 (mission feasibility)
```

### 3. MIT MÉRÜNK?

#### Bio-code:
- **Node health**: Landsat9Model komponensek valós health-je
  - EPS.battery.health
  - EPS.solar_wings[].health
  - GNC.star_trackers[].health
- **Module health**: Alrendszerek aggregált health-je
  - payload = OLI2 + TIRS2 health
  - power = EPS health
  - navigation = GNC health
  - comm = X_BAND + S_BAND health
- **Mission feasibility**: Weighted module health alapján

#### EKF:
- **Sensor measurements**: Landsat9Model szenzorok valós adatai
  - GPS: get_gps_measurement() → pozíció
  - Star Tracker: GNC.get_verified_orientation() → orientáció
  - IMU: (simulated, de valós fizika alapján)
- **Subsystem health**: Landsat9Model alrendszerek health-je
  - navigation = GNC health
  - power = EPS health
  - payload = (OLI2 + TIRS2) health
  - comm = (X_BAND + S_BAND) health
- **Mission feasibility**: EKF confidence alapján (valós szenzor adatokból számított)

### 4. HOGYAN KELLENE MŰKÖDNIE?

1. **Landsat9Model.simulate_step()** → Fizikai szimuláció
   - EPS frissítése (napelemek, akku)
   - GNC frissítése (star tracker, orientáció)
   - Komponens health változása (hiba esetén)

2. **Bio-code generálás** → Landsat9Model komponensekből
   - Node health = komponens health (EPS.battery.health, stb.)
   - Module health = alrendszerek aggregációja
   - Mission feasibility = weighted module health

3. **EKF generálás** → Landsat9Model szenzorokból
   - Sensor measurements = valós szenzor adatok
   - Subsystem health = alrendszerek health-je
   - Mission feasibility = EKF confidence (valós szenzor adatokból)

4. **Megjelenítés** → Valós adatokból
   - Comparison Panel: Valós feasibility, confidence, stb.
   - File Viewer: Valós bio-code és EKF adatok

### 5. JAVÍTÁSOK SZÜKSÉGESEK

1. **Bio-code generálás**:
   - `generate_complete_biocode_sequence()` → Landsat9Model komponensek health-jét használja
   - Node health = valós komponens health (nem random)

2. **EKF generálás**:
   - `_generate_level1_ekf()` → Landsat9Model szenzorok valós adatait használja
   - Sensor measurements = valós szenzor adatok (nem placeholder)

3. **Adatfolyam**:
   - `process_regeneration()` → Landsat9Model komponensek health-jét olvassa
   - `update()` → Landsat9Model szenzorok adatait olvassa

### 6. VÁRHATÓ ÉRTÉKEK

#### Normál működés (nincs hiba):
- **Bio-code Level 1**: Node health = 90-100% (valós komponens health)
- **Bio-code Level 3**: Feasibility = 95-100% (weighted module health)
- **EKF Level 1**: Sensor confidence = 90-100% (valós szenzor adatok)
- **EKF Level 3**: Feasibility = 90-100% (EKF confidence alapján)

#### Hiba esetén:
- **Bio-code**: Node health csökken → Feasibility csökken
- **EKF**: Sensor confidence csökken → Feasibility csökken
- **Különbség**: MetaSpace gyorsabban reagál (bio-code alapú) vs. EKF lassan reagál (szenzor átlagolás)


