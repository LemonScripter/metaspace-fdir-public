# Migrációs Stratégia - Moduláris UI
## Meglévő kód vs. Új moduláris architektúra

**Dátum:** 2025-12-28  
**Státusz:** Terv

---

## 1. JELENLEGI HELYZET

### 1.1 Meglévő Fájlok
- `static/js/main.js` - Monolitikus dashboard logika (587 sor)
- `static/js/interpretation.js` - Interpretációs logika
- `templates/index.html` - Fő dashboard (használja a main.js-t)
- `templates/v3_fractal_sim.html` - V3 Neural Sandbox (D3.js)

### 1.2 Jelenlegi Struktúra
```
index.html
  └─ <script src="/static/js/main.js"></script>
  └─ <script src="/static/js/interpretation.js"></script>
       └─ Globális változók (chartInstance, simulationInterval)
       └─ Monolitikus függvények (runSimulation, updateChart, stb.)
```

---

## 2. STRATÉGIA: "STRANGLER PATTERN"

### 2.1 Elv
**"Ne törjük el a meglévőt, építsük mellé az újat"**

- ✅ Meglévő kód **működőképes marad**
- ✅ Új oldal **modulárisan épül**
- ✅ Lassú migráció (ha szükséges)
- ✅ Nincs breaking change

### 2.2 Megközelítés

```
┌─────────────────────────────────────────┐
│  MEGLÉVŐ (Működik)                      │
│  - index.html → main.js                 │
│  - v3_fractal_sim.html                  │
│  - Nincs változás!                      │
└─────────────────────────────────────────┘
              +
┌─────────────────────────────────────────┐
│  ÚJ (Moduláris)                         │
│  - navigation-plan.html                 │
│  - static/js/core/                      │
│  - static/js/components/               │
│  - Teljesen új struktúra               │
└─────────────────────────────────────────┘
```

---

## 3. IMPLEMENTÁCIÓS TERV

### 3.1 Fázis 1: Új oldal modulárisan (NEM érinti a régit)
```
✅ Új fájlok létrehozása:
   - templates/navigation-plan.html (új oldal)
   - static/js/core/ (core modulok)
   - static/js/components/ (komponensek)
   - static/js/services/ (szolgáltatások)
   - static/js/pages/navigation-plan-page.js

❌ Nincs módosítás:
   - static/js/main.js (változatlan)
   - templates/index.html (változatlan)
   - templates/v3_fractal_sim.html (változatlan)
```

### 3.2 Fázis 2: Backend API endpoint-ok (új)
```
✅ Új route-ok:
   - /api/navigation/plan
   - /api/biocode/files/latest
   - /api/ekf/files/latest
   - /api/comparison/metrics

❌ Nincs módosítás:
   - /api/simulation (meglévő, működik)
   - /api/v3/* (meglévő, működik)
```

### 3.3 Fázis 3: Opcionális migráció (később, ha kell)
```
Ha később úgy döntünk, hogy a régi dashboard-ot is modulárisra
alakítjuk:
   - Lépésenkénti refaktorálás
   - Komponensekbe szétbontás
   - De NEM kötelező!
```

---

## 4. FÁJLSZERKEZET (ÚJ RÉSZ)

### 4.1 Új Fájlok (NEM érinti a régit)
```
static/
├── js/
│   ├── main.js                    ← MEGLÉVŐ (változatlan)
│   ├── interpretation.js          ← MEGLÉVŐ (változatlan)
│   │
│   └── core/                      ← ÚJ
│       ├── EventBus.js
│       ├── StateManager.js
│       ├── ComponentBase.js
│       └── APIClient.js
│   │
│   └── components/                 ← ÚJ
│       └── ...
│
templates/
├── index.html                      ← MEGLÉVŐ (változatlan)
├── v3_fractal_sim.html             ← MEGLÉVŐ (változatlan)
└── navigation-plan.html            ← ÚJ
```

### 4.2 Új Route (app.py)
```python
# Meglévő route-ok (változatlanok)
@app.route('/')
def index():
    return render_template('index.html')  # ← Működik továbbra is

@app.route('/v3-sandbox')
def v3_sandbox():
    return render_template('v3_fractal_sim.html')  # ← Működik továbbra is

# Új route (nem érinti a régit)
@app.route('/navigation-plan')
def navigation_plan():
    return render_template('navigation-plan.html')  # ← ÚJ
```

---

## 5. KOMPATIBILITÁS

### 5.1 Nincs Konfliktus
- ✅ Új modulok **nem használják** a régi globális változókat
- ✅ Új oldal **nem függ** a main.js-től
- ✅ Régi oldal **nem függ** az új moduloktól

### 5.2 Névtér Elválasztás
```javascript
// Régi kód (main.js)
let chartInstance = null;  // ← Globális, de csak index.html-ben használatos

// Új kód (core/EventBus.js)
class EventBus { ... }     // ← Modul, csak navigation-plan.html-ben használatos
```

---

## 6. ELŐNYÖK

### 6.1 Biztonság
- ✅ **Nincs breaking change** - meglévő funkciók működnek
- ✅ **Nincs rizikó** - ha valami nem működik, csak az új rész
- ✅ **Visszavonható** - ha kell, törölhetjük az új részt

### 6.2 Fejlesztési Sebesség
- ✅ **Párhuzamos fejlesztés** - régi és új egyszerre
- ✅ **Nincs merge conflict** - külön fájlok
- ✅ **Könnyű tesztelés** - új rész izoláltan tesztelhető

### 6.3 Lassú Migráció (Opcionális)
- ✅ Később refaktorálhatjuk a régi kódot is
- ✅ De **nem kötelező** - ha működik, működjön

---

## 7. KÖVETKEZŐ LÉPÉSEK

### 7.1 Azonnal (NEM érinti a régit)
1. ✅ Core modulok létrehozása (`static/js/core/`)
2. ✅ Új oldal template (`templates/navigation-plan.html`)
3. ✅ Új route (`app.py`-ban)
4. ✅ Első komponens implementálása

### 7.2 Később (Opcionális)
- Régi dashboard refaktorálása (ha kell)
- V3 sandbox modulárisra alakítása (ha kell)

---

## 8. PÉLDA: ÚJ OLDAL INICIALIZÁLÁS

### 8.1 navigation-plan.html
```html
<!DOCTYPE html>
<html>
<head>
    <title>Navigation Plan Execution</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <!-- ÚJ: Moduláris JS (NEM használja a main.js-t) -->
    <script type="module" src="/static/js/pages/navigation-plan-page.js"></script>
</head>
<body>
    <div id="orbit-visualization-container"></div>
    <div id="satellite-control-container"></div>
</body>
</html>
```

### 8.2 navigation-plan-page.js
```javascript
// ÚJ: Moduláris importok (NEM függ a main.js-től)
import OrbitVisualization from '../components/OrbitVisualization/OrbitVisualization.js';
import SatelliteControl from '../components/SatelliteControl/SatelliteControl.js';
// ...

// Inicializálás
document.addEventListener('DOMContentLoaded', async () => {
    const page = new NavigationPlanPage();
    await page.init();
});
```

---

## 9. ÖSSZEFOGLALÁS

### ✅ MIT CSINÁLUNK
- Új fájlok létrehozása (core, components, services)
- Új oldal template (navigation-plan.html)
- Új route-ok (backend API)
- Moduláris architektúra az új oldalon

### ❌ MIT NEM CSINÁLUNK
- **NEM módosítjuk** a main.js-t
- **NEM módosítjuk** az index.html-t
- **NEM módosítjuk** a v3_fractal_sim.html-t
- **NEM törjük el** a meglévő funkciókat

### 🎯 EREDMÉNY
- Meglévő kód **működik továbbra is**
- Új oldal **modulárisan épül**
- **Nincs rizikó**, nincs breaking change
- Később **opcionálisan refaktorálhatjuk** a régit is

---

**Státusz:** Terv kész, implementációra vár (NEM érinti a meglévőt!)


