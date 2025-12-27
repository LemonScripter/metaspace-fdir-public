import random
import numpy as np

class BioComponent:
    """
    LEVEL 1: CELL LEVEL PROTECTION (Komponens szint)
    Minden hardver ősosztálya. 
    Képességek: Öndiagnózis, Csendes lekapcsolás (Silent Drop).
    """
    def __init__(self, name, component_type):
        self.name = name
        self.type = component_type
        self.health = 100.0          # 0-100%
        self.temperature = 20.0      # Celsius
        self.is_active = True        # Ha False, az egység izolálva van
        self.faults = []             # Hibanapló

    def self_diagnose(self):
        """
        Belső integritás ellenőrzése. Ez fut le minden ciklus előtt.
        """
        if not self.is_active:
            return False

        # 1. Hőmérséklet védelem (Thermal Cutoff)
        if self.temperature > 95.0:
            self.shutdown("CRITICAL_OVERHEAT")
            return False

        # 2. Hardver integritás (Véletlenszerű SEU - Single Event Upset szimuláció)
        # 0.001% esély per ciklus spontán bitflipre
        if random.random() < 0.00001:
            self.register_fault("SEU_BITFLIP_MEMORY")
            # Kisebb hiba nem öl, csak csökkenti a health-t

        # 3. Életerő ellenőrzés
        if self.health <= 0:
            self.shutdown("END_OF_LIFE")
            return False

        return True

    def register_fault(self, fault_code):
        if fault_code not in self.faults:
            self.faults.append(fault_code)
            self.health -= 15.0 # Jelentős sérülés

    def shutdown(self, reason):
        if self.is_active:
            self.is_active = False
            self.health = 0
            # Debug célból, ha látni akarod a konzolon:
            # print(f"[{self.name}] SHUTDOWN: {reason} (SILENT DROP ACTIVATED)")

    def force_fail(self, failure_type):
        """Külső hiba injektálása (pl. a szimulátorból)"""
        self.register_fault(failure_type)
        
        # --- JAVÍTÁS: .lower() használata a biztos találatért ---
        ft_lower = failure_type.lower()
        if "physics" in ft_lower or "break" in ft_lower or "fire" in ft_lower:
             self.shutdown(failure_type)

class SolarPanel(BioComponent):
    def __init__(self, name, area_m2):
        super().__init__(name, "POWER_GEN")
        self.area = area_m2
        self.efficiency = 0.30 # 30% hatásfok
    
    def get_power_output(self, sun_intensity):
        if not self.self_diagnose(): return 0.0
        # P = Intenzitás * Terület * Hatásfok
        # 1000 W/m2 a napállandó földközelben (felszínen, űrben 1361, de egyszerűsítünk)
        return max(0, sun_intensity * self.area * self.efficiency * 1000) 

class BatteryCell(BioComponent):
    def __init__(self, name, capacity_wh):
        super().__init__(name, "STORAGE")
        self.capacity_wh = capacity_wh
        self.current_charge = capacity_wh * 0.9 # 90%-on indul
    
    def update_charge(self, net_power, dt_hours):
        if not self.self_diagnose(): return 0.0
        
        # Töltés / Merítés
        self.current_charge += net_power * dt_hours
        
        # Fizikai korlátok (Level 1 Invariáns)
        if self.current_charge > self.capacity_wh:
            self.current_charge = self.capacity_wh
        if self.current_charge < 0:
            self.current_charge = 0
            self.register_fault("DEEP_DISCHARGE_DAMAGE")
            
        return self.current_charge

class StarTracker(BioComponent):
    def __init__(self, name):
        super().__init__(name, "SENSOR_ATTITUDE")
        self.accuracy = 0.999 # 99.9% pontosság
    
    def get_orientation(self, true_orientation):
        if not self.self_diagnose(): return None
        
        # Szimulált zaj
        if random.random() > self.accuracy:
            # Hiba esetén torz adatot ad
            return true_orientation * random.uniform(0.8, 1.2)
        return true_orientation