# MetaSpace Satellite Simulation - Projekt Állapot

**Utolsó frissítés:** 2026. január 8.

## 🚀 Jelentős Fejlesztések (2026.01.08)

### 1. Valós 3D Kálmán-szűrő (EKF)
Az EKF szimulátor (`backend/modules/ekf_model.py`) teljes matematikai átalakításon esett át. A korábbi heurisztikus ("dummy") logikát egy **valós 6-DOF (Degrees of Freedom) Kálmán-szűrő** váltotta fel:
- **Matematikai Modell:** `KalmanFilter3D` osztály NumPy alapon.
- **Állapotvektor:** Pozíció (X, Y, Z) és Sebesség (VX, VY, VZ).
- **Confidence Számítás:** A kovariancia mátrix (P) nyomából (Trace) számolva.
- **Eredmény:** A rendszer mostantól matematikailag bizonyítja az EKF "vakságát" az akkumulátor állapotára (a Confidence nem csökken, amíg van adat, még ha az akku kritikus is).

### 2. Szakmai Nyelvezet (Localization)
A validációs motor (`v3_validation_engine.py`) és a bio-kód motor (`v3_biocode_engine.py`) kimenetei frissültek a precíz mérnöki terminológia használatára:
- "Értéktartományon kívül" a "NEM ... kozott" helyett.
- "Elvárt: legfeljebb 1" a "kell: max 1" helyett.
- "Regeneráció inaktív, ellenőrzés nem releváns (N/A)".

### 3. Biztonsági Audit (Passed)
A rendszer IP védelme sikeresen auditálva:
- **Git Védelem:** `.gitignore` helyesen kizárja a `*.key` és `secrets/` fájlokat.
- **SecureBridge:** A titkosított modulok betöltése kizárólag a memóriában történik (`exec()`), soha nem íródnak ki a lemezre dekódolt formában.

### 4. Dokumentáció
- Létrehozva a `GEMINI.md` fájl, amely kontextust biztosít az AI asszisztensek számára.

---

## Áttekintés

A projekt egy determinisztikus FDIR (Fault Detection, Isolation, and Recovery) rendszert szimulál, amely az Extended Kalman Filter (EKF) rendszerekkel való összehasonlítást mutatja be. A rendszer három fő komponensből áll:
1. **V2 Main Simulation** (`/`): EKF vs MetaSpace összehasonlítás, hiba injektálás, költségbecslés
2. **V3 Neural Sandbox** (`/v3-sandbox`): Holografikus hálózati motor bio-kód vezérléssel, 100% matematikai validációval
3. **Navigation Plan Simulation** (`/navigation-plan`): Navigációs terv végrehajtás szimulációja, split-screen UI-val, orbit pozíciók és task timeline

## V2 Main Simulation - Állapot

### Implementált Funkciók

#### 1. EKF vs MetaSpace Összehasonlítás
- **EKF Simulator**: **FRISSÍTVE:** Valós 3D Kalman Filter implementáció (NumPy).
- **MetaSpace Simulator**: Determinisztikus FDIR rendszer
- **Összehasonlítási metrikák**: Feasibility, Confidence, Detection Latency, Decision Quality, Data Loss

#### 2. Hiba Injektálás (Failure Injection)
- **Solar Panel Structural Failure**: Napelem struktúrális hiba
- **GPS Spoofing / Signal Loss**: GPS spoofing vagy jelvesztés
- **Battery Thermal Runaway**: Akkumulátor termikus futás
- **IMU Gyro Bias Drift**: IMU drift (gyroscope bias)
- **Nominal Flight**: Kontroll szimuláció (hiba nélkül)

#### 3. Landsat-9 Fizikai Modell
- **8 Komponens**: OLI2, TIRS2, OBC, StarTracker, IMU, GPS_Antenna, EPS, Comm
- **Valódi adatok**: Landsat-9 specifikációk alapján
- **Komponens health tracking**: Valós idejű állapot követés
- **GPS error tracking**: GPS hiba számítás és követés

#### 4. MetaSpace FDIR Logika
- **Level 1 Assessment**: Szenzor szintű egészség ellenőrzés
- **Level 2 Assessment**: Modul szintű aggregáció
- **Level 0 Arbiter**: Küldetés megvalósíthatóság számítás
- **GPS Spoofing Detection**: GPS hiba > 50% → GPS FAULT
- **IMU Drift Handling**: IMU drift nem kapcsolja ki a GPS antennát (csak a navigációs rendszer megbízhatatlan)

#### 5. UI Komponensek
- **Mission Feasibility Chart**: EKF vs MetaSpace összehasonlítás grafikon
- **Component Health Matrix**: Komponens állapot mátrix
- **Analysis Panel**: Szimuláció narratíva
- **Invariant Verification Stream**: Bio-kód validációs stream
- **Grid Layout**: 2 oszlop első sorban, 1 oszlop a többi sorban

### Javított Bugok

1. **GPS Spoofing Detection**: MetaSpace most helyesen detektálja a GPS spoofing-ot és leállítja a szenzorokat
2. **IMU Drift vs GPS**: IMU drift nem kapcsolja ki a GPS antennát, csak a navigációs rendszer megbízhatatlan lesz
3. **Grid Layout**: Javított grid elrendezés (2 oszlop első sor, 1 oszlop többi sor)
4. **Component Matrix**: GPS_Antenna hozzáadva a komponens mátrixhoz
5. **Graph X-axis**: Napok egész számként jelennek meg (tizedesek eltávolítva)

## V3 Neural Sandbox - Állapot

### Implementált Funkciók

#### 1. Bio-Kód Rendszer (3-Level Pipeline)
- **Level 1**: Node health → 64-bit bio-code (szenzor adatok)
- **Level 2**: Module aggregation → 32-bit bio-code (modul szintű aggregáció)
- **Level 3**: Mission decision → 64-bit bio-code (küldetés döntés, weighted feasibility)

**Főbb jellemzők:**
- Bio-kód **vezérli** a műhold működését (nem csak validálja)
- Level 3 bio-kód a Level 2 bio-kódokból generálódik (bio-kód vezérelt kontroll)
- Weighted feasibility számítás: logic 30%, navigation 25%, power 25%, comm 20%
- Action meghatározás feasibility és power status alapján
- Safety margin számítás a regeneráció sebességének módosításához

#### 2. Landsat-9 Integráció
- **8 Node**: OLI2, TIRS2, OBC, StarTracker, IMU, GPS_Antenna, EPS, Comm
- **Valódi adatok**: Landsat-9 specifikációk alapján
- **Node health szinkronizáció**: HolographicNode health szinkronizálva Landsat9Model komponens health-jével
- **Időbeli degradáció**: 0.02% degradáció per nap (realisztikus wear and tear)

#### 3. Validációs Rendszer (100% Matematikai Bizonyítás)

**Invariánsok:**
- `health_bounds`: ∀n: 0 ≤ n.health ≤ 100
- `master_uniqueness`: |{n: n.is_master}| ≤ 1
- `power_dependency`: regen_active → ∃n: 'power' ∈ n.capabilities
- `feasibility_bounds`: 0 ≤ feasibility ≤ 100
- `regen_monotonicity`: regen → health_new ≥ health_old (regeneráció előtti health értékekkel összehasonlítva)
- `biocode_consistency`: decode(encode(state)) == state
- `biocode_encrypted_validation`: Bio-kód validáció titkosított fájlokkal (SecureBridge)

**Matematikai Validáció:**
- Feasibility formula ellenőrzése
- Bio-code encoding/decoding konzisztencia (1% tolerancia)
- Minden művelet validálva (chaos injection, regeneration)
- Titkosított validátorok betöltése (VHDL_Synth, Logic_Lock)

**Validációs Jelentés:**
- SHA-256 alapú validation ID (unforgeable)
- Operations log minden műveletről
- Detailed error information FAILED műveletekhez
- Összesített success rate és overall status
- Overall status explanation (100% validáció követelmény)
- Automatikus fájl mentés (csak aktív szimuláció során, vagy szimuláció végén)
- Automatikus cleanup (csak az utolsó 2 jelentés marad meg)

#### 4. Determinisztikus Öngyógyítás

**Bio-Kód Vezérlés:**
- Regeneráció csak akkor történik, ha:
  - Van power capability
  - Action nem EMERGENCY_HALT vagy SAFE_MODE
  - Feasibility > 20%
- Regeneráció sebessége a safety margin alapján módosul
- Master migration GIP alapú logikával

**Szimuláció Befejezése:**
- Ha nincs power capability ÉS vannak sérült node-ok → szimuláció befejeződik (végtelen ciklus elkerülése)
- Ha minden node 100% health ÉS feasibility >= 100% → szimuláció befejeződik
- `simulation_active` flag vezérli a jelentés generálást

#### 5. Frontend Funkciók

**UI Komponensek:**
- D3.js alapú hálózati visualizáció
- Node kattintás → egy node kikapcsolása (bug fix: csak a kattintott node)
- Bio-kód status megjelenítés (Level 3, Action, Feasibility, Safety Margin)
- Validációs jelentés panel (Overall Status, Invariants, Mathematics, FAILED műveletek részletei)
- Download Validation Report gomb (JSON formátumban)

**Hard Refresh Kezelés:**
- Automatikus backend reset oldal betöltéskor (`/api/v3/reset`)
- Backend állapot lekérése inicializáláskor (`/api/v3/state`)
- Biztosítja, hogy tiszta állapotból induljon minden szimuláció

**Regeneráció Loop:**
- Automatikus indítás chaos injection után
- 3 másodperces intervallum
- Automatikus leállítás szimuláció befejezéskor
- `simulationActive` flag vezérli a loop-ot

### Javított Bugok

1. **regen_monotonicity fix**: A health history tracking most a regeneráció **előtti** health értékeket használja, nem a health history-t (ami régi értékeket tartalmazhatott)
2. **Végtelen ciklus megoldás**: Ha nincs power capability, a szimuláció befejeződik, nem ragad végtelen ciklusba
3. **Node click bug**: Csak a kattintott node kapcsolódik ki, nem minden node egyszerre (event propagation stop + pontos targetId használata)
4. **Hard refresh reset**: Backend állapot automatikus reset-elése oldal betöltéskor, hogy ne legyen állapot inkonzisztencia
5. **Error details tárolása**: FAILED műveletek részletes hiba információi most tárolódnak és megjelennek a UI-ban
6. **Validation report generálás**: Csak aktív szimuláció során generálódnak jelentések, nem folyamatosan
7. **Landsat9Model integráció**: Node health szinkronizálva a fizikai modell komponens health-jével
8. **Időbeli degradáció**: Realisztikus wear and tear szimuláció (0.02% per nap)

## Navigation Plan Simulation - Állapot

### Implementált Funkciók

#### 1. Navigációs Terv Rendszer
- **NavigationPlan osztály**: Navigációs terv kezelés, orbit pozíciók, task-ok
- **JSON alapú terv betöltés**: Terv betöltése JSON fájlból
- **Orbit számítás**: Jelenlegi orbit számítása, következő task-ok lekérése

#### 2. Bio-Code Fájlkezelés
- **3-Level Bio-Code Fájlok**: `level1.bio`, `level2.bio`, `level3.bio`
- **Bináris szerializáció**: Magic number, metadata, timestamp
- **Fájl mentés/betöltés**: `BioCodeFileManager` osztály
- **Validáció integráció**: Bio-kód fájlok mentésekor automatikus validáció

#### 3. EKF Fájlkezelés
- **3-Level EKF Fájlok**: `level1.ekf`, `level2.ekf`, `level3.ekf`
- **Bináris szerializáció**: Magic number, metadata, timestamp
- **Fájl mentés/betöltés**: `EKFFileManager` osztály
- **JSON serializáció**: NumPy array-k konvertálva Python listákká

#### 4. Moduláris UI Architektúra
- **Core Modulok**:
  - `EventBus.js`: Pub/sub eseménykezelés
  - `StateManager.js`: Globális állapotkezelés
  - `APIClient.js`: API kommunikáció (retry logika, timeout kezelés)
  - `ComponentBase.js`: Alap komponens osztály (lifecycle management)
- **Services**:
  - `NavigationService.js`: Navigációs terv API hívások
  - `BioCodeService.js`: Bio-kód fájl API hívások
  - `EKFService.js`: EKF fájl API hívások
  - `ComparisonService.js`: Összehasonlítás metrikák API hívások
- **Components**:
  - `ComparisonPanel.js`: EKF vs MetaSpace összehasonlítás panel
  - `FileViewer.js`: 3-level bio-code/EKF fájl megjelenítő (tab navigáció)

#### 5. Split-Screen UI
- **Bal oldal**:
  - Orbit Visualization: D3.js alapú pálya vizualizáció, műhold animáció
  - Task Timeline: D3.js alapú task idővonal
  - Orbit Parameters: Pálya paraméterek (altitude, period, inclination, current_orbit)
- **Jobb oldal**:
  - Comparison Panel: EKF vs MetaSpace összehasonlítás
  - Bio-Code Files: 3-level bio-code fájl megjelenítő
  - EKF Files: 3-level EKF fájl megjelenítő
  - Control Buttons: Start, Stop, Reset

#### 6. Szimuláció Futtatás
- **Mission Day Tracking**: Napok számlálása (10 másodpercenként 1 nap)
- **Fájl generálás**: Bio-code és EKF fájlok generálása minden nap
- **Valós idejű frissítés**: 2 másodpercenként adatok frissítése
- **Placeholder adatok**: API hiba esetén placeholder adatok megjelenítése

### Javított Bugok

1. **EKF File Loading**: `struct.unpack` byte számok javítva (30 bytes Level 1, 25 bytes Level 3)
2. **JSON Serialization**: NumPy array-k konvertálva Python listákká
3. **FileViewer Tabs**: Event delegation használata dinamikusan renderelt gombokhoz
4. **ComparisonPanel Update**: DOM renderelés után frissítés (setTimeout)
5. **Orbit Parameters**: Statikus paraméterek, de `current_orbit` változik
6. **Mission Day Increment**: Automatikus növelés szimuláció futása közben

## Header Menü - Állapot

### Implementált Funkciók

- **Brand**: METASPACE .BIO V2.0 (bal oldal)
- **Menü Linkek** (jobb oldal, egy sorban):
  - **NEURAL SANDBOX**: V3 Neural Sandbox link (sárga szín)
  - **NAVIGATION PLAN**: Navigation Plan szimuláció link (cyan szín)
  - **ABOUT**: Dokumentáció link
- **Layout**: Flexbox, `justify-content: space-between`, `flex-wrap: nowrap`
- **Menügombok**: Növelt padding (`8px 20px`), `min-width: fit-content`

### Javított Bugok

1. **Menünevek kilógása**: Növelt padding és `min-width: fit-content` hozzáadása
2. **Egy sorban**: `flex-wrap: nowrap` és `white-space: nowrap` biztosítása
3. **Min-width visszaállítás**: 1280px (nem 1600px)

## Szimuláció Izoláció

### 3 Különálló Szimuláció

1. **index.html** (`/`):
   - V2 Main Simulation
   - EKF vs MetaSpace összehasonlítás
   - Véletlenszerű hiba injektálás
   - Global változók: `_global_simulator`, `_global_landsat_model`

2. **v3_fractal_sim.html** (`/v3-sandbox`):
   - V3 Neural Sandbox
   - Bio-kód vezérlés
   - Chaos injection és regeneráció
   - Global változók: `_global_v3_network` (opcionális `landsat_model`)

3. **navigation-plan.html** (`/navigation-plan`):
   - Navigation Plan Simulation
   - Bio-code és EKF fájl generálás
   - Split-screen UI
   - Global változók: `_navigation_plan_ekf_simulator`, `_navigation_plan_v3_network`, `_navigation_plan_landsat_model`

### Backward Compatibility

- **v3_neural_core.py**: `landsat_model` opcionális paraméter (default: `None`)
- **ekf_model.py**: Időbeli degradáció csak `navigation-plan` szimulációhoz
- **Global változók**: Prefixed nevek (`_navigation_plan_*`) az izoláció biztosításához

## API Endpoint-ok

### V2 Main Simulation:
- `POST /api/simulation/run`: Szimuláció futtatása
- `GET /api/simulation/status`: Szimuláció állapot lekérése

### V3 Neural Sandbox:
- `POST /api/v3/chaos`: Káosz injektálás (node-ok kikapcsolása)
- `POST /api/v3/regen`: Regenerációs ciklus futtatása
- `POST /api/v3/config`: Konfiguráció módosítása (regen_rate)
- `GET /api/v3/validation/report/latest`: Legutóbbi validációs jelentés
- `POST /api/v3/reset`: Backend állapot reset-elése (hard refresh után)
- `GET /api/v3/state`: Backend állapot lekérése (inicializáláskor)

### Navigation Plan:
- `GET /api/navigation/plan/<plan_id>`: Navigációs terv lekérése
- `GET /api/navigation/current-orbit`: Jelenlegi orbit számítása
- `GET /api/navigation/upcoming-tasks`: Következő task-ok lekérése
- `GET /api/navigation/orbit-parameters`: Pálya paraméterek lekérése
- `GET /api/biocode/files/latest`: Legutóbbi bio-code fájlok
- `GET /api/biocode/files/load`: Bio-code fájl betöltése
- `GET /api/ekf/files/latest`: Legutóbbi EKF fájlok
- `GET /api/ekf/files/load`: EKF fájl betöltése
- `GET /api/comparison/metrics`: Összehasonlítás metrikák
- `POST /api/simulation/generate-files`: Bio-code és EKF fájlok generálása

## Fájlstruktúra

### Backend Modulok:
- `backend/modules/v3_neural_core.py`: Fő hálózati motor, regeneráció, chaos injection
- `backend/modules/v3_biocode_engine.py`: 3-level bio-code generálás és dekódolás
- `backend/modules/v3_validation_engine.py`: Invariánsok és matematikai validáció
- `backend/modules/v3_validation_report.py`: Validációs jelentés generálás és tárolás
- `backend/modules/biocode_file_manager.py`: Bio-code fájl mentés/betöltés
- `backend/modules/ekf_file_manager.py`: EKF fájl mentés/betöltés
- `backend/modules/navigation_plan.py`: Navigációs terv kezelés
- `backend/modules/landsat9.py`: Landsat-9 fizikai modell
- `backend/modules/metaspace.py`: MetaSpace FDIR logika
- `backend/modules/ekf_model.py`: EKF szimulátor
- `backend/modules/simulator.py`: Unified simulator engine
- `backend/modules/secure_bridge.py`: Titkosított modulok betöltése

### Frontend:
- `templates/index.html`: V2 Main Simulation UI
- `templates/v3_fractal_sim.html`: V3 Neural Sandbox UI
- `templates/navigation-plan.html`: Navigation Plan Simulation UI
- `static/js/main.js`: Main simulation frontend logika
- `static/js/pages/navigation-plan-page.js`: Navigation Plan page orchestrator
- `static/js/core/EventBus.js`: Event bus modul
- `static/js/core/StateManager.js`: State manager modul
- `static/js/core/APIClient.js`: API client modul
- `static/js/core/ComponentBase.js`: Component base osztály
- `static/js/services/NavigationService.js`: Navigation service
- `static/js/services/BioCodeService.js`: Bio-code service
- `static/js/services/EKFService.js`: EKF service
- `static/js/services/ComparisonService.js`: Comparison service
- `static/js/components/ComparisonPanel/ComparisonPanel.js`: Comparison panel komponens
- `static/js/components/FileViewer/FileViewer.js`: File viewer komponens
- `static/css/style.css`: Stílusok

### Dokumentáció:
- `docs/MetaSpace_Simulation_Spec.md`: Szimuláció specifikáció
- `docs/UI_MODULAR_ARCHITECTURE.md`: Moduláris UI architektúra
- `docs/MIGRATION_STRATEGY.md`: Migrációs stratégia (Strangler Pattern)
- `docs/NAVIGATION_PLAN_UI_SPEC.md`: Navigation Plan UI specifikáció
- `docs/REAL_SIMULATION_DATA_FLOW.md`: Valós szimulációs adatfolyam
- `docs/FAILURE_INJECTION_ANALYSIS.md`: Hiba injektálás elemzés
- `docs/EKF_BETTER_THAN_METASPACE_ANALYSIS.md`: EKF vs MetaSpace elemzés
- `docs/EKF_CONFIDENCE_RESET_ANALYSIS.md`: EKF confidence reset elemzés
- `docs/BACKWARD_COMPATIBILITY.md`: Backward compatibility dokumentáció
- `docs/SIMULATION_ISOLATION.md`: Szimuláció izoláció dokumentáció
- `docs/Landsat9_BioCode_Data_Sources.md`: Landsat-9 bio-code adatforrások

## Ismert Korlátok / Megjegyzések

1. **Bio-code encoding/decoding tolerancia**: 1% tolerancia a feasibility értékeknél (integer tárolás miatt)
2. **Validation report cleanup**: Csak az utolsó 2 jelentés marad meg (automatikus törlés)
3. **Simulation active flag**: A szimuláció befejezésekor (`simulation_active = False`) nem generálódnak új jelentések
4. **Power dependency**: Ha nincs power capability, a szimuláció befejeződik (fizikai korlát)
5. **Orbit Parameters**: Alapvető pálya paraméterek (altitude, period, inclination) statikusak, csak `current_orbit` változik
6. **EKF Confidence**: Időbeli degradáció csak `navigation-plan` szimulációhoz, nem `index.html`-hez
7. **IMU Drift**: IMU drift nem kapcsolja ki a GPS antennát, csak a navigációs rendszer megbízhatatlan lesz

## Következő Lépések (Opciók)

1. További invariánsok hozzáadása
2. Performance optimalizálás (nagy számú node esetén)
3. További teszt esetek
4. Dokumentáció bővítése
5. Navigation Plan UI további fejlesztése (több interaktivitás)
6. Real-time orbit tracking fejlesztése

---

**Megjegyzés**: Ez a dokumentum a projekt aktuális állapotát dokumentálja. A GitHub-ra való feltöltés nem szükséges, csak helyi dokumentáció.