# 🛰️ MetaSpace: Az űreszközök digitális immunrendszere
# 🛰️ MetaSpace: The Digital Immune System for Satellites

---

## 🇭🇺 MAGYAR LEÍRÁS

### 1. Mi a MetaSpace?
A MetaSpace egy forradalmian új fedélzeti szoftver-technológia, amely a műholdak túlélését biztosítja kritikus hibahelyzetekben. Míg a hagyományos rendszerek (mint az EKF) statisztikai alapon "tippelnek" a műhold állapotára, a MetaSpace **fizikai törvények (invariánsok)** alapján, determinisztikusan dönti el, hogy egy működés biztonságos-e.

Olyan ez, mint egy **digitális immunrendszer**: nem kell megvárnia, hogy a Földről (az orvostól) parancsot kapjon. Ha érzékeli a "fertőzést" (hibás adatot, zárlatot), azonnal izolálja a problémát, hogy a szervezet (a műhold) életben maradjon.

### 2. A Probléma: A "Diplomata" (Hagyományos EKF)
A mai műholdak irányító rendszerei (GNC) statisztikai szűrőket használnak. Ezek úgy viselkednek, mint egy **Diplomata**:
* Ha a szenzorok ellentmondó adatokat küldenek (pl. a GPS szerint jobbra megyünk, a giroszkóp szerint balra), a rendszer megpróbál **kompromisszumot** kötni és átlagolni.
* **A Veszély:** Ha egy hiba nem zajszerű, hanem tartós (pl. elgörbült napelem, vagy "hazudós" GPS), a Diplomata lassan elhiszi a hazugságot.
* **Eredmény:** A grafikonon a piros vonal (Hagyományos EKF) 100%-os biztonságot mutat, miközben a műhold éppen lemerül vagy letér a pályáról. Ez a **"Vakrepülés"**.

### 3. A Megoldás: A "Bíró" (MetaSpace)
A MetaSpace nem köt kompromisszumot. Úgy viselkedik, mint egy szigorú **Bíró**:
* Ismeri a fizika törvényeit (Energiamérleg, Impulzus-megmaradás). Ezek a szabályok sosem sérülhetnek.
* **Működés:** Ha egy szenzor olyan adatot küld, ami fizikailag lehetetlen (pl. "teleportálás" vagy "töltés árnyékban"), a MetaSpace nem átlagol. Azonnal **kizárja** a hibás eszközt a döntéshozatalból.
* **Eredmény:** A grafikonon a kék vonal (MetaSpace) a hiba pillanatában 0%-ra zuhan. Ez nem hiba, hanem **védelem**: a rendszer leállítja az adatgyűjtést, hogy ne mentsen selejtet, és Safe Mode-ba kapcsol, hogy megmentse a hardvert.

### 4. Mit látunk a Szimulátorban?
Ez a szoftver egy "Digitális Iker" (Digital Twin) környezet, amely a NASA Landsat-9 műholdjának fizikáját modellezi.
* **Forgatókönyvek:** Véletlenszerű időpontban (a futamidő 10-80%-a között) drasztikus hibákat idézünk elő (Napelem törés, GPS hiba, Akku zárlat).
* **A Grafikon:**
    * 🔴 **Piros szaggatott vonal:** Azt mutatja, mit hisz a hagyományos rendszer. Ha hiba esetén is magasan marad, az a veszély jele.
    * 🔵 **Kék vonal:** A MetaSpace reakciója. A cél, hogy hiba esetén azonnal reagáljon (leessen).
* **Üzleti Érték:** A szimuláció végén a rendszer kiszámolja, hány napnyi "vakrepülést" és adatvesztést spóroltunk meg.

---

## 🇬🇧 ENGLISH DESCRIPTION

### 1. What is MetaSpace?
MetaSpace is a revolutionary onboard software technology designed to ensure satellite survival during critical failures. While traditional systems (like EKF) use statistical methods to "guess" the satellite's state, MetaSpace uses **physical laws (invariants)** to deterministically decide if an operation is safe.

It acts like a **digital immune system**: it doesn't wait for commands from Earth (the doctor). If it detects an "infection" (corrupted data, short circuit), it immediately isolates the problem to keep the organism (the satellite) alive.

### 2. The Problem: The "Diplomat" (Traditional EKF)
Today's satellite guidance systems (GNC) use statistical filters. They act like a **Diplomat**:
* When sensors send conflicting data (e.g., GPS says "go right", Gyro says "go left"), the system tries to find a **compromise** by averaging the inputs.
* **The Danger:** If a fault is persistent rather than noisy (e.g., a broken solar panel or a "spoofed" GPS), the Diplomat slowly starts to believe the lie.
* **Result:** On the chart, the red line (Traditional EKF) shows 100% confidence while the satellite is actually draining its battery or drifting off course. This is **"Flying Blind."**

### 3. The Solution: The "Judge" (MetaSpace)
MetaSpace does not compromise. It acts like a strict **Judge**:
* It knows the laws of physics (Energy Budget, Conservation of Momentum). These laws can never be broken.
* **Mechanism:** If a sensor sends data that is physically impossible (e.g., "teleportation" or "charging in shadow"), MetaSpace does not average. It immediately **excludes** the faulty device from decision-making.
* **Result:** On the chart, the blue line (MetaSpace) drops to 0% the instant a failure occurs. This is not a bug, but **protection**: the system stops data collection to prevent corruption and enters Safe Mode to save the hardware.

### 4. What Does the Simulator Show?
This software is a "Digital Twin" environment modeling the physics of the NASA Landsat-9 satellite.
* **Scenarios:** At random times (between 10-80% of runtime), we inject drastic failures (Solar Panel breakage, GPS failure, Battery short).
* **The Chart:**
    * 🔴 **Red Dashed Line:** Shows what the traditional system believes. If it stays high during a failure, it indicates danger.
    * 🔵 **Blue Line:** MetaSpace's reaction. The goal is an immediate drop (reaction) upon failure.
* **Business Value:** At the end of the simulation, the system calculates how many days of "flying blind" and data loss were prevented.

---

### 5. Technológiai Stack / Technology Stack
* **Core:** Python 3.10 (Deterministic Logic)
* **Physics Engine:** Landsat-9 Orbital Mechanics & Energy Budgeting
* **Backend:** Flask (API) + Gunicorn
* **Frontend:** HTML5 / JavaScript (Chart.js for visualization)
* **Security:** Private Key Architecture (Simulated Secure Enclave)