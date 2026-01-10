# EKF Confidence Reset Probléma - Elemzés

## Probléma

Az EKF confidence:
1. **Csökken** 1-1 tized százalékot (0.1-0.3%)
2. **Visszaugrik** 100%-ra
3. Nincs hiba a szimulációban

## Ok

### 1. ÚJ EKFSimulator minden alkalommal

```python
# app.py - generate_simulation_files() metódusban:
ekf_simulator = EKFSimulator(landsat_model)  # ⚠️ ÚJ objektum minden alkalommal!
ekf_simulator.mission_day = mission_day
ekf_simulator.update()
```

**Probléma:** Minden mission day-nél **ÚJ EKFSimulator objektum** jön létre!

### 2. EKFSimulator.__init__() reseteli a confidence-t

```python
# ekf_model.py - __init__() metódusban:
def __init__(self, landsat_model):
    self.confidence = 100.0  # ⚠️ MINDIG 100%-ra resetelődik!
```

**Probléma:** Minden új objektum létrehozásakor a confidence **100%-ra resetelődik**!

### 3. Degradáció csak az update() metódusban történik

```python
# ekf_model.py - update() metódusban:
if self.mission_day > 0:
    random_degradation = random.uniform(0, 0.3)
    self.confidence = max(0, self.confidence - random_degradation)  # Csökken 0-0.3%
```

**Probléma:** A degradáció csak az `update()` hívásakor történik, de mivel mindig új objektum jön létre, a confidence mindig 100%-ról indul!

## Folyamat

1. **Mission Day 1**:
   - Új EKFSimulator → confidence = 100%
   - `update()` → degradáció 0.1% → confidence = 99.9%
   - Fájl mentés → confidence = 99.9%

2. **Mission Day 2**:
   - **ÚJ EKFSimulator** → confidence = **100%** (reset!)
   - `update()` → degradáció 0.2% → confidence = 99.8%
   - Fájl mentés → confidence = 99.8%

3. **Mission Day 3**:
   - **ÚJ EKFSimulator** → confidence = **100%** (reset!)
   - `update()` → degradáció 0.15% → confidence = 99.85%
   - Fájl mentés → confidence = 99.85%

**Eredmény:** 
- Minden nap **csökken** 0.1-0.3%-ot (degradáció miatt)
- De **visszaugrik** 100%-ra (mert új objektum jön létre)
- A felhasználó látja: 99.9% → 100% → 99.8% → 100% → 99.85%

## Megoldás

### Opció 1: EKFSimulator megőrzése (ajánlott)
- Az EKFSimulator objektumot **meg kellene őrizni** a fájlok között
- Globális state vagy singleton pattern
- A confidence **nem resetelődik** minden alkalommal

### Opció 2: Confidence betöltése fájlból
- Az EKF confidence-t **menteni** a fájlokba
- Következő nap: **betölteni** a confidence-t a fájlból
- Folytatni a degradációt onnan

### Opció 3: Degradáció kikapcsolása normál működésben
- Ha nincs hiba, **ne legyen degradáció**
- Confidence = 100% stabil marad
- Csak hiba esetén csökkenjen

## Jelenlegi viselkedés

**Miért csökken 0.1-0.3%-ot?**
- Degradáció: `random.uniform(0, 0.3)` per nap
- Ez történik az `update()` metódusban

**Miért ugrik vissza 100%-ra?**
- Új EKFSimulator objektum jön létre minden nap
- `__init__()` reseteli a confidence-t 100%-ra

**Ez realisztikus?**
- ❌ **NEM!** Valós műholdon az EKF confidence **nem resetelődik** minden nap
- ❌ **NEM!** Normál működésben (nincs hiba) a confidence **stabil marad** (100%)

## Javaslat

**Javítás 1: EKFSimulator megőrzése**
- Globális EKFSimulator objektum (vagy singleton)
- A confidence **nem resetelődik** minden nap

**Javítás 2: Degradáció kikapcsolása normál működésben**
- Ha nincs hiba, **ne legyen degradáció**
- Confidence = 100% stabil marad

**Javítás 3: Valós komponens health alapján**
- EKF confidence = valós szenzor health alapján
- Ha a szenzorok egészségesek → confidence = 100%
- Ha a szenzorok hibásak → confidence csökken


