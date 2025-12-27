import sys
import os
import unittest

# Beállítjuk az útvonalat, hogy elérjük a backend modulokat
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.modules.landsat9 import Landsat9Model

class TestMetaSpacePhysics(unittest.TestCase):
    """
    METASPACE v2.0 PHYSICS VERIFICATION SUITE
    Ez a teszt közvetlenül a fizikai motort vizsgálja, UI nélkül.
    """

    def setUp(self):
        print("\n----------------------------------------------------------------------")
        print(f"TEST: {self._testMethodName}")
        self.satellite = Landsat9Model()

    def test_01_solar_panel_physics(self):
        """
        TESZT 1: Napelem fizika ellenőrzése
        Ha eltörjük a bal szárnyat, a termelésnek CSÖKKENNIE kell,
        de nem lehet nulla (mert a jobb szárny még ép).
        """
        # 1. Alapállapot (Napon vagyunk)
        nominal_power = self.satellite.eps.update_energy_budget(1.0, 500, 1.0)['generation']
        print(f"   > Nominal Power Output: {nominal_power:.2f} W")

        # 2. Hiba injektálása (Bal szárny törés)
        print("   > INJECTING FAILURE: Solar Panel Breakage...")
        self.satellite.inject_failure('solar_panel')

        # 3. Új mérés
        damaged_power = self.satellite.eps.update_energy_budget(1.0, 500, 1.0)['generation']
        print(f"   > Damaged Power Output: {damaged_power:.2f} W")

        # ELLENŐRZÉS (Asserts)
        # A. A teljesítménynek csökkennie kellett
        self.assertLess(damaged_power, nominal_power, "HIBA: A napelem törés nem csökkentette a termelést!")
        
        # B. A teljesítmény nem lehet 0 (mert a jobb szárny működik)
        self.assertGreater(damaged_power, 0, "HIBA: A jobb szárnynak még termelnie kéne!")
        
        # C. A bal szárnynak inaktívnak vagy sérültnek kell lennie
        left_wing = self.satellite.eps.solar_wings[0]
        print(f"   > Left Wing Status: Health={left_wing.health}%, Active={left_wing.is_active}")
        self.assertTrue(left_wing.health < 100 or not left_wing.is_active, "HIBA: A bal szárny sértetlen maradt!")

    def test_02_battery_drain_logic(self):
        """
        TESZT 2: Akkumulátor merülés
        Ha árnyékban vagyunk (Eclipse), az akkunak merülnie KELL.
        """
        # 1. Árnyék szimuláció (Sun Intensity = 0)
        # Fogyasztás: 500W, Idő: 1 óra
        initial_charge = self.satellite.eps.battery.current_charge
        print(f"   > Initial Charge: {initial_charge:.2f} Wh")
        
        self.satellite.eps.update_energy_budget(sun_intensity=0.0, power_consumption_watts=500.0, dt_hours=1.0)
        
        final_charge = self.satellite.eps.battery.current_charge
        print(f"   > Final Charge after 1h eclipse: {final_charge:.2f} Wh")
        
        # ELLENŐRZÉS
        expected_drain = 500.0 * 1.0 # 500 Wh
        measured_drain = initial_charge - final_charge
        
        # Kis hibatűréssel (floating point error)
        self.assertAlmostEqual(measured_drain, expected_drain, delta=1.0, 
                               msg=f"HIBA: Nem megfelelő merülés! Elvárt: {expected_drain}, Mért: {measured_drain}")

    def test_03_isolation_mechanism(self):
        """
        TESZT 3: Bio-Architektúra Izoláció (Sejt védelem)
        Ha egy komponenst 'megölünk' (Health=0), az Active flag-nek False-ra kell váltania.
        """
        target_sensor = self.satellite.gnc.star_trackers[0]
        print(f"   > Targeting Sensor: {target_sensor.name}")
        
        # Erőszakos halál
        target_sensor.health = -10
        target_sensor.self_diagnose() # Futtatjuk a belső ellenőrzést
        
        print(f"   > Post-Mortem Status: Active={target_sensor.is_active}")
        
        # ELLENŐRZÉS
        self.assertFalse(target_sensor.is_active, "HIBA: A halott szenzor még mindig aktív!")

if __name__ == '__main__':
    print("=== METASPACE v2.0 CORE VERIFICATION RUN ===")
    unittest.main(verbosity=0)