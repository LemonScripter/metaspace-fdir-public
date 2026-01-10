# ✅ MetaSpace Validációs Rendszer - Használati Útmutató

## 🎯 Cél

A validációs rendszer futtatja a MetaSpace rendszer teszteit és generál egy részletes validációs jegyzőkönyvet (JSON formátumban).

## 📋 Használat

### 1. **Parancssorból (Terminál)**

```bash
# Validáció futtatása
python backend/modules/validation_runner.py
```

**Kimenet:**
- Unit tesztek futtatása
- Integrációs tesztek futtatása
- Validációs jegyzőkönyv generálása
- Összefoglaló megjelenítése

**Jegyzőkönyv helye:**
```
validation_reports/validation_report_YYYYMMDD_HHMMSS.json
```

### 2. **API-n keresztül (Flask)**

#### A. Validáció futtatása

```bash
# POST kérés
curl -X POST http://localhost:5000/api/validation/run
```

**Válasz:**
```json
{
  "status": "success",
  "report": {
    "metadata": {
      "timestamp": "2025-01-28T12:38:27",
      "version": "1.4",
      "validation_type": "Full System Validation"
    },
    "summary": {
      "total_tests": 5,
      "passed": 4,
      "failed": 1,
      "success_rate": 80.0,
      "status": "FAILED"
    },
    "unit_tests": { ... },
    "integration_tests": { ... },
    "recommendations": [ ... ]
  }
}
```

#### B. Jegyzőkönyvek listázása

```bash
# GET kérés
curl http://localhost:5000/api/validation/reports
```

**Válasz:**
```json
{
  "status": "success",
  "reports": [
    {
      "filename": "validation_report_20251228_123827.json",
      "path": "...",
      "modified": "2025-12-28T12:38:27"
    }
  ]
}
```

#### C. Jegyzőkönyv letöltése

```bash
# GET kérés
curl http://localhost:5000/api/validation/reports/validation_report_20251228_123827.json
```

## 📊 Jegyzőkönyv Struktúra

### Metadata
```json
{
  "metadata": {
    "timestamp": "2025-01-28T12:38:27",
    "version": "1.4",
    "validation_type": "Full System Validation"
  }
}
```

### Összefoglaló
```json
{
  "summary": {
    "total_tests": 5,
    "passed": 4,
    "failed": 1,
    "success_rate": 80.0,
    "status": "FAILED"
  }
}
```

### Unit Tesztek
```json
{
  "unit_tests": {
    "total": 3,
    "passed": 3,
    "failed": 0,
    "errors": 0,
    "success_rate": 100.0,
    "failures": [],
    "errors_list": []
  }
}
```

### Integrációs Tesztek
```json
{
  "integration_tests": {
    "total": 2,
    "passed": 1,
    "failed": 1,
    "success_rate": 50.0,
    "test_details": [
      {
        "name": "MetaSpace Invariáns Ellenőrzések",
        "status": "PASSED",
        "details": { ... }
      }
    ]
  }
}
```

### Javaslatok
```json
{
  "recommendations": [
    "⚠️ 1 integrációs teszt sikertelen. Rendszer szintű ellenőrzés szükséges.",
    "⚠️ Integrációs teszt lefedettség nem 100%. További tesztek hozzáadása ajánlott."
  ]
}
```

## 🔍 Tesztek Részletei

### Unit Tesztek

1. **test_01_solar_panel_physics**
   - Napelem fizika ellenőrzése
   - Hiba injektálása után csökken-e a termelés?
   - Nem lett-e 0? (jobb szárny még működik)

2. **test_02_battery_drain_logic**
   - Akkumulátor merülés logika
   - Árnyékban merül-e az akku?

3. **test_03_isolation_mechanism**
   - Bio-Architektúra izoláció
   - Halott komponens inaktívvá válik-e?

### Integrációs Tesztek

1. **MetaSpace Invariáns Ellenőrzések**
   - Power health (akku < 20% → FAULT)
   - GPS health (gps_error > 50 → FAULT)
   - IMU health (drift > 0.5 → FAULT)
   - Mission feasibility (kritikus hibák → 0%)

2. **EKF vs MetaSpace Reakcióidő**
   - MetaSpace azonnal észleli-e a hibát?
   - Detection latency < 100ms?
   - Mission feasibility → 0%?

## 📈 Értelmezés

### Sikeres Validáció
- **Status:** `PASSED`
- **Success Rate:** ≥95%
- **Failed:** 0

### Részben Sikeres
- **Status:** `FAILED`
- **Success Rate:** 80-95%
- **Failed:** 1-2

### Sikertelen Validáció
- **Status:** `FAILED`
- **Success Rate:** <80%
- **Failed:** >2

## 🛠️ Hibaelhárítás

### Unit tesztek sikertelenek
1. Ellenőrizd a fizikai modellt (`backend/modules/landsat9.py`)
2. Ellenőrizd a hiba injektálást (`backend/modules/failure.py`)
3. Futtasd újra: `python backend/tests/verify_core.py`

### Integrációs tesztek sikertelenek
1. Ellenőrizd a MetaSpace logikát (`backend/modules/metaspace.py`)
2. Ellenőrizd az invariáns ellenőrzéseket
3. Futtasd újra: `python test/test_comparison.py`

### API hiba
1. Ellenőrizd, hogy a Flask szerver fut-e
2. Ellenőrizd a log fájlokat
3. Próbáld meg újraindítani: `python app.py`

## 📝 Példa Használat

### 1. Validáció futtatása
```bash
python backend/modules/validation_runner.py
```

### 2. Eredmények ellenőrzése
```bash
# Jegyzőkönyv megnyitása
cat validation_reports/validation_report_*.json | python -m json.tool
```

### 3. API-n keresztül
```bash
# Validáció futtatása
curl -X POST http://localhost:5000/api/validation/run

# Jegyzőkönyvek listázása
curl http://localhost:5000/api/validation/reports

# Legfrissebb jegyzőkönyv letöltése
curl http://localhost:5000/api/validation/reports/validation_report_20251228_123827.json
```

## 🎯 Következő Lépések

1. ✅ **Unit tesztek bővítése** - További fizikai invariánsok
2. ✅ **Integrációs tesztek bővítése** - Több hibatípus
3. ⚠️ **Formális verifikáció** - SMT Solver integráció
4. ⚠️ **Valós adatok validálása** - Landsat-9 telemetria

---

**Dátum:** 2025. január  
**Verzió:** v1.4  
**Státusz:** ✅ Működőképes

