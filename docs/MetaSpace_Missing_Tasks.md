# MetaSpace Szimuláció – Hátralévő Audit Feladatok és Hiányzó Bizonyítékok

**Dátum:** 2026-01-10  
**Verzió:** 1.0 (Draft)  
**Tárgy:** A _Verified_ Safety Case és Validation Report utáni fennmaradó audit hiányosságok és teendők

---

## 1. Áttekintés

A következő dokumentum összefoglalja azokat a **még hiányzó vagy nem elég transzparens elemeket**, amelyek szükségesek ahhoz, hogy a MetaSpace FDIR szimulációs rendszer **tudományosan vitathatatlanul megalapozott** és **auditálhatóan SIL 3 kompatibilis** legyen.

A két új dokumentum:
- `01_Safety_Case_Verified.html`
- `04_Validation_Report_Verified.html`

már **lezárták** az alábbi kritikus pontokat:
- ✅ PFD számítás (SIL 3 tartományban: PFD = 5.58e-04)
- ✅ MMS alapú numerikus verifikáció (RK4)
- ✅ Analitikus ground truth elleni validáció (Energy Balance modell, corr = 0.9930, MAE = 0.12%)
- ✅ GPS Spoofing TTD: 20 ms, 100% detection rate

Az alábbiakban azon **hiányzó / pontosítandó** tételek listája következik, amelyekre még **külön dokumentált bizonyíték** szükséges.

---

## 2. SIL 3 PFD SZÁMÍTÁS – TRANSZPARENS MUNKAFÜZET

### 2.1 Hiányzó elem

A Safety Case Verified dokumentum csak a **végső PFD értéket** közli:

- PFD_avg = 5.58e-04 (SIL 3 tartományban)

De nem mutatja:
- a részletes **képletet**,
- az összes **bemeneti paramétert** (hibaráták, CCF faktor, proof test logika),
- az **adatforrásokat** (katalógus, szabvány, mérés).

### 2.2 Mit kell csinálni

1. **Készíteni kell egy részletes PFD számítási munkafüzetet** (pl. `SIL3_PFD_Calculation.md` + Excel/CSV):
   - Tartalmazza a használt képletet, pl. 1oo2 architektúrára:
     ```
     PFD_avg = (λ_D × T_proof / 2) × (1 - DC) + β × λ_CCF × T_proof / 2
     ```
     ahol:
     - λ_D = veszélyes (dangerous) hibaráta [1/h vagy 1/év]
     - T_proof = proof test intervallum (3 év)
     - DC = diagnostic coverage (99.0%)
     - β = CCF (Common Cause Failure) faktor (pl. 0.05)
     - λ_CCF = közös okú hiba komponens

2. **Táblázatban fel kell sorolni az összes bemenetet**:
   ```md
   | Paraméter            | Jelölés | Érték        | Egység     | Forrás                       |
   |----------------------|--------|-------------|-----------|------------------------------|
   | Dangerous failure rate per channel | λ_D   | 1.0e-6      | 1/h       | MIL-HDBK-217F / gyártó     |
   | Proof test interval  | T_proof| 3           | év         | Karbantartási terv          |
   | Diagnostic coverage  | DC     | 0.99        | -          | Invariant observer analízis |
   | CCF beta factor      | β      | 0.05        | -          | SIL 3 best practice         |
   | CCF failure rate     | λ_CCF  | 5.0e-7      | 1/h        | Konzervatív feltevés        |
   ```

3. **Lépésről lépésre ki kell számítani a PFD-t**, és a végén megmutatni, hogyan adódik ki a 5.58e-04.

4. **Dokumentálni kell**, hogy a PFD a **SIL 3 tartományban helyezkedik el**:
   ```md
   SIL 3 tartomány: 1.0e-4 ≤ PFD_avg ≤ 1.0e-3
   Számított PFD_avg: 5.58e-4  →  megfelel SIL 3-nak.
   ```

---

## 3. ARCHITEKTÚRA – 1oo2 REDUNDANCIA RÉSZLETES LEÍRÁS

### 3.1 Hiányzó elem

A Safety Case Verified csak ennyit mond:
- „Architecture: 1oo2 (Redundant)”

De nem látszik:
- pontosan milyen **blokkokból** áll a rendszer,
- hogyan néz ki a **kettős csatorna** (két FDIR channel? két szenzor? két számítógép?),
- milyen **szavazási logika** (voting logic) van implementálva.

### 3.2 Mit kell csinálni

1. Készíteni kell egy **architektúra blokkdiagramot** (leírható markdownban is):
   ```md
   [Sensor A] ─┐
               ├─> [FDIR Channel 1] ──┐
   [Sensor B] ─┘                       │
                                       ├─> [1oo2 Decision Logic] ──> [Actuators]
   [FDIR Channel 2] <──────────────────┘
   ```

2. Szövegesen leírni:
   - Mely érzékelők redundánsak (GPS A/B, IMU A/B stb.).
   - Melyik FDIR algoritmus fut melyik csatornán.
   - Mi történik, ha az egyik csatorna hibás.

3. Pontosan definiálni a **1oo2 logikát**:
   - 1oo2 = 1 out of 2 → már az egyik channel hibajelzése is elég a beavatkozáshoz.
   - Meg kell írni:
     ```md
     A MetaSpace FDIR 1oo2 architektúrában működik, ahol bármelyik csatorna hibadetektálása elegendő a védelmi akció kiváltásához. A második csatorna redundáns, a PFD csökkentésére szolgál.
     ```

4. Készíteni egy táblázatot a **single point** és **dual point** failure eshetőségekről:
   ```md
   | Esemény                       | Leírás                                  | Következmény             |
   |-------------------------------|------------------------------------------|--------------------------|
   | Channel 1 FDIR failure        | Szoftver bug / HW hiba                  | Channel 2 átveszi        |
   | Channel 2 FDIR failure        | Szoftver bug / HW hiba                  | Channel 1 átveszi        |
   | CCF – common firmware bug     | Azonos szoftver mindkét csatornán       | CCF analízis szükséges   |
   | Sensor A+B common failure     | Azonos beszállító, azonos batch         | CCF a szenzor szinten    |
   ```

---

## 4. DIAGNOSTIC COVERAGE (DC = 99%) – METODOLÓGIA

### 4.1 Hiányzó elem

Most:
- A Safety Case Verified csak azt mondja: „Diagnostic Coverage (DC): 99.0% – Invariant Observers”

De **nem részletezi**, hogyan jött ki a 99%.

### 4.2 Mit kell csinálni

1. Létrehozni egy **„Diagnostic Coverage Analysis.md”** dokumentumot, amely:
   - Felsorolja az összes releváns hibamódot (FM-01, FM-02, FM-03 + továbbiak).
   - Megmutatja, hogy a MetaSpace FDIR ezeket milyen arányban detektálja.

2. DC definíciója:
   ```md
   DC = (Detectable dangerous faults aránya) / (Minden dangerous fault aránya)
   ```

3. Táblázat hibamódonként:
   ```md
   | Fault Mode | Leírás                    | Dangerous? | Detectálva? | Detektálási valószínűség |
   |-----------|---------------------------|-----------|------------|---------------------------|
   | FM-01     | GPS Spoofing              | Igen      | Igen       | 100%                      |
   | FM-02     | Solar Panel Failure       | Igen      | Igen       | 99.5%                    |
   | FM-03     | Battery Fault             | Igen      | Igen       | 99.2%                    |
   | ...       | ...                       | ...       | ...        | ...                       |
   ```

4. Végül kiszámítani a DC-t:
   ```md
   DC ≈ 0.99 = 99%
   ```

5. Rövid leírás arról, hogy a 99% **konzervatív**-e, és milyen biztonsági tartalékkal rendelkezik.

---

## 5. FDIR TELJESÍTMÉNY – TTI, FAR, MDR KIBONTÁSA

### 5.1 Mi van már meg

A Verified Validation Report már közli:
- GPS Spoofing: Mean TTD = 20.00 ms, Detection Rate = 100.0%

### 5.2 Még hiányzó metrikák

1. **TTI – Time To Isolation**
   - Mennyi idő alatt tudja az FDIR **nem csak detektálni**, hanem **izolálni** a hibát (pl. FM-01 vs FM-02)?

2. **FAR – False Alarm Rate**
   - Hányszor jelez hibát a rendszer **akkor is, amikor nincs hiba**?
   - Például: `FAR < 0.1 / óra`.

3. **MDR – Missed Detection Rate**
   - Hány % olyan hiba, amit a rendszer **nem vesz észre**.

### 5.3 Mit kell csinálni

1. Létrehozni egy `FDIR_Performance.md` dokumentumot, amely tartalmazza:

   ```md
   ## FDIR Teljesítmény Metrikák

   | Scenario         | Mean TTD | P95 TTD | TTI   | FAR (/h) | MDR (%) |
   |------------------|---------:|--------:|------:|---------:|--------:|
   | GPS Spoofing     | 20 ms    | 40 ms   | 50 ms | 0.01     | 0.0     |
   | Solar Panel Fault| 35 ms    | 60 ms   | 80 ms | 0.02     | 0.3     |
   | Battery Fault    | 30 ms    | 55 ms   | 70 ms | 0.02     | 0.2     |
   ```

2. Rövid magyarázatot adni a metrikákhoz:
   - **TTD:** mennyi idő a hibajel megjelenéséig.
   - **TTI:** mennyi idő, amíg tudható, melyik komponens a hibás.
   - **FAR:** téves riasztás gyakorisága.
   - **MDR:** nem detektált hibák aránya.

3. Leírni, milyen **tesztszcenáriók** alapján lettek ezek mérve:
   - Hány szimuláció futott (N=100, N=1000 stb.).
   - Milyen zaj- és paramétervariációval.

---

## 6. ROBUSZTUSSÁG ÉS SENSITIVITY ANALYSIS

### 6.1 Hiányzó elem

Bár a rendszer teljesítménye jó (20 ms TTD, 100% detection), **nem látszik**, hogyan viselkedik:
- paraméter-eltérés (
  ±10–20%),
- szenzor zaj növekedés,
- nem modellezett dinamika mellett.

### 6.2 Mit kell csinálni

1. Létrehozni egy `Robustness_And_Sensitivity.md` dokumentumot, amely:
   - Tartalmaz **paraméter sweep** vagy **Monte Carlo** eredményeket.

2. Példa táblázat:
   ```md
   ## Szenzor zaj hatása a TTD-re (GPS Spoofing)

   | Gyro zaj szint | Mean TTD | Detection Rate |
   |---------------:|---------:|---------------:|
   | 0.01 °/s       | 20 ms    | 100%           |
   | 0.05 °/s       | 22 ms    | 100%           |
   | 0.10 °/s       | 25 ms    | 99.8%          |
   ```

3. **Sensitivity** – pl. Sobol vagy Morris módszerrel:
   - Azonosítani, mely paraméterek a legkritikusabbak (Solar irradiance, Battery SOC, Gyro ARW stb.).

4. Rövid megállapítás:
   ```md
   A rendszer detektálási ideje (TTD) és detektálási aránya (Detection Rate) stabil marad a kritikus paraméterek ±20%-os változására, ami magas robusztussági szintet jelez.
   ```

---

## 7. Tesztspecifikációk – GPS SPOOFING / SOLAR / BATTERY

### 7.1 Hiányzó elem

A Verified report állítja, hogy:
- „High-fidelity (10ms step) injection tests were performed for GPS Spoofing scenarios.”

De:
- nincs részletezve a hiba **amplitúdója**, **időtartama**, **jelalakja**,
- nincs specifikálva a **zajszint**, **boundary condition**, **operációs pont**.

### 7.2 Mit kell csinálni

1. Létrehozni egy `Test_Specifications.md` dokumentumot, legalább az alábbi fejezetekkel:

   ```md
   # Test Specifications – MetaSpace FDIR

   ## TC-GPS-01 – GPS Spoofing
   - Time step: 10 ms
   - Simulation duration: 120 s
   - Fault injection start: t = 50 s
   - Spoofing profile: step change in position (Δpos = 2 km), velocity bias (Δv = 20 m/s)
   - Sensor noise: σ_pos = 10 m, σ_vel = 0.1 m/s
   - Acceptance criteria: Mean TTD < 50 ms, Detection Rate > 99.5%

   ## TC-SOLAR-01 – Solar Panel Fault
   - Fault: sudden loss of 50% panel output at t = 30 s
   - Irradiance model: standard AM0, no eclipse
   - Acceptance: Fault detected in < 100 ms, SOC model stable

   ## TC-BATT-01 – Battery Fault
   - Fault: internal resistance jump +50%
   - Initial SOC: 40%
   - Thermal condition: -10 °C
   - Acceptance: Fault detected in < 150 ms, no unsafe undervoltage
   ```

2. Ezeket a specifikációkat hivatkozni a Validation Report Verified dokumentumban.

---

## 8. ÖSSZEFOGLALÓ – MELY LÉPÉSEK MARADTAK

### 8.1 Rövid lista

A Verified dokumentumok után **nagyon jó helyen van a rendszer**, de az alábbi **5 fő dokumentum** még szükséges a teljes, vitathatatlan audit csomaghoz:

1. `SIL3_PFD_Calculation.md`
   - Részletes PFD képlet, paraméterek, források, számítási lépések.

2. `Architecture_1oo2.md`
   - Blokkdiagram + 1oo2 logika szöveges leírása + failure eshetőségek.

3. `Diagnostic_Coverage_Analysis.md`
   - Hibamód listák, detektálási valószínűségek, DC = 99% számítás.

4. `FDIR_Performance.md`
   - TTD + TTI + FAR + MDR összesítve több szcenárióra.

5. `Test_Specifications.md` + `Robustness_And_Sensitivity.md`
   - Tesztesetek részletezése + robusztussági eredmények.

Ha ez az 5 dokumentum elkészül, akkor a MetaSpace FDIR szimuláció **nem csak erős mérnöki alapokon áll**, hanem egy **külső auditor / szabályozó hatóság felé is átlátható, reprodukálható és matematikailag/trendileg megalapozott** lesz.

---

**Dokumentum vége – v1.0**
