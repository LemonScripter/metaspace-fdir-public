# Navigation Plan UI - Mit kellene látni?

## Áttekintés

Ez a dokumentum leírja, hogy **mit kellene látni** a Navigation Plan oldal különböző ablakokban, **mit mérünk**, és **hogyan kellene változniuk** az adatoknak a szimuláció során.

---

## 1. ORBIT PARAMETERS (Bal oldal, felső panel)

### Mit mutat:
- **Altitude**: 705 km (statikus - Landsat-9 pálya magassága)
- **Period**: 99 min (statikus - keringési idő)
- **Inclination**: 98.2° (statikus - pályahajlás)
- **Current Orbit**: 1, 2, 3... (dinamikus - növekszik, ahogy a műhold kering)

### Változik-e?
- **Altitude, Period, Inclination**: **NEM** - ezek fizikai paraméterek, nem változnak
- **Current Orbit**: **IGEN** - növekszik, ahogy a műhold kering (minden 99 percben +1)

### Mit mérünk?
- Fizikai pálya paramétereket (statikus)
- Jelenlegi orbit számot (dinamikus)

---

## 2. TASK TIMELINE (Bal oldal, középső panel)

### Mit mutat:
- **Timeline track**: Vízszintes vonal, amely az orbit időtartamát mutatja
- **Task markers**: Körök a timeline-on, amelyek a task-okat jelölik
  - Kék: Imaging task (fényképezés)
  - Narancs: Attitude maneuver (pozícióváltás)
  - Zöld: Downlink window (adatok letöltése)

### Változik-e?
- **IGEN** - Ahogy a szimuláció halad, a task-ok eltűnnek (már megtörténtek) és új task-ok jelennek meg

### Mit mérünk?
- Task-ok időzítését (mikor kell végrehajtani)
- Task-ok státuszát (upcoming, active, completed)
- Task-ok prioritását és típusát

---

## 3. ORBIT VISUALIZATION (Bal oldal, alsó panel)

### Mit mutat:
- **Orbit path**: Elliptikus pálya (D3.js animáció)
- **Satellite position**: Műhold pozíciója a pályán (animált kör)
- **Earth**: Föld középpont (opcionális)

### Változik-e?
- **IGEN** - A műhold folyamatosan mozog a pályán (animáció)
- A pozíció változik, ahogy a műhold kering

### Mit mérünk?
- Műhold pozícióját a pályán
- Orbit fázisát (napos/árnyékos rész)
- Animáció sebességét (valós idő vs. gyorsított)

---

## 4. EKF vs METASPACE COMPARISON (Jobb oldal, felső panel)

### Mit mutat:

#### EKF oszlop:
- **Feasibility**: 0-100% (EKF confidence alapú)
- **Decision**: CONTINUE_NOMINAL, CONTINUE_WITH_MONITORING, STOP_IMAGING, SAFE_MODE
- **Confidence**: 0-100% (GPS/IMU confidence)
- **Anomaly**: DETECTED / NONE
- **Scenes Today**: 0-700 (napi fényképek száma)
- **Data Loss**: 0-700 (elveszett/rossz minőségű fényképek)

#### MetaSpace oszlop:
- **Feasibility**: 0-100% (bio-code alapú, weighted)
- **Decision**: CONTINUE_NOMINAL, CONTINUE_WITH_MONITORING, GRACEFUL_DEGRADATION, SAFE_MODE
- **Safety Margin**: 0-100% (feasibility - critical threshold)
- **Bio-code L3**: 64-bit hex kód (pl. 0x8F2C_A4E7_B1D9_5C6A)

#### Difference:
- MetaSpace feasibility - EKF feasibility (pl. +16.8%)

### Változik-e?
- **IGEN** - Ez a legfontosabb panel! Itt kell látni a különbséget:
  - **Detection Latency**: EKF: 5-30 másodperc, MetaSpace: <100 ms
  - **Decision Quality**: MetaSpace gyorsabban és pontosabban dönt
  - **Data Loss**: EKF: 20-40% (hiba esetén), MetaSpace: 0% (legtöbb esetben)
  - **Scenes Today**: EKF: változó (hiba esetén rossz adat), MetaSpace: stabil

### Mit mérünk?
- **Detection Latency**: Mennyi idő alatt észleli a hibát
- **Decision Quality**: Mennyire jó a döntés (feasibility alapján)
- **Data Loss**: Mennyi adat veszik el (rossz minőségű fényképek)
- **Mission Success Rate**: Hány %-ban sikerül a küldetés

### Várható értékek (dokumentáció alapján):
- **EKF Detection Latency**: 5-30 másodperc
- **MetaSpace Detection Latency**: <100 milliszekundum
- **EKF Data Loss**: 20-40% (hiba esetén)
- **MetaSpace Data Loss**: 0% (legtöbb esetben)
- **EKF Mission Success**: 70-85%
- **MetaSpace Mission Success**: 95-99%

---

## 5. BIO-CODE FILES (Jobb oldal, középső panel)

### Mit mutat:

#### Level 1 (Node-level):
- **8 node**: OLI2, TIRS2, ST_A, ST_B, EPS, OBC, X_BAND, S_BAND
- **64-bit bio-code** minden node-hoz (pl. 0x0001_8F2C_A4E7_B1D9)
- **Node health**: 0-100% (implicit a bio-code-ban)

#### Level 2 (Module-level):
- **4 module**: payload, power, navigation, comm
- **32-bit bio-code** minden module-hoz (pl. 0xA7_F4_B2_E8)
- **Module aggregation**: Node-ok aggregációja

#### Level 3 (Mission-level):
- **Mission Day**: 0, 1, 2, 3... (növekszik)
- **64-bit bio-code**: Mission decision kód (pl. 0x8F2C_A4E7_B1D9_5C6A)
- **Feasibility**: 0-100% (weighted, bio-code alapú)
- **Action**: CONTINUE_NOMINAL, CONTINUE_WITH_MONITORING, stb.
- **Safety Margin**: 0-100% (feasibility - critical threshold)

### Változik-e?
- **IGEN** - Ahogy a szimuláció halad:
  - **Level 1**: Node health változik (hiba esetén csökken)
  - **Level 2**: Module health változik (aggregált node health)
  - **Level 3**: Feasibility változik (mission day növekedésével, hibák esetén)
  - **Bio-codes**: Minden frissítésnél új bio-code generálódik

### Mit mérünk?
- **Node health**: Minden komponens (OLI2, TIRS2, stb.) egészségi állapota
- **Module health**: Alrendszerek (payload, power, navigation, comm) egészségi állapota
- **Mission feasibility**: Küldetés megvalósíthatósága (0-100%)
- **Safety margin**: Biztonsági tartalék (feasibility - critical threshold)

---

## 6. EKF FILES (Jobb oldal, alsó panel)

### Mit mutat:

#### Level 1 (Sensor-level):
- **4 sensor**: GPS, IMU, STAR_TRACKER_A, STAR_TRACKER_B
- **Measurement**: Raw sensor reading (pl. 705.0 m)
- **State Estimate**: EKF filtered estimate (pl. 704.8 m)
- **Covariance**: Estimation uncertainty (pl. 0.5)
- **Confidence**: Sensor reliability (pl. 95.0%)

#### Level 2 (Subsystem-level):
- **4 subsystem**: navigation, power, payload, comm
- **Health**: Subsystem health percentage (pl. 85.0%)
- **Covariance Trace**: Aggregated uncertainty measure (pl. 12.5)

#### Level 3 (Mission-level):
- **Mission Day**: 0, 1, 2, 3... (növekszik)
- **Feasibility**: 0-100% (EKF confidence alapú)
- **Anomaly Detected**: YES / NO
- **Detection Latency**: 0-5000 perc (mennyi idő alatt észleli a hibát)
- **Confidence**: 0-100% (EKF confidence)
- **Decision**: CONTINUE_WITH_MONITORING, STOP_IMAGING, SAFE_MODE
- **Scenes Today**: 0-700 (napi fényképek száma)
- **Data Loss**: 0-700 (elveszett/rossz minőségű fényképek)

### Változik-e?
- **IGEN** - Ahogy a szimuláció halad:
  - **Level 1**: Sensor measurements változnak (GPS hiba esetén rossz adat)
  - **Level 2**: Subsystem health változik (hiba esetén csökken)
  - **Level 3**: Feasibility, anomaly detection, data loss változik

### Mit mérünk?
- **Sensor accuracy**: Milyen pontosak a szenzorok (measurement vs. state estimate)
- **Estimation uncertainty**: Mennyire bizonytalan az EKF becslése (covariance)
- **Detection latency**: Mennyi idő alatt észleli a hibát (5-30 másodperc)
- **Data loss**: Mennyi adat veszik el (20-40% hiba esetén)

---

## 7. SZIMULÁCIÓ FUTÁSA

### Hogyan kellene változniuk az adatoknak?

#### Normál működés (nincs hiba):
- **EKF Feasibility**: 90-100% (stabil)
- **MetaSpace Feasibility**: 95-100% (stabil, kicsit magasabb)
- **Scenes Today**: 700 (normál)
- **Data Loss**: 0 (nincs veszteség)
- **Anomaly**: NONE

#### Hiba bekövetkezése (pl. GPS antenna damage):
- **EKF**:
  - Detection Latency: 5-30 másodperc (lassan észleli)
  - Confidence: 100% → 60% (lassan csökken)
  - Anomaly: NONE → DETECTED (5-30 másodperc után)
  - Scenes Today: 700 → 700 (tovább gyűjt, de rossz adat)
  - Data Loss: 0 → 200-300 (rossz minőségű fényképek)
  - Feasibility: 100% → 60% (lassan csökken)

- **MetaSpace**:
  - Detection Latency: <100 milliszekundum (azonnal észleli)
  - Feasibility: 100% → 85% (gyorsan reagál)
  - Anomaly: NONE → DETECTED (<100 ms után)
  - Scenes Today: 700 → 0 (azonnal leállítja a fényképezést)
  - Data Loss: 0 → 0 (nem gyűjt rossz adatot)
  - Safety Margin: 15% → 5% (csökken, de még pozitív)

#### Hiba után (recovery):
- **EKF**:
  - Recovery Time: 3-4 óra (ground involvement szükséges)
  - Confidence: 60% → 100% (lassan növekszik)
  - Scenes Today: 0 → 700 (lassan újraindul)

- **MetaSpace**:
  - Recovery Time: <1 másodperc (automatikus adaptation)
  - Feasibility: 85% → 100% (gyorsan helyreáll)
  - Scenes Today: 0 → 700 (azonnal újraindul)

---

## 8. MISSION DAY NÖVELÉSE

### Hogyan működik?
- **Mission Day**: 0, 1, 2, 3... (növekszik)
- **Frissítési gyakoriság**: 10 másodpercenként (5 update ciklus)
- **Új fájlok generálása**: Minden mission day-nél új .bio és .ekf fájlok

### Mit kellene látni?
- **Mission Day számláló**: Növekszik (0 → 1 → 2 → 3...)
- **Új fájlok**: Minden mission day-nél új fájlok generálódnak
- **Adatok változása**: Ahogy a mission day növekszik, az adatok változnak (hiba esetén)

---

## 9. ÖSSZEFOGLALÁS

### Mit kellene látni az ablakokban?

1. **Orbit Parameters**: Statikus adatok (nem változnak) + Current Orbit (növekszik)
2. **Task Timeline**: Task-ok idővonala (változik, ahogy a szimuláció halad)
3. **Orbit Visualization**: Műhold animáció (folyamatosan mozog)
4. **Comparison Panel**: EKF vs MetaSpace összehasonlítás (változik, hiba esetén)
5. **Bio-code Files**: 3 szintű bio-code adatok (változik, mission day növekedésével)
6. **EKF Files**: 3 szintű EKF adatok (változik, mission day növekedésével)

### Mit mérünk?

- **Detection Latency**: Mennyi idő alatt észleli a hibát (EKF: 5-30s, MetaSpace: <100ms)
- **Decision Quality**: Mennyire jó a döntés (feasibility alapján)
- **Data Loss**: Mennyi adat veszik el (EKF: 20-40%, MetaSpace: 0%)
- **Mission Success Rate**: Hány %-ban sikerül a küldetés (EKF: 70-85%, MetaSpace: 95-99%)
- **Recovery Time**: Mennyi idő alatt helyreáll (EKF: 3-4h, MetaSpace: <1s)

### Hogyan kellene változniuk?

- **Normál működés**: Stabil értékek (EKF: 90-100%, MetaSpace: 95-100%)
- **Hiba bekövetkezése**: Gyors változás (EKF: lassan, MetaSpace: gyorsan)
- **Hiba után**: Recovery (EKF: lassan, MetaSpace: gyorsan)
- **Mission day növekedése**: Folyamatos változás (új fájlok, új adatok)

---

## 10. KÖVETKEZŐ LÉPÉSEK

1. **Szimuláció indítása**: Start gomb megnyomása
2. **Mission day növelése**: Automatikus (10 másodpercenként)
3. **Hiba injektálása**: Opcionális (jövőbeli fejlesztés)
4. **Adatok frissítése**: Automatikus (2 másodpercenként)
5. **Fájlok generálása**: Automatikus (minden mission day-nél)


