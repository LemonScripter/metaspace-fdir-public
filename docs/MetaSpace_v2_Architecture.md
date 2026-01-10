# 📄 MetaSpace v2.0: Bio-Mimetic Satellite Architecture
**Verzió:** 2.0 (Tervezési fázis)
**Státusz:** Fejlesztés alatt
**Fókusz:** Moduláris integritás, 3 szintű védelem, Fizikai sérülések (Meteor) kezelése

---

## 1. Vezetői Összefoglaló
A v1.0 sikeresen demonstrálta a determinisztikus védelem előnyét a hagyományos EKF-fel szemben "black-box" (doboz) szinten. A **v2.0 célja a "glass-box" (átlátszó) modell**: a műholdat nem egyetlen egységként, hanem önálló, intelligens komponensek hálózataként modellezzük (mint egy élő szervezetet).

Ez lehetővé teszi a **fizikai sérülések** (pl. meteor becsapódás a bal napelembe) realisztikus szimulálását, ahol a rendszernek "amputálnia" kell a sérült részt a túlélés érdekében.

---

## 2. A 3 Szintű Védelmi Hierarchia (Bio-Code)

A rendszer decentralizált intelligenciára épül. A MetaSpace nem csak egy központi agy, hanem minden sejtben jelen lévő kód.

### **Level 1: A Sejt Védelme (Component Integrity)**
* **Helye:** Egyedi szenzorok (pl. `StarTracker_A`, `Battery_Cell_4`).
* **Feladata:** Belső működés ellenőrzése (Self-Test).
* **Logika:** Hőmérséklet, Feszültség, Checksum, "Szívverés" (Heartbeat).
* **Reakció:** *Silent Drop* (Csendes eldobás) – A hibás alkatrész nem küld adatot, hogy ne szennyezze a hálózatot.

### **Level 2: A Szerv Védelme (Subsystem Redundancy)**
* **Helye:** Alrendszer vezérlők (pl. `GNC_Manager`, `EPS_Manager`).
* **Feladata:** Többségi szavazás (Voting) és redundancia kezelés.
* **Logika:** Ha van 3 szenzor, és 1 eltér, azt kizárjuk. Ha egy elsődleges egység (Primary) kiesik (Level 1 hiba miatt), aktiváljuk a tartalékot (Redundant).
* **Reakció:** *Isolation & Switchover* (Leválasztás és Átkapcsolás).

### **Level 3: A Szervezet Védelme (Mission Assurance)**
* **Helye:** A központi `MetaSpaceSimulator` (Master Arbiter).
* **Feladata:** Egzisztenciális döntések és Fizikai Invariánsok.
* **Logika:** Energiamérleg, Pálya-integritás, Küldetés céljának vizsgálata.
* **Reakció:** *Safe Mode / Deorbit / Self-Destruct* (Végső protokollok).

---

## 3. Hardver Leltár (Landsat-9 Modell)

A v2.0-ban ezeket a konkrét objektumokat fogjuk programozni:

### **A. GNC (Guidance, Navigation & Control) - Navigáció**
| Egység | Mennyiség | Funkció | Hiba Típusok |
| :--- | :--- | :--- | :--- |
| **Star Tracker** | 3 db (A, B, C) | Precíziós orientáció | Vakulás (Nap), Pixel hiba, Hőhalál |
| **GPS Vevő** | 2 db (Pri, Red) | Pozíció (X, Y, Z) | Jelvesztés, Spoofing, Drift |
| **IMU Blokk** | 2 db (Pri, Red) | Gyorsulás + Forgás | Bias Drift, Mechanikai törés |
| **Reaction Wheel** | 4 db (Piramis) | Stabilizálás | Súrlódás növekedés, Megszorulás |

### **B. EPS (Electrical Power System) - Energia**
| Egység | Mennyiség | Funkció | Hiba Típusok |
| :--- | :--- | :--- | :--- |
| **Solar Wing** | 2 db (Bal, Jobb) | Energiatermelés | Törés (Meteor), Hatásfok csökkenés |
| **Battery Pack** | 1 db (Multiplex) | Tárolás | Cella zárlat, Kapacitásvesztés |
| **PDU** | 1 db | Elosztás | Relé hiba (Nem tud lekapcsolni) |

---

## 4. Tervezett Fájlstruktúra (Modularitás)

A kód átláthatósága érdekében új modulokat vezetünk be:

* `backend/modules/components.py`: Az alapvető építőkockák (Level 1). Itt definiáljuk a `BioUnit` ősosztályt.
* `backend/modules/subsystems.py`: A menedzserek (Level 2). Itt van a `GNC` és `EPS` logika.
* `backend/modules/landsat9.py`: **Refaktorálás:** A `simulate_day` már nem képleteket számol, hanem meghívja az alrendszereket (`self.eps.update()`).
* `backend/modules/failure.py`: **Bővítés:** Most már specifikus egységeket tud elrontani (pl. `target="solar_wing_left"`, `type="physical_impact"`).

---

## 5. Fejlesztési Ütemterv

1.  **Fázis 1: Alapozás (`components.py`)** - A "Sejt" szintű osztályok és a Level 1 önellenőrzés megírása.
2.  **Fázis 2: Szervezés (`subsystems.py`)** - A "Szerv" szintű szavazó logika és redundancia-kezelés.
3.  **Fázis 3: Integráció** - A `Landsat9Model` átkötése az új struktúrára.
4.  **Fázis 4: Meteor Szimuláció** - Fizikai behatás szimulálása (pl. Bal oldali napelem + ST-A elvesztése egyszerre).