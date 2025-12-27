import numpy as np
from .subsystems import EPSSubsystem, GNCSubsystem

class Landsat9Model:
    """
    MetaSpace v2.0 - Landsat-9 Digital Twin
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
        self.base_consumption = 450.0 # Watt
        
        # --- TELEMETRIA BUFFER ---
        self.last_state = {}

    def calculate_orbit_position(self, t_minutes):
        cycle_pos = (t_minutes % self.orbital_period) / self.orbital_period
        self.in_sunlight = cycle_pos < (1.0 - self.eclipse_ratio)
        return self.in_sunlight

    def inject_failure(self, failure_type):
        """
        Kívülről érkező hiba. Csak akkor fut le, ha érvényes hibatípust kap.
        """
        if not failure_type or failure_type == 'nominal':
            return

        print(f"[LANDSAT-9] Failure Injection Triggered: {failure_type}")
        
        if failure_type == 'solar_panel':
            self.eps.inject_solar_failure()
        elif failure_type == 'battery_failure':
            self.eps.inject_battery_failure()
        elif failure_type == 'imu_drift' or failure_type == 'gps_antenna':
            self.gnc.inject_failure(0)
        else:
            print(f"[LANDSAT-9] Unknown failure type: {failure_type}")

    def simulate_step(self, dt_minutes, current_failure=None):
        self.time_elapsed += dt_minutes
        
        is_sun = self.calculate_orbit_position(self.time_elapsed)
        sun_intensity = 1.0 if is_sun else 0.0

        # JAVÍTÁS: Csak akkor injektálunk hibát, ha nem NOMINAL a kérés
        if current_failure and current_failure != 'nominal':
            self.inject_failure(current_failure)

        # EPS ALRENDSZER FRISSÍTÉSE
        dt_hours = dt_minutes / 60.0
        eps_status = self.eps.update_energy_budget(
            sun_intensity=sun_intensity,
            power_consumption_watts=self.base_consumption,
            dt_hours=dt_hours
        )

        # GNC ALRENDSZER FRISSÍTÉSE
        true_orientation = 1.0 
        measured_orientation = self.gnc.get_verified_orientation(true_orientation)
        
        if measured_orientation is None:
            attitude_integrity = 0.0
        else:
            error = abs(measured_orientation - true_orientation)
            attitude_integrity = max(0.0, 100.0 - (error * 1000))

        # RÉSZLETES TELEMETRIA BŐVÍTÉS
        component_health = {}
        for panel in self.eps.solar_wings:
            component_health[panel.name] = {
                'health': panel.health, 
                'active': panel.is_active,
                'temp': panel.temperature
            }
        component_health[self.eps.battery.name] = {
            'health': self.eps.battery.health,
            'active': self.eps.battery.is_active,
            'charge': self.eps.battery.current_charge
        }
        for sensor in self.gnc.star_trackers:
            component_health[sensor.name] = {
                'health': sensor.health,
                'active': sensor.is_active,
                'faults': sensor.faults
            }

        telemetry = {
            'time': self.time_elapsed,
            'is_eclipse': not is_sun,
            'battery_percent': eps_status['battery_percent'],
            'power_generation_w': eps_status['generation'],
            'attitude_integrity': attitude_integrity,
            'active_sensors': self.gnc.active_sensor_count,
            'components': component_health,
            'system_status': 'NOMINAL' if eps_status['battery_percent'] > 20 and attitude_integrity > 90 else 'CRITICAL'
        }
        
        self.last_state = telemetry
        return telemetry

    def run_full_day_simulation(self):
        results = []
        minutes_per_day = 24 * 60
        dt = 1.0 
        for t in np.arange(0, minutes_per_day, dt):
            state = self.simulate_step(dt)
            results.append(state)
        return results