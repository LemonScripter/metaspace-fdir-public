import numpy as np
from .components import SolarPanel, BatteryCell, StarTracker

class GNCSubsystem:
    """
    Guidance, Navigation & Control Manager
    Kezeli a redundáns szenzorokat (Level 2 Voting).
    """
    def __init__(self):
        # 3 db Star Tracker a redundancia miatt
        self.star_trackers = [
            StarTracker("ST_A"),
            StarTracker("ST_B"),
            StarTracker("ST_C")
        ]
        self.active_sensor_count = 3

    def get_verified_orientation(self, true_val):
        """
        Lekérdezi az összes szenzort, és kiszűri a hibásakat.
        """
        readings = []
        valid_units = []

        # 1. Adatgyűjtés
        for st in self.star_trackers:
            val = st.get_orientation(true_val)
            if val is not None: # Ha nem volt Silent Drop
                readings.append(val)
                valid_units.append(st)
        
        self.active_sensor_count = len(readings)

        if self.active_sensor_count == 0:
            return None # VAKREPÜLÉS (Nincs működő szenzor)

        # 2. Level 2 Voting Logic (Egyszerűsített: Átlag és Szórás vizsgálat)
        # Ha valamelyik érték nagyon eltér az átlagtól, eldobjuk
        mean_val = np.mean(readings)
        clean_readings = []
        
        for val in readings:
            # Ha 10%-nál nagyobb az eltérés az átlagtól, gyanús
            if abs(val - mean_val) / (mean_val + 1e-9) < 0.1:
                clean_readings.append(val)
            else:
                # Ezt a szenzort megjelölhetnénk hibásnak
                pass

        if not clean_readings:
            return mean_val # Jobb híján

        return np.mean(clean_readings)

    def inject_failure(self, target_idx):
        """Szimulációs hiba injektálása"""
        if 0 <= target_idx < len(self.star_trackers):
            self.star_trackers[target_idx].force_fail("SENSOR_BLINDNESS")

class EPSSubsystem:
    """
    Electrical Power System Manager
    Kezeli a napelemeket és az akkumulátort.
    """
    def __init__(self):
        # Bal és Jobb oldali szárny
        self.solar_wings = [
            SolarPanel("Solar_Left_Wing", area_m2=4.0),
            SolarPanel("Solar_Right_Wing", area_m2=4.0)
        ]
        # Fő akkumulátor pakk
        self.battery = BatteryCell("Main_Battery_Pack", capacity_wh=4000)

    def update_energy_budget(self, sun_intensity, power_consumption_watts, dt_hours):
        """
        Kiszámolja a termelést és frissíti az akkut.
        """
        total_gen = 0.0
        
        # 1. Termelés összegzése a szárnyakról
        for panel in self.solar_wings:
            total_gen += panel.get_power_output(sun_intensity)

        # 2. Mérleg
        net_power = total_gen - power_consumption_watts
        
        # 3. Akku frissítés
        current_charge = self.battery.update_charge(net_power, dt_hours)
        
        return {
            'generation': total_gen,
            'consumption': power_consumption_watts,
            'battery_charge': current_charge,
            'battery_percent': (current_charge / self.battery.capacity_wh) * 100
        }

    def inject_solar_failure(self):
        # Törjük el a bal szárnyat
        self.solar_wings[0].force_fail("PHYSICAL_BREAK_METEOR")
    
    def inject_battery_failure(self):
        self.battery.force_fail("SHORT_CIRCUIT_FIRE")