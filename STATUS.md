# MetaSpace Satellite Simulation - Projekt Állapot

**Utolsó frissítés:** 2025. december 28.

## Áttekintés

A projekt egy determinisztikus FDIR (Fault Detection, Isolation, and Recovery) rendszert szimulál, amely az Extended Kalman Filter (EKF) rendszerekkel való összehasonlítást mutatja be. A rendszer két fő komponensből áll:
1. **V2 Main Simulation** (`/`): EKF vs MetaSpace összehasonlítás, hiba injektálás, költségbecslés
2. **V3 Neural Sandbox** (`/v3-sandbox`): Holografikus hálózati motor bio-kód vezérléssel, 100% matematikai validációval

## V3 Neural Sandbox - Jelenlegi Állapot

### Implementált Funkciók

#### 1. Bio-Kód Rendszer (3-Level Pipeline)
- **Level 1**: Node health → 64-bit bio-code (szenzor adatok)
- **Level 2**: Module aggregation → 32-bit bio-code (modul szintű aggregáció)
- **Level 3**: Mission decision → 64-bit bio-code (küldetés döntés, weighted feasibility)

**Főbb jellemzők:**
- Bio-kód **vezérli** a műhold működését (nem csak validálja)
- Level 3 bio-kód a Level 2 bio-kódokból generálódik (bio-kód vezérelt kontroll)
- Weighted feasibility számítás: logic 30%, navigation 25%, power 25%, comm 20%
- Action meghatározás feasibility és power status alapján
- Safety margin számítás a regeneráció sebességének módosításához

#### 2. Validációs Rendszer (100% Matematikai Bizonyítás)

**Invariánsok:**
- `health_bounds`: ∀n: 0 ≤ n.health ≤ 100
- `master_uniqueness`: |{n: n.is_master}| ≤ 1
- `power_dependency`: regen_active → ∃n: 'power' ∈ n.capabilities
- `feasibility_bounds`: 0 ≤ feasibility ≤ 100
- `regen_monotonicity`: regen → health_new ≥ health_old (regeneráció előtti health értékekkel összehasonlítva)
- `biocode_consistency`: decode(encode(state)) == state

**Matematikai Validáció:**
- Feasibility formula ellenőrzése
- Bio-code encoding/decoding konzisztencia (1% tolerancia)
- Minden művelet validálva (chaos injection, regeneration)

**Validációs Jelentés:**
- SHA-256 alapú validation ID (unforgeable)
- Operations log minden műveletről
- Detailed error information FAILED műveletekhez
- Összesített success rate és overall status
- Overall status explanation (100% validáció követelmény)
- Automatikus fájl mentés (csak aktív szimuláció során, vagy szimuláció végén)
- Automatikus cleanup (csak az utolsó 2 jelentés marad meg)

#### 3. Determinisztikus Öngyógyítás

**Bio-Kód Vezérlés:**
- Regeneráció csak akkor történik, ha:
  - Van power capability
  - Action nem EMERGENCY_HALT vagy SAFE_MODE
  - Feasibility > 20%
- Regeneráció sebessége a safety margin alapján módosul
- Master migration GIP alapú logikával

**Szimuláció Befejezése:**
- Ha nincs power capability ÉS vannak sérült node-ok → szimuláció befejeződik (végtelen ciklus elkerülése)
- Ha minden node 100% health ÉS feasibility >= 100% → szimuláció befejeződik
- `simulation_active` flag vezérli a jelentés generálást

#### 4. Frontend Funkciók

**UI Komponensek:**
- D3.js alapú hálózati visualizáció
- Node kattintás → egy node kikapcsolása (bug fix: csak a kattintott node)
- Bio-kód status megjelenítés (Level 3, Action, Feasibility, Safety Margin)
- Validációs jelentés panel (Overall Status, Invariants, Mathematics, FAILED műveletek részletei)
- Download Validation Report gomb (JSON formátumban)

**Hard Refresh Kezelés:**
- Automatikus backend reset oldal betöltéskor (`/api/v3/reset`)
- Backend állapot lekérése inicializáláskor (`/api/v3/state`)
- Biztosítja, hogy tiszta állapotból induljon minden szimuláció

**Regeneráció Loop:**
- Automatikus indítás chaos injection után
- 3 másodperces intervallum
- Automatikus leállítás szimuláció befejezéskor
- `simulationActive` flag vezérli a loop-ot

### Javított Bugok

1. **regen_monotonicity fix**: A health history tracking most a regeneráció **előtti** health értékeket használja, nem a health history-t (ami régi értékeket tartalmazhatott)

2. **Végtelen ciklus megoldás**: Ha nincs power capability, a szimuláció befejeződik, nem ragad végtelen ciklusba

3. **Node click bug**: Csak a kattintott node kapcsolódik ki, nem minden node egyszerre (event propagation stop + pontos targetId használata)

4. **Hard refresh reset**: Backend állapot automatikus reset-elése oldal betöltéskor, hogy ne legyen állapot inkonzisztencia

5. **Error details tárolása**: FAILED műveletek részletes hiba információi most tárolódnak és megjelennek a UI-ban

6. **Validation report generálás**: Csak aktív szimuláció során generálódnak jelentések, nem folyamatosan

### API Endpoint-ok

**V3 Neural Sandbox:**
- `POST /api/v3/chaos`: Káosz injektálás (node-ok kikapcsolása)
- `POST /api/v3/regen`: Regenerációs ciklus futtatása
- `POST /api/v3/config`: Konfiguráció módosítása (regen_rate)
- `GET /api/v3/validation/report/latest`: Legutóbbi validációs jelentés
- `POST /api/v3/reset`: Backend állapot reset-elése (hard refresh után)
- `GET /api/v3/state`: Backend állapot lekérése (inicializáláskor)

### Fájlstruktúra

**Backend Modulok:**
- `backend/modules/v3_neural_core.py`: Fő hálózati motor, regeneráció, chaos injection
- `backend/modules/v3_biocode_engine.py`: 3-level bio-code generálás és dekódolás
- `backend/modules/v3_validation_engine.py`: Invariánsok és matematikai validáció
- `backend/modules/v3_validation_report.py`: Validációs jelentés generálás és tárolás

**Frontend:**
- `templates/v3_fractal_sim.html`: V3 Neural Sandbox UI
- `static/js/main.js`: Main simulation frontend logika
- `static/css/style.css`: Stílusok

**Teszt Fájlok:**
- `test_validation_failures.py`: Validációs hibák tesztelése

### Ismert Korlátok / Megjegyzések

1. **Bio-code encoding/decoding tolerancia**: 1% tolerancia a feasibility értékeknél (integer tárolás miatt)
2. **Validation report cleanup**: Csak az utolsó 2 jelentés marad meg (automatikus törlés)
3. **Simulation active flag**: A szimuláció befejezésekor (`simulation_active = False`) nem generálódnak új jelentések
4. **Power dependency**: Ha nincs power capability, a szimuláció befejeződik (fizikai korlát)

### Következő Lépések (Opciók)

1. További invariánsok hozzáadása
2. Performance optimalizálás (nagy számú node esetén)
3. További teszt esetek
4. Dokumentáció bővítése

## V2 Main Simulation - Állapot

(A V2 részletek megtartása, ha szükséges...)

---

**Megjegyzés**: Ez a dokumentum a projekt aktuális állapotát dokumentálja. A GitHub-ra való feltöltés nem szükséges, csak helyi dokumentáció.
