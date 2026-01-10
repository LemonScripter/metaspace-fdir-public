# Backward Compatibility - Meglévő Szimulációk Védelme

## Probléma

A navigation-plan szimulációhoz készült változások **nem szabad, hogy befolyásolják** a meglévő szimulációkat:
- **v3_fractal_sim** (V3 Neural Sandbox)
- **index.html** (V2 Main Simulation)

## Megoldás: Opcionális Paraméterek és Feltételes Logika

### 1. NeuralFractalNetwork.__init__()

```python
def __init__(self, landsat_model=None):  # ✅ Opcionális paraméter
    # ...
    self.landsat_model = landsat_model  # None is lehet (backward compatible)
```

**Eredmény:**
- `NeuralFractalNetwork()` → működik (v3_fractal_sim)
- `NeuralFractalNetwork(landsat_model=lm)` → működik (navigation-plan)

### 2. process_regeneration() - Feltételes Logika

```python
if self.landsat_model is not None:  # ✅ Csak akkor fut le, ha van landsat_model
    # Valós komponens health szinkronizálás
    # ...
# Ha nincs landsat_model, akkor NEM csinálunk semmit
# (A meglévő szimulációk működnek tovább, ahogy eddig)
```

**Eredmény:**
- `v3_fractal_sim` → `landsat_model = None` → **NEM fut le** a valós szinkronizálás
- `navigation-plan` → `landsat_model = Landsat9Model()` → **Fut le** a valós szinkronizálás

### 3. EKFSimulator - Degradáció Kikapcsolása

```python
# 0.5. Időbeli degradáció - CSAK navigation-plan szimulációhoz
# Fontos: Ez CSAK akkor fut le, ha van landsat_model
# A v3_fractal_sim NEM használ EKF-et, így NEM érinti!
```

**Eredmény:**
- `v3_fractal_sim` → **NEM használ EKF-et** → **NEM érinti**
- `navigation-plan` → **Használ EKF-et** → **Fut le** a degradáció logika

### 4. Globális Változók - Előtaggal

```python
# CSAK navigation-plan szimulációhoz (előtaggal, hogy ne keveredjen)
_navigation_plan_ekf_simulator = None
_navigation_plan_v3_network = None
_navigation_plan_landsat_model = None
```

**Eredmény:**
- `v3_fractal_sim` → **NEM használja** ezeket a változókat
- `navigation-plan` → **Használja** ezeket a változókat

## Tesztelés

### V3 Fractal Sim Teszt

```python
from backend.modules.v3_neural_core import NeuralFractalNetwork

# ✅ Működik landsat_model nélkül
n = NeuralFractalNetwork()
n.process_regeneration()  # ✅ Működik
```

### Navigation Plan Teszt

```python
from backend.modules.v3_neural_core import NeuralFractalNetwork
from backend.modules.landsat9 import Landsat9Model

# ✅ Működik landsat_model-lel
lm = Landsat9Model()
n = NeuralFractalNetwork(landsat_model=lm)
n.process_regeneration()  # ✅ Működik, valós komponens health-tel
```

## Garancia

✅ **v3_fractal_sim** → **NEM ÉRINTETT** (landsat_model = None)
✅ **index.html** → **NEM ÉRINTETT** (nem használja a módosított kódot)
✅ **navigation-plan** → **MŰKÖDIK** (landsat_model = Landsat9Model())

## Jövőbeli Fejlesztések

**SZABÁLY:** Minden új funkció **opcionális paraméterekkel** és **feltételes logikával** kell, hogy működjön, hogy **ne érintse** a meglévő szimulációkat!


