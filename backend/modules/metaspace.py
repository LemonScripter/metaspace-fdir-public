import numpy as np

class MetaSpaceSimulator:
    def __init__(self, landsat9_model):
        self.landsat9 = landsat9_model
        
        # Komponens egészségi állapot (2=OK, 1=Degradált, 0=Hiba)
        self.health = {
            'gps': 2,
            'imu': 2,
            'thermal': 2,
            'power': 2,
            'comm': 2
        }
        
        # Kimeneti változók
        self.mission_feasibility = 100
        self.execution_mode = 'FULL_MISSION'
        self.scenes_today = 0
        self.data_loss_today = 0
        self.anomaly_detected = False
        self.detection_latency = 0
        self.decision_latency = 0
        
        # Belső állapot a detektáláshoz
        self._last_check_status = "NOMINAL"

    def update(self):
        """A MetaSpace logikai ciklus futtatása"""
        
        # 1. Level 1: Modul szintű ellenőrzés (Itt olvassuk ki a hibákat!)
        self._level1_assessment()
        
        # 2. Level 0: Master Arbiter döntés
        self._level0_arbiter()
        
        # 3. Végrehajtási mód kiválasztása
        self._adapt_execution()
        
        # 4. Adatgyűjtés szimulálása a döntés alapján
        # MetaSpace: Gyorsan reagál, leállítja az adatgyűjtést, ha hiba van
        # Ezzel szemben az EKF tovább gyűjt rossz adatot (fölösleges/költséges fotók)
        if self.execution_mode == 'FULL_MISSION':
            self.scenes_today = 700
            self.data_loss_today = 0
        elif self.execution_mode == 'PARTIAL_MISSION':
            # Csökkentett mód
            self.scenes_today = int(700 * (self.mission_feasibility / 100))
            self.data_loss_today = 700 - self.scenes_today
        else:
            # SAFE_MODE vagy EMERGENCY -> Nincs adatgyűjtés (Védelem)
            # MetaSpace: Leállítja az adatgyűjtést, ha hiba van (nem gyűjt fölösleges fotókat)
            self.scenes_today = 0
            self.data_loss_today = 0 # Nem "veszteség", hanem "megmentett selejt"
            
    def _level1_assessment(self):
        """
        A szenzorok és alrendszerek ellenőrzése.
        Itt kötjük össze a fizikai modellt (landsat9) a MetaSpace logikával.
        """
        # --- AKKUMULÁTOR ELLENŐRZÉS (Energy Invariant) ---
        # REÁLIS: A MetaSpace azonnal észleli az energia invariáns megsértését
        # - Akku < 20%: Kritikus (FAULT)
        # - Akku < 40%: Degradált (DEGRADED)
        # - Power generation < 50%: Solar panel hiba (FAULT vagy DEGRADED)
        if self.landsat9.battery_level < 20.0:
            self.health['power'] = 0 # FAULT (Kritikus)
        elif self.landsat9.battery_level < 40.0:
            self.health['power'] = 1 # DEGRADED
        elif hasattr(self.landsat9, 'power_generation_w') and self.landsat9.power_generation_w <= 1200.0:
            # Solar panel hiba: power generation <= 50% (normál: ~2400W, hiba esetén: <=1200W)
            # A MetaSpace azonnal észleli az energia invariáns megsértését
            # KRITIKUS: A solar panel hiba azonnal FAULT-ot jelent, mert nem tudja visszatölteni az akkut
            # Ez hosszú távon Dead Bus állapotot okozhat
            self.health['power'] = 0 # FAULT (Kritikus - Solar panel hiba)
        else:
            self.health['power'] = 2 # NOMINAL

        # --- GPS ELLENŐRZÉS (Spatial Invariant) ---
        # A MetaSpace a "maradék" (residual) hibát látja a modellek között
        if self.landsat9.gps_error > 50.0:
            self.health['gps'] = 0 # FAULT
        else:
            self.health['gps'] = 2

        # --- IMU ELLENŐRZÉS (Temporal Invariant) ---
        if self.landsat9.imu_accumulated_error > 0.5:
            self.health['imu'] = 0 # FAULT
        elif self.landsat9.imu_accumulated_error > 0.2:
            self.health['imu'] = 1 # DEGRADED
        else:
            self.health['imu'] = 2

    def _level0_arbiter(self):
        """
        A 'Master Arbiter' kiszámolja a teljes küldetés megvalósíthatóságát.
        """
        # Súlyozott pontszámítás
        nav_points = 0
        nav_points += 10 if self.health['gps'] == 2 else 0
        nav_points += 5 if self.health['imu'] == 2 else 0
        nav_points += 5 # Radar (feltételezzük, hogy jó)
        
        power_points = 20 if self.health['power'] == 2 else (10 if self.health['power'] == 1 else 0)
        
        # Ha az akku kritikus (0), akkor a power pont 0, ami azonnal lehúzza az egészet
        
        obs_points = 30 # Kamerák
        prop_points = 15 # Hajtómű
        comm_points = 15 # Kommunikáció
        
        # Összegzés
        total_score = nav_points + obs_points + power_points + prop_points + comm_points
        
        # KRITIKUS VÉDŐHÁLÓ: Ha bármely létfontosságú rendszer 0 (FAULT),
        # a MetaSpace felülbírálja a matekot és 0%-ra állítja a biztonságot.
        if self.health['power'] == 0 or self.health['gps'] == 0 or self.health['imu'] == 0:
            self.mission_feasibility = 0
            self.anomaly_detected = True
            self.detection_latency = 50 # ms (FPGA sebesség)
        else:
            self.mission_feasibility = total_score
            self.anomaly_detected = False

    def _adapt_execution(self):
        """Döntés a feasibility alapján"""
        if self.mission_feasibility >= 90:
            self.execution_mode = 'FULL_MISSION'
        elif self.mission_feasibility >= 40:
            self.execution_mode = 'PARTIAL_MISSION'
        else:
            self.execution_mode = 'SAFE_MODE'