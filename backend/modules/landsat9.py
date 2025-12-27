import numpy as np
from .subsystems import EPSSubsystem, GNCSubsystem

class Landsat9Model:
    """
    MetaSpace v2.0 - Landsat-9 Digital Twin
    
    Ez a modul a műhold "fizikai teste". 
    A v2.0 architektúrában már nem saját maga számolja az energiát vagy a navigációt,
    hanem dedikált alrendszereket (Bio-Organs) vezérel:
    - EPS (Electrical Power System)
    - GNC (Guidance, Navigation & Control)
    
    Fizikai paraméterek:
    - Tömeg: ~2700 kg
    - Pálya: 705 km (Napszinkron)
    - Keringési idő: ~99 perc
    """
    
    def __init__(self):
        # --- ALRENDSZEREK (Level 2: Subsystems) ---
        self.eps = EPSSubsystem() # Energiaellátás
        self.gnc = GNCSubsystem() # Navigáció és Irányítás
        
        # --- ORBITÁLIS FIZIKA (Constants) ---
        self.orbital_period = 99.0  # perc
        self.orbit_height = 705.0   # km
        self.velocity = 7.5         # km/s
        self.eclipse_ratio = 0.35   # A pálya 35%-a van árnyékban
        
        # --- ÁLLAPOTVÁLTOZÓK ---
        self.time_elapsed = 0.0     # Eltelt idő (perc)
        self.in_sunlight = True     # Napon vagyunk-e?
        self.base_consumption = 450.0 # Watt (Alapfogyasztás: fedélzeti számítógép + fűtés)
        
        # --- TELEMETRIA BUFFER ---
        self.last_state = {}

    def calculate_orbit_position(self, t_minutes):
        """
        Kiszámolja a műhold pozícióját a pályán, és meghatározza,
        hogy éppen a Föld árnyékában van-e (Eclipse).
        """
        # A ciklusban elfoglalt hely (0.0 - 1.0)
        cycle_pos = (t_minutes % self.orbital_period) / self.orbital_period
        
        # Landsat-9 napszinkron pályán van.
        # Feltételezzük, hogy a ciklus elején lép ki a napra.
        # 0.0 - 0.65: Napos oldal
        # 0.65 - 1.0: Árnyékos oldal (Eclipse)
        self.in_sunlight = cycle_pos < (1.0 - self.eclipse_ratio)
        
        return self.in_sunlight

    def inject_failure(self, failure_type):
        """
        Kívülről érkező hiba (Simulated Fault Injection).
        A hibát továbbítja az érintett alrendszernek.
        """
        print(f"[LANDSAT-9] Failure Injection Triggered: {failure_type}")
        
        if failure_type == 'solar_panel':
            # Fizikai behatás: Meteor vagy törmelék találat a bal szárnyon
            self.eps.inject_solar_failure()
            
        elif failure_type == 'battery_failure':
            # Termikus futás: Akkumulátor cella zárlat
            self.eps.inject_battery_failure()
            
        elif failure_type == 'imu_drift' or failure_type == 'gps_antenna':
            # Szenzor hiba: A GNC rendszer egyik érzékelőjét "megvakítjuk"
            # 0 = Az elsődleges Star Tracker vagy IMU
            self.gnc.inject_failure(0)
            
        else:
            print(f"[LANDSAT-9] Unknown failure type: {failure_type}")

    def simulate_step(self, dt_minutes, current_failure=None):
        """
        Egyetlen szimulációs lépés végrehajtása (dt_minutes időközzel).
        Ez a függvény hívja meg az alrendszerek update() metódusait.
        """
        self.time_elapsed += dt_minutes
        
        # 1. Környezeti hatások számítása
        is_sun = self.calculate_orbit_position(self.time_elapsed)
        sun_intensity = 1.0 if is_sun else 0.0

        # 2. Hiba injektálás (ha éppen most történik)
        if current_failure:
            self.inject_failure(current_failure)

        # 3. EPS ALRENDSZER FRISSÍTÉSE
        dt_hours = dt_minutes / 60.0
        eps_status = self.eps.update_energy_budget(
            sun_intensity=sun_intensity,
            power_consumption_watts=self.base_consumption,
            dt_hours=dt_hours
        )

        # 4. GNC ALRENDSZER FRISSÍTÉSE
        true_orientation = 1.0 
        measured_orientation = self.gnc.get_verified_orientation(true_orientation)
        
        if measured_orientation is None:
            attitude_integrity = 0.0
        else:
            error = abs(measured_orientation - true_orientation)
            attitude_integrity = max(0.0, 100.0 - (error * 1000))

        # 5. Adatok összeállítása (RÉSZLETES TELEMETRIA BŐVÍTÉS)
        # Itt gyűjtjük ki az egyes "sejtek" (komponensek) állapotát név szerint
        component_health = {}
        
        # EPS (Energia) komponensek lekérdezése
        for panel in self.eps.solar_wings:
            component_health[panel.name] = {
                'health': panel.health, 
                'active': panel.is_active,
                'temp': panel.temperature
            }
        # Akkumulátor hozzáadása
        component_health[self.eps.battery.name] = {
            'health': self.eps.battery.health,
            'active': self.eps.battery.is_active,
            'charge': self.eps.battery.current_charge
        }

        # GNC (Navigáció) komponensek lekérdezése
        for sensor in self.gnc.star_trackers:
            component_health[sensor.name] = {
                'health': sensor.health,
                'active': sensor.is_active,
                'faults': sensor.faults
            }

        telemetry = {
            'time': self.time_elapsed,
            'is_eclipse': not is_sun,
            
            # --- ÖSSZESÍTETT ADATOK (Grafikonhoz) ---
            'battery_percent': eps_status['battery_percent'],
            'power_generation_w': eps_status['generation'],
            'attitude_integrity': attitude_integrity,
            'active_sensors': self.gnc.active_sensor_count,
            
            # --- RÉSZLETES BONTÁS (A Grid nézethez) ---
            'components': component_health,  # <--- EZ AZ ÚJ KULCS!
            
            'system_status': 'NOMINAL' if eps_status['battery_percent'] > 20 and attitude_integrity > 90 else 'CRITICAL'
        }
        
        self.last_state = telemetry
        return telemetry

    def run_full_day_simulation(self):
        """
        Segédfüggvény teszteléshez
        """
        results = []
        minutes_per_day = 24 * 60
        dt = 1.0 
        
        for t in np.arange(0, minutes_per_day, dt):
            state = self.simulate_step(dt)
            results.append(state)
            
        return results