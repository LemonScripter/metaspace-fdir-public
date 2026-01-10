# Szimulációk Izolációja - 3 Különálló Szimuláció

## 3 Különálló Szimuláció

### 1. **index.html (V2 Main Simulation)**
- **Objektum**: `simulator = SimulationEngine()`
- **Használat**: `/api/simulation` endpoint
- **Jellemzők**:
  - Véletlenszerű hibainjekció (scenario alapján)
  - EKF vs MetaSpace összehasonlítás
  - Landsat9Model fizikai szimuláció
  - **NEM használ landsat_model-t a NeuralFractalNetwork-ben**

### 2. **v3_fractal_sim (V3 Neural Sandbox)**
- **Objektum**: `v3_network = NeuralFractalNetwork()` (landsat_model=None)
- **Használat**: `/api/v3/*` endpointok
- **Jellemzők**:
  - Chaos injection (manuális node kill)
  - Bio-code generálás
  - Holografikus hálózat
  - **NEM használ landsat_model-t** (backward compatible)

### 3. **navigation-plan (Navigation Plan Simulation)**
- **Objektum**: `_navigation_plan_v3_network = NeuralFractalNetwork(landsat_model=landsat_model)`
- **Használat**: `/api/simulation/generate-files` endpoint
- **Jellemzők**:
  - Valós Landsat9Model kapcsolat
  - Bio-code és EKF fájlok generálása
  - Mission day alapú szimuláció
  - **Használ landsat_model-t** (valós komponens health)

## Izoláció Garancia

✅ **index.html**: `simulator` objektum (külön)
✅ **v3_fractal_sim**: `v3_network` objektum (külön, landsat_model=None)
✅ **navigation-plan**: `_navigation_plan_v3_network` objektum (külön, landsat_model=lm)

**Fontos**: A 3 szimuláció **NEM érinti egymást**, mert külön objektumokat használnak!


