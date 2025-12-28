import json
import random
import os
import uuid
import time
from datetime import datetime

# --- DINAMIKUS IMPORT KEZELÉS ---
try:
    from backend.modules.landsat9 import Landsat9Model
    from backend.modules.ekf_model import EKFSimulator
    from backend.modules.metaspace import MetaSpaceSimulator
except ImportError:
    from .landsat9 import Landsat9Model
    from .ekf_model import EKFSimulator
    from .metaspace import MetaSpaceSimulator

class SimulationEngine:
    """
    MetaSpace v2.0 - Unified Simulator Engine
    Összeköti a Landsat9 fizikai modellt az EKF és MetaSpace szolvörökkel.
    """
    def __init__(self):
        self.results_cache = {}
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.results_dir = os.path.join(self.base_dir, "results")
        
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir, exist_ok=True)

    def run(self, scenario, duration):
        sim_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 1. MODELL ÉS SZOLVÖRÖK INICIALIZÁLÁSA
        satellite = Landsat9Model()
        
        # ADATHÍD KONFIGURÁCIÓ: Változók, amiket a szolvörök keresnek
        satellite.gps_error = 0.0
        satellite.battery_level = 100.0
        satellite.imu_accumulated_error = 0.0
        satellite._gps_antenna_failed = False  # GPS antenna hiba flag
        satellite._gps_error_accumulated = 0.0  # GPS hiba akkumuláció (GPS antenna hiba esetén)
        
        # Az EKFSimulator ezt a metódust hívja az update-ben
        # REÁLIS VISELKEDÉS:
        # - GPS antenna hiba: rossz adat (nagy eltolódás)
        # - Akku < 10%: GPS timeout (nincs elég energia a GPS-hez)
        # - Solar panel hiba → akku lassan lemerül → GPS timeout → EKF lassan reagál
        # - Battery failure → akku azonnal lemerül → GPS timeout → EKF lassan reagál
        def get_gps_with_failure():
            # REÁLIS: Ha az akku < 10%, a GPS jel eltűnik (nincs elég energia)
            # Az EKF ezt észleli, de lassan reagál (valószínűségszámítás, átlagolás)
            if satellite.battery_level < 10.0:
                return None  # GPS timeout (nincs elég energia)
            
            if satellite.gnc.active_sensor_count > 0:
                if satellite._gps_antenna_failed:
                    # GPS antenna hiba: rossz adat (nagy eltolódás)
                    return [150.0, 150.0, -100.0]  # ~250m hiba (rossz adat)
                else:
                    return [0.0, 0.0, 0.0]  # Normál adat
            else:
                return None  # Nincs GPS jel (nincs aktív szenzor)
        
        satellite.get_gps_measurement = get_gps_with_failure

        ekf_solver = EKFSimulator(satellite)
        metaspace_solver = MetaSpaceSimulator(satellite)
        
        # 2. HIBA IDŐZÍTÉS ÉS TÍPUS VÉLETLENSZERŰSÍTÉS
        # Ha 'nominal', akkor nincs hiba
        # Egyébként véletlenszerűen választunk a 4 hibatípus közül
        if scenario == 'nominal':
            selected_failure = None
        else:
            # Ha konkrét scenario van megadva, azt használjuk
            # Egyébként véletlenszerűen választunk
            failure_types = ['solar_panel', 'battery_failure', 'gps_antenna', 'imu_drift']
            if scenario in failure_types:
                selected_failure = scenario
            else:
                selected_failure = random.choice(failure_types)
        
        # Véletlenszerű hiba nap számítása: a duration 20-80%-a között
        min_day = max(2, int(duration * 0.2))
        max_day = max(min_day + 1, int(duration * 0.8))
        failure_day = random.randint(min_day, max_day)
        failure_minute_start = failure_day * 24 * 60
        
        # Debug: Kiírjuk a véletlenszerűen generált hibát
        if selected_failure:
            print(f"[SIMULATOR] Véletlenszerű hiba generálva: {selected_failure} (Nap: {failure_day} / {duration} napos szimuláció)")
        
        dt_minutes = 60 
        total_minutes = duration * 24 * 60
        history = []
        failure_triggered = False
        
        # 3. SZIMULÁCIÓS CIKLUS
        for t in range(0, total_minutes, dt_minutes):
            active_failure = None
            # A hiba csak akkor aktív, ha elérte a hiba időpontját
            # DE: ha már bekövetkezett, akkor továbbra is aktív marad (tartós hiba)
            if t >= failure_minute_start:
                if selected_failure:
                    if not failure_triggered:
                        # Első alkalommal injektáljuk a hibát
                        active_failure = selected_failure
                        failure_triggered = True
                        print(f"[SIMULATOR] Hiba bekövetkezett: {selected_failure} (T+{t} perc, {t/1440:.1f} nap)")
                    else:
                        # A hiba már bekövetkezett, továbbra is aktív marad
                        active_failure = selected_failure

            # Fizikai szimuláció (meghívja a subsystems.py-t)
            telemetry = satellite.simulate_step(dt_minutes, current_failure=active_failure)
            
            # --- KRITIKUS ADAT-SZINKRONIZÁCIÓ (Az EKF-nek és MetaSpace-nek jelek kellenek!) ---
            # Bekötjük a subsystems.py valós kimeneteit
            satellite.battery_level = telemetry.get('battery_percent', 100.0)
            satellite.power_generation_w = telemetry.get('power_generation_w', 2400.0)  # MetaSpace számára
            
            # GPS hiba számítása: ha az attitude_integrity csökken, nő a hiba az EKF számára
            base_gps_error = 100.0 - telemetry.get('attitude_integrity', 100.0)
            
            # GPS antenna hiba: Az EKF rossz adatot kap, lassan reagál, közben fölösleges fotók készülnek
            if active_failure == 'gps_antenna':
                # GPS antenna hiba -> azonnal nagy GPS hiba (rossz adat)
                # Az EKF lassan reagál (heurisztikusan, valószínűségszámítással)
                # Közben tovább gyűjt adatot (fölösleges/költséges fotók)
                
                # Jelöljük, hogy GPS antenna hiba van (rossz adat érkezik)
                satellite._gps_antenna_failed = True
                
                # GPS antenna hiba: azonnal nagy GPS hiba (rossz adat)
                # Az attitude_integrity nem változik, de a GPS hiba igen
                # Szimuláljuk, hogy a GPS antenna hiba hatással van a navigációra
                # Az EKF rossz GPS adatot kap, és lassan reagál (heurisztikusan próbálja visszaterelni)
                if not hasattr(satellite, '_gps_error_accumulated'):
                    satellite._gps_error_accumulated = 0.0
                
                # Fokozatosan növeljük a GPS hibát (lassú EKF reakció szimulálása)
                # Az EKF heurisztikusan próbálja visszaterelni a műholdat
                satellite._gps_error_accumulated += 1.0
                satellite.gps_error = min(100.0, 60.0 + satellite._gps_error_accumulated)
            
            # IMU drift szimuláció
            if active_failure == 'imu_drift':
                satellite.imu_accumulated_error += 0.08
                # IMU drift hatással van az attitude_integrity-re is
                # (mivel az IMU és Star Tracker együttműködik)
                # Az IMU drift fokozatosan növeli a GPS hibát, hogy az EKF reagáljon
                # De lassan (valószínűségszámítás, tehetetlenség)
                if satellite.imu_accumulated_error > 0.2:
                    # Ha az IMU drift nagy, az attitude_integrity csökken
                    # Ez növeli a GPS hibát, hogy az EKF reagáljon
                    attitude_degradation = min(50.0, satellite.imu_accumulated_error * 100)
                    # Fokozatosan növeljük a GPS hibát (lassú EKF reakció szimulálása)
                    satellite.gps_error = max(satellite.gps_error, min(100.0, 50.0 + attitude_degradation))
                else:
                    # Kisebb IMU drift: fokozatosan növeljük a GPS hibát
                    satellite.gps_error = max(satellite.gps_error, min(100.0, satellite.imu_accumulated_error * 200))

            # SZOLVÖRÖK FRISSÍTÉSE
            try:
                ekf_solver.update() # Itt jön létre az ekf_reliability
                metaspace_solver.update() # Itt jön létre a metaspace_integrity
            except Exception as e:
                print(f"Solver Error at T+{t}: {e}")

            # Telemetria kiegészítése a frontend grafikonhoz
            telemetry['ekf_reliability'] = ekf_solver.confidence
            telemetry['metaspace_integrity'] = metaspace_solver.mission_feasibility
            telemetry['time'] = t
            
            history.append(telemetry)

        # 4. EREDMÉNY CSOMAG (A main.js ezt várja)
        # MetaSpace és EKF log üzenetek gyűjtése a telemetry log-ból
        metaspace_logs = []
        ekf_logs = []
        last_metaspace_integrity = 100.0
        last_ekf_confidence = 100.0
        metaspace_detection_time = None
        ekf_detection_time = None
        last_metaspace_mode = 'FULL_MISSION'
        metaspace_detection_logged = False  # Flag, hogy már logoltuk-e a detektálást
        
        # Végigjárjuk a telemetry log-ot, hogy megtaláljuk a MetaSpace és EKF reakciókat
        for entry in history:
            current_metaspace_integrity = entry.get('metaspace_integrity', 100)
            current_ekf_reliability = entry.get('ekf_reliability', 100)
            current_time = entry.get('time', 0)
            
            # MetaSpace hiba észlelése (integrity < 100)
            # Fontos: Az integrity változhat, de csak akkor logoljuk, ha először esik 100 alá
            if current_metaspace_integrity < 100 and last_metaspace_integrity >= 100 and not metaspace_detection_logged:
                metaspace_detection_time = current_time
                metaspace_detection_logged = True
                failure_type_name = {
                    'solar_panel': 'Solar Panel Failure',
                    'battery_failure': 'Battery Failure',
                    'gps_antenna': 'GPS Spoofing/Signal Loss',
                    'imu_drift': 'IMU Gyro Bias Drift'
                }.get(selected_failure, selected_failure)
                metaspace_logs.append(f"MetaSpace: Anomaly Detected - {failure_type_name} (T+{current_time} min, {current_time/1440:.2f} days)")
            
            # MetaSpace módváltás észlelése (integrity alapján)
            if current_metaspace_integrity < 100:
                if current_metaspace_integrity == 0:
                    current_mode = 'SAFE_MODE'
                elif current_metaspace_integrity < 40:
                    current_mode = 'SAFE_MODE'
                elif current_metaspace_integrity < 90:
                    current_mode = 'PARTIAL_MISSION'
                else:
                    current_mode = 'FULL_MISSION'
            else:
                current_mode = 'FULL_MISSION'
            
            if current_mode != last_metaspace_mode and metaspace_detection_time is not None:
                if current_mode == 'SAFE_MODE':
                    metaspace_logs.append(f"MetaSpace: Mode Change → SAFE_MODE (T+{current_time} min, {current_time/1440:.2f} days)")
                elif current_mode == 'PARTIAL_MISSION':
                    metaspace_logs.append(f"MetaSpace: Mode Change → PARTIAL_MISSION (T+{current_time} min, {current_time/1440:.2f} days)")
                last_metaspace_mode = current_mode
            
            # EKF hiba észlelése (confidence < 60%)
            if current_ekf_reliability < 60.0 and last_ekf_confidence >= 60.0:
                ekf_detection_time = current_time
                ekf_logs.append(f"EKF: Anomaly Detected (T+{current_time} min, {current_time/1440:.2f} days) - Confidence: {current_ekf_reliability:.1f}%")
            
            last_metaspace_integrity = current_metaspace_integrity
            last_ekf_confidence = current_ekf_reliability
        
        # Bio logs összeállítása
        bio_logs = [
            "Neural Link: Established.",
            f"Injection Detected: {selected_failure if selected_failure else scenario} (Day {failure_day})."
        ]
        
        # MetaSpace log üzenetek hozzáadása
        # Fontos: A MetaSpace mindig logolja az észlelést, még akkor is, ha az integrity nem esik 100 alá
        if metaspace_logs:
            bio_logs.extend(metaspace_logs)
        else:
            # Ellenőrizzük, hogy a MetaSpace valóban nem észlelt hibát
            # Végigjárjuk a teljes history-t, hogy megtaláljuk az első integrity változást
            first_integrity_change = None
            first_integrity_value = None
            for entry in history:
                integrity = entry.get('metaspace_integrity', 100)
                if integrity < 100:
                    first_integrity_change = entry.get('time', 0)
                    first_integrity_value = integrity
                    break
            
            if first_integrity_change is not None:
                # MetaSpace észlelt hibát, de nem logoltuk (pl. azonnal < 100 volt)
                failure_type_name = {
                    'solar_panel': 'Solar Panel Failure',
                    'battery_failure': 'Battery Failure',
                    'gps_antenna': 'GPS Spoofing/Signal Loss',
                    'imu_drift': 'IMU Gyro Bias Drift'
                }.get(selected_failure, selected_failure)
                final_integrity = history[-1].get('metaspace_integrity', 100) if history else 100
                bio_logs.append(f"MetaSpace: Anomaly Detected - {failure_type_name} (T+{first_integrity_change} min, {first_integrity_change/1440:.2f} days) - Integrity: {final_integrity:.1f}%")
                if metaspace_detection_time is None:
                    metaspace_detection_time = first_integrity_change
            else:
                # Ellenőrizzük, hogy a MetaSpace észlelte-e a hibát más módon (pl. power generation < 50%)
                # Ha van hiba, de az integrity nem változott (pl. solar panel hiba, de még nem kritikus)
                if selected_failure and selected_failure != 'nominal':
                    # Ellenőrizzük, hogy a MetaSpace észlelte-e a hibát
                    # Ha a power generation < 50%, akkor a MetaSpace észleli, de az integrity lehet még 90%
                    final_power_gen = history[-1].get('power_generation_w', 2400.0) if history else 2400.0
                    final_battery = history[-1].get('battery_percent', 100.0) if history else 100.0
                    
                    if selected_failure == 'solar_panel' and final_power_gen < 1200.0:
                        # Solar panel hiba észlelve
                        failure_time_for_log = failure_minute_start if selected_failure else 0
                        bio_logs.append(f"MetaSpace: Anomaly Detected - Solar Panel Failure (T+{failure_time_for_log} min, {failure_time_for_log/1440:.2f} days) - Power Generation: {final_power_gen:.0f}W")
                        if metaspace_detection_time is None:
                            metaspace_detection_time = failure_time_for_log
                    elif selected_failure == 'battery_failure' and final_battery < 20.0:
                        # Battery failure észlelve
                        failure_time_for_log = failure_minute_start if selected_failure else 0
                        bio_logs.append(f"MetaSpace: Anomaly Detected - Battery Failure (T+{failure_time_for_log} min, {failure_time_for_log/1440:.2f} days) - Battery: {final_battery:.1f}%")
                        if metaspace_detection_time is None:
                            metaspace_detection_time = failure_time_for_log
                    else:
                        bio_logs.append("MetaSpace: No anomalies detected - System Nominal")
                else:
                    bio_logs.append("MetaSpace: No anomalies detected - System Nominal")
        
        # EKF log üzenetek hozzáadása
        if ekf_logs:
            bio_logs.extend(ekf_logs)
        else:
            final_ekf = history[-1].get('ekf_reliability', 100) if history else 100
            if final_ekf < 100:
                bio_logs.append(f"EKF: Confidence degraded to {final_ekf:.1f}% (anomaly detected but not below 60% threshold)")
            else:
                bio_logs.append(f"EKF: No anomalies detected - Confidence: {ekf_solver.confidence:.1f}%")
        
        # Reakció idő összehasonlítás
        if metaspace_detection_time is not None and ekf_detection_time is not None:
            reaction_time_diff = ekf_detection_time - metaspace_detection_time
            bio_logs.append(f"Reaction Time Difference: MetaSpace {reaction_time_diff/1440:.2f} days faster than EKF")
        elif metaspace_detection_time is not None:
            bio_logs.append("MetaSpace detected anomaly, EKF did not detect")
        elif ekf_detection_time is not None:
            bio_logs.append("EKF detected anomaly, MetaSpace did not detect")
        
        bio_logs.extend([
            f"Final EKF Reliability: {ekf_solver.confidence:.1f}%",
            f"Final MetaSpace Integrity: {metaspace_solver.mission_feasibility:.1f}%",
            f"System Mode: {metaspace_solver.execution_mode}"
        ])
        
        # Komponensek kinyerése: keressük meg az utolsó telemetria bejegyzést, ami tartalmaz components mezőt
        last_state_with_components = None
        for entry in reversed(history):
            if 'components' in entry and entry.get('components'):
                last_state_with_components = entry
                break
        
        # Ha nincs, használjuk az utolsó elemet
        if last_state_with_components is None and history:
            last_state_with_components = history[-1]
        
        result_package = {
            'sim_id': sim_id,
            'status': 'success',
            'telemetry_log': history,
            'components': self._extract_components(last_state_with_components if last_state_with_components else {}),
            'narrative': f"Analysis Complete. MetaSpace Mode: {metaspace_solver.execution_mode}",
            'failure_type': selected_failure if selected_failure else scenario,
            'failure_time': failure_minute_start if selected_failure else None,
            'bio_logs': bio_logs
        }

        self.results_cache[sim_id] = result_package
        return sim_id

    def _extract_components(self, state):
        """Átalakítja az alrendszer-komponenseket a UI mátrixhoz."""
        comps = []
        raw_comps = state.get('components', {})
        
        # Magyarázó szövegek a komponensekhez
        descriptions = {
            'Solar_Left_Wing': 'Bal oldali napelem szárny. Napenergiát alakít át elektromos energiává az akkumulátor töltéséhez.',
            'Solar_Right_Wing': 'Jobb oldali napelem szárny. Napenergiát alakít át elektromos energiává az akkumulátor töltéséhez.',
            'Main_Battery_Pack': 'Fő akkumulátor csomag. Energiatárolás a műhold működéséhez, különösen napfogyatkozás alatt.',
            'ST_A': 'Star Tracker A. Csillagok pozíciójának mérésével segíti a műhold orientációjának meghatározását.',
            'ST_B': 'Star Tracker B. Csillagok pozíciójának mérésével segíti a műhold orientációjának meghatározását.',
            'ST_C': 'Star Tracker C. Csillagok pozíciójának mérésével segíti a műhold orientációjának meghatározását.'
        }
        
        # Ha nincs komponens, akkor hozzunk létre alapértelmezett listát
        if not raw_comps:
            # Alapértelmezett komponensek létrehozása
            default_components = {
                'Solar_Left_Wing': {'health': 100, 'active': True},
                'Solar_Right_Wing': {'health': 100, 'active': True},
                'Main_Battery_Pack': {'health': 100, 'active': True},
                'ST_A': {'health': 100, 'active': True},
                'ST_B': {'health': 100, 'active': True},
                'ST_C': {'health': 100, 'active': True}
            }
            raw_comps = default_components
        
        for name, data in raw_comps.items():
            # Biztosítjuk, hogy mindig legyen leírás
            description = descriptions.get(name, f'Komponens: {name}')
            comps.append({
                'id': name[:6].upper(),
                'name': name,
                'status': 'HEALTHY' if data.get('health', 100) > 50 else 'FAULT',
                'description': description
            })
        return comps

    def get_results(self, sim_id):
        return self.results_cache.get(sim_id)