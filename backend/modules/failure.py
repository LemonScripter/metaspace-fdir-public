import json
import numpy as np

class FailureInjector:
    """
    Felelős a hibák beinjektálásáért a fizikai modellbe.
    """
    def __init__(self, scenario_config):
        self.triggered = False
        
        # Config normalizálás
        if isinstance(scenario_config, str):
            self.config = {"failure_type": scenario_config}
        else:
            self.config = scenario_config

        self.f_type = self.config.get("failure_type", "nominal")
        
        # A hibanapot kívülről kapjuk a szimulátortól (randomizálva), 
        # vagy a configból, ha fix.
        self.target_day = self.config.get("failure_day", 10)

    def set_random_day(self, day):
        """A Simulator hívja meg, hogy véletlenszerűsítse a napot"""
        self.target_day = day

    def apply_failures(self, landsat_model, current_day):
        """Minden nap fut."""
        if current_day == self.target_day and not self.triggered:
            if self.f_type != "nominal":
                print(f"[FAILURE] >>> Injektálás: {self.f_type} (Nap: {current_day}) <<<")
                self._trigger_physics(landsat_model)
                self.triggered = True
            
    def _trigger_physics(self, model):
        """Itt rontjuk el tartósan a hardvert."""
        
        if self.f_type == "nominal":
            return 

        if self.f_type == "gps_antenna":
            # GPS antenna hiba: Óriási zaj és eltolódás
            model.gps_noise_factor = 20.0
            model.gps_bias = np.array([150.0, 150.0, -100.0]) # ~250m hiba
            
        elif self.f_type == "battery_failure":
            # Akku cella zárlat (Azonnali halál)
            model.battery_dead = True # Bekapcsoljuk a tartós hibát
            model.battery_level = 15.0 # Azonnali feszültségesés
            
        elif self.f_type == "solar_panel":
            # Napelem törés (Lassú halál)
            # A hatásfok 20%-ra esik -> Nem tudja visszatölteni a fogyasztást
            model.solar_efficiency = 0.2 
            
        elif self.f_type == "imu_drift":
            # IMU Drift (Lopakodó hiba)
            model.imu_drift_rate = 1.2 # Erős drift