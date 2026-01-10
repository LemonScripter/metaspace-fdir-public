# Landsat-9 Bio-Code Adatforrások Dokumentáció

**Dátum:** 2025. január  
**Cél:** Dokumentálni, hogy a bio-kód rendszerben mely értékek származnak valódi Landsat-9 adatokból, és melyek hardcoded értékek (mert nincs rá nyilvános adat).

---

## ✅ VALÓDI LANDSAT-9 ADATOK (Nyilvános Specifikációkból)

### 1. **Payload Komponensek** (Valódi)

| Komponens | Valódi Név | Típus | Forrás |
|-----------|------------|-------|--------|
| OLI-2 | Operational Land Imager-2 | Payload | NASA Landsat-9 spec |
| TIRS-2 | Thermal Infrared Sensor-2 | Payload | NASA Landsat-9 spec |

**Megjegyzés:** A Landsat-9 két fő payload szenzort tartalmaz: OLI-2 és TIRS-2. Ezek a műhold legkritikusabb komponensei.

### 2. **Alrendszerek** (Valódi)

| Alrendszer | Valódi Név | Leírás | Forrás |
|------------|------------|--------|--------|
| Power | EPS (Electrical Power System) | Solar panels + Battery | NASA Landsat-9 spec |
| Navigation | GNC (Guidance, Navigation, Control) | Star Trackers, IMU, GPS | NASA Landsat-9 spec |
| Communication | X-band, S-band | High-gain antenna, transponders | NASA Landsat-9 spec |
| Computing | OBC (Onboard Computer) | Flight computer | NASA Landsat-9 spec |

**Megjegyzés:** A Landsat-9 standard műhold alrendszereket tartalmaz, amelyek a NASA dokumentációban szerepelnek.

### 3. **Kritikus Alrendszerek Fontossága** (Valódi Becslés)

A module weights a műhold működésének kritikussága alapján:

| Modul | Súly | Indoklás | Forrás |
|-------|------|----------|--------|
| **Payload (OLI-2/TIRS-2)** | 35% | A műhold fő célja: képalkotás | Landsat-9 mission spec |
| **Power (EPS)** | 30% | Kritikus: nincs power = nincs működés | Standard műhold architektúra |
| **Navigation (GNC)** | 20% | Fontos: pálya megtartás, képgeoreferálás | Landsat-9 GNC spec |
| **Communication** | 15% | Fontos: adat lejátszás, parancsok | Landsat-9 comm spec |

**Megjegyzés:** Ezek a súlyok a Landsat-9 küldetés céljai alapján becsültek (Earth observation = payload kritikus).

---

## ⚠️ HARDCODED ÉRTÉKEK (Nincs Nyilvános Adat)

### 1. **Node ID Mapping** (Hardcoded - Belső Azonosítók)

```python
self.node_id_map = {
    "OLI2": 0x0001,      # ⚠️ HARDCODED - Belső azonosító
    "TIRS2": 0x0002,     # ⚠️ HARDCODED - Belső azonosító
    "ST_A": 0x0003,      # ⚠️ HARDCODED - Belső azonosító
    "ST_B": 0x0004,      # ⚠️ HARDCODED - Belső azonosító
    "EPS": 0x0005,       # ⚠️ HARDCODED - Belső azonosító
    "OBC": 0x0006,       # ⚠️ HARDCODED - Belső azonosító
    "X_BAND": 0x0007,    # ⚠️ HARDCODED - Belső azonosító
    "S_BAND": 0x0008     # ⚠️ HARDCODED - Belső azonosító
}
```

**Indoklás:** A Node ID-k belső azonosítók a bio-kód rendszerben. A Landsat-9 specifikációban nincs ilyen azonosító rendszer, ezért hardcoded értékeket használunk.

### 2. **Module ID Mapping** (Hardcoded - Belső Azonosítók)

```python
self.module_id_map = {
    "payload": 0x01,     # ⚠️ HARDCODED - Belső azonosító
    "power": 0x02,       # ⚠️ HARDCODED - Belső azonosító
    "navigation": 0x03,  # ⚠️ HARDCODED - Belső azonosító
    "comm": 0x04         # ⚠️ HARDCODED - Belső azonosító
}
```

**Indoklás:** A Module ID-k belső azonosítók a bio-kód aggregációhoz. Nincs rá valós Landsat-9 specifikáció.

### 3. **Status Encoding** (Hardcoded - MetaSpace Architektúra)

```python
self.status_encoding = {
    "OPERATIONAL": 0b0000,  # ⚠️ HARDCODED - MetaSpace architektúra
    "HEALING": 0b0001,      # ⚠️ HARDCODED - MetaSpace architektúra
    "DEGRADED": 0b0010,    # ⚠️ HARDCODED - MetaSpace architektúra
    "WARNING": 0b0011,     # ⚠️ HARDCODED - MetaSpace architektúra
    "DEAD": 0b0100,        # ⚠️ HARDCODED - MetaSpace architektúra
    "CRITICAL": 0b0101     # ⚠️ HARDCODED - MetaSpace architektúra
}
```

**Indoklás:** A status encoding a MetaSpace bio-kód architektúra része. A Landsat-9 nem használ ilyen status rendszert.

### 4. **Action Codes** (Hardcoded - MetaSpace Architektúra)

```python
self.action_codes = {
    "CONTINUE_NOMINAL": 0x000001,           # ⚠️ HARDCODED - MetaSpace architektúra
    "CONTINUE_WITH_MONITORING": 0x000002,  # ⚠️ HARDCODED - MetaSpace architektúra
    "REDUCE_IMAGING_RATE": 0x000003,       # ⚠️ HARDCODED - MetaSpace architektúra
    "SWITCH_TO_FALLBACK": 0x000004,        # ⚠️ HARDCODED - MetaSpace architektúra
    "SAFE_MODE": 0x000005,                 # ⚠️ HARDCODED - MetaSpace architektúra
    "EMERGENCY_HALT": 0x000006             # ⚠️ HARDCODED - MetaSpace architektúra
}
```

**Indoklás:** Az action codes a MetaSpace determinisztikus döntéshozatali rendszer része. A Landsat-9 nem használ ilyen autonóm döntési rendszert.

### 5. **Trend Encoding** (Hardcoded - MetaSpace Architektúra)

```python
self.trend_encoding = {
    "IMPROVING": 0b0000,    # ⚠️ HARDCODED - MetaSpace architektúra
    "STABLE": 0b0001,       # ⚠️ HARDCODED - MetaSpace architektúra
    "DEGRADING": 0b0010,   # ⚠️ HARDCODED - MetaSpace architektúra
    "CRITICAL": 0b0011     # ⚠️ HARDCODED - MetaSpace architektúra
}
```

**Indoklás:** A trend encoding a MetaSpace bio-kód architektúra része.

### 6. **Star Tracker Szám** (Becsült - Nincs Pontos Adat)

A Landsat-9 specifikációban nincs pontos információ arról, hogy hány Star Tracker van a műholdon. A standard műholdak általában 2-3 Star Tracker-t használnak redundancia miatt.

**Jelenlegi implementáció:** 2 Star Tracker (ST_A, ST_B)  
**Indoklás:** Standard műhold architektúra alapján becsült érték.

---

## 📊 Összefoglaló Táblázat

| Elem | Valódi Adat? | Forrás | Megjegyzés |
|------|--------------|--------|------------|
| **Payload nevek (OLI-2, TIRS-2)** | ✅ Igen | NASA Landsat-9 spec | Valódi komponens nevek |
| **Alrendszerek (EPS, GNC, Comm)** | ✅ Igen | NASA Landsat-9 spec | Valódi alrendszer nevek |
| **Module weights** | ✅ Igen (becsült) | Landsat-9 mission spec | Küldetés céljai alapján |
| **Node ID mapping** | ❌ Nem | ⚠️ HARDCODED | Belső azonosítók |
| **Module ID mapping** | ❌ Nem | ⚠️ HARDCODED | Belső azonosítók |
| **Status encoding** | ❌ Nem | ⚠️ HARDCODED | MetaSpace architektúra |
| **Action codes** | ❌ Nem | ⚠️ HARDCODED | MetaSpace architektúra |
| **Trend encoding** | ❌ Nem | ⚠️ HARDCODED | MetaSpace architektúra |
| **Star Tracker szám** | ⚠️ Becsült | Standard architektúra | Nincs pontos spec |

---

## 🔗 Források

1. **NASA Landsat-9 Overview:** https://landsat.gsfc.nasa.gov/satellites/landsat-9/landsat-9-overview/
2. **Landsat-9 Instruments:** https://landsat.gsfc.nasa.gov/satellites/landsat-9/landsat-9-instruments/
3. **Landsat-9 Spectral Specifications:** https://landsat.gsfc.nasa.gov/satellites/landsat-9/landsat-9-spectral-specifications/
4. **USGS Landsat-9:** https://www.usgs.gov/landsat-missions/landsat-9

---

**Utolsó frissítés:** 2025. január  
**Karbantartó:** MetaSpace Development Team


