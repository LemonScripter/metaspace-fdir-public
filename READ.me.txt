# 🛰️ MetaSpace: Deterministic Satellite Mission Assurance
### Determinisztikus Műholdas Küldetésbiztosítás

[![Status](https://img.shields.io/badge/Status-Stable-success)]() [![Version](https://img.shields.io/badge/Core-v1.4-blue)]() [![License](https://img.shields.io/badge/License-Proprietary-red)]()

**(English version below)**

---

## 🇭🇺 MAGYAR DOKUMENTÁCIÓ

### 1. Projekt Áttekintés
A **MetaSpace** egy új generációs fedélzeti szoftver-architektúra, amely szakít a hagyományos valószínűségi alapú (pl. EKF - Extended Kalman Filter) hibakezeléssel. A rendszer a **MetaSpace.bio** szabadalmaztatott determinisztikus logikáját használja a műholdak védelmére.

Ez a szimulátor összehasonlító elemzést végez ("A/B Teszt") a hagyományos ipari standard és a MetaSpace között, valós fizikai modellek (Landsat-9) alapján.

### 2. A Probléma
A hagyományos műholdas rendszerek (EKF) "Diplomataként" viselkednek: a hibás szenzoradatokat (zaj, drift) megpróbálják átlagolni és kisimítani.
* **Következmény:** Kritikus hiba esetén (pl. napelem törés, IMU sodródás) a rendszer lassan, de biztosan hibás döntéseket hoz ("Vakrepülés"), ami a küldetés elvesztéséhez vagy selejtes adatokhoz vezet.

### 3. A MetaSpace Megoldás
A MetaSpace "Bíróként" viselkedik: Fizikai Invariánsokat (megváltoztathatatlan törvényeket) használ.
* **Működés:** Ha egy adat fizikailag lehetetlen (pl. energiafogyasztás > termelés), a rendszer nem átlagol, hanem azonnal **izolálja** a hibás modult.
* **Eredmény:** Azonnali (<1ms) beavatkozás, zéró adatvesztés, a hardver túlélése.

### 4. Szimulációs Forgatókönyvek
A rendszer 4 kritikus hibaforgatókönyvet vizsgál (véletlenszerű időpontban injektálva):

| Hiba Típusa | Leírás | EKF Reakció (Hagyományos) | MetaSpace Reakció (Új) |
| :--- | :--- | :--- | :--- |
| **GPS Antenna** | Hirtelen pozícióugrás és zaj. | **Selejt gyártás:** Jónak hiszi a rossz adatot. | **Blokkolás:** Azonnal eldobja a hibás mérést. |
| **Akkumulátor** | Cella zárlat (Feszültségzuhanás). | **Dead Bus:** Hagyja teljesen lemerülni a gépet. | **Survival Mode:** Lekapcsolja a fogyasztókat. |
| **Napelem** | Törés miatti negatív energiamérleg. | **Lassú halál:** Nem észleli a trendet időben. | **Degradált Mód:** Észleli a hiányt és beavatkozik. |
| **IMU Drift** | Lopakodó navigációs sodródás. | **Téves irány:** Elfordul a műhold a Földtől. | **Pályakorrekció:** Észleli az invariáns sértést. |

### 5. Telepítés és Futtatás

**Követelmények:** Python 3.10+

1.  Környezet előkészítése:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  Szimulátor indítása:
    ```bash
    python app.py
    ```

3.  Nyisd meg a böngészőt: `http://localhost:5000`

---

## 🇬🇧 ENGLISH DOCUMENTATION

### 1. Project Overview
**MetaSpace** is a next-generation onboard software architecture that departs from traditional probabilistic fault management (e.g., EKF - Extended Kalman Filter). The system utilizes the proprietary deterministic logic of **MetaSpace.bio** to protect satellite assets.

This simulator performs a comparative analysis ("A/B Test") between the traditional industry standard and MetaSpace, based on high-fidelity physical models (Landsat-9).

### 2. The Problem
Traditional satellite systems (EKF) act as "Diplomats": they attempt to average out and smooth erroneous sensor data (noise, drift).
* **Consequence:** In critical failure scenarios (e.g., solar panel breakage, IMU drift), the system makes slowly degrading decisions ("Flying Blind"), leading to total mission loss or corrupted data lakes.

### 3. The MetaSpace Solution
MetaSpace acts as a "Judge": It uses Physical Invariants (immutable laws of physics).
* **Mechanism:** If data is physically impossible (e.g., Energy Consumption > Production), the system does not average; it immediately **isolates** the faulty module.
* **Result:** Instant (<1ms) intervention, zero data corruption, guaranteed hardware survival.

### 4. Simulation Scenarios
The system validates 4 critical failure scenarios (injected at random timestamps):

| Failure Type | Description | EKF Reaction (Legacy) | MetaSpace Reaction (New) |
| :--- | :--- | :--- | :--- |
| **GPS Antenna** | Sudden position jump & noise. | **Data Corruption:** Accepts invalid coordinates. | **Rejection:** Instantly discards invalid data. |
| **Battery** | Cell short-circuit (Voltage drop). | **Dead Bus:** Allows total depletion & loss of asset. | **Survival Mode:** Sheds non-essential loads. |
| **Solar Panel** | Negative energy budget (Breakage). | **Slow Death:** Fails to detect the trend in time. | **Degraded Mode:** Detects deficit & intervenes. |
| **IMU Drift** | Creeping navigational drift. | **False Attitude:** Satellite points away from Earth. | **Correction:** Detects invariant violation. |

### 5. Installation & Usage

**Requirements:** Python 3.10+

1.  Setup environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  Start the simulator:
    ```bash
    python app.py
    ```

3.  Open dashboard: `http://localhost:5000`

---

### 📂 Directory Structure / Könyvtárszerkezet

* `app.py` - Flask Web Server / Webszerver
* `backend/`
    * `modules/simulator.py` - Core Logic / Központi logika
    * `modules/landsat9.py` - Physics Engine / Fizikai motor
    * `modules/metaspace.py` - **The Innovation / Az Innováció**
    * `modules/ekf_model.py` - The Legacy Control / A Hagyományos Kontroll
* `results/` - JSON Audit Logs (Generated) / Generált audit naplók
* `templates/` & `static/` - Frontend Dashboard

---

**© 2025 MetaSpace.bio - LemonScript | Citrom Média LTD ** All rights reserved. / Minden jog fenntartva.
*Confidential & Proprietary Simulation Data.*