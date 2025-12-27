import numpy as np
import random

class Landsat9Model:
    """
    Landsat-9 fizikai szimulátor (A Valóság).
    Ez a modul a fizikai törvényeket szimulálja.
    """
    def __init__(self):
        # Orbitális paraméterek
        self.time_step = 0
        self.orbital_period = 99 * 60 
        
        # Fizikai állapot
        self.battery_level = 100.0 # %
        self.position = np.array([705000.0, 0.0, 0.0]) 
        self.velocity = np.array([0.0, 7500.0, 0.0]) 
        
        # --- HARDVER ÁLLAPOTOK (A Failure Injector ezeket rontja el) ---
        self.gps_bias = np.zeros(3)
        self.gps_noise_factor = 1.0
        self.gps_timeout = False
        
        self.imu_bias = np.zeros(3)
        self.imu_drift_rate = 0.0
        
        self.battery_dead = False        # Ha igaz, az akku nem tárol áramot
        self.solar_efficiency = 1.0      # 1.0 = 100%, 0.0 = Törött napelem
        
        # Publikus metrikák (Resetelve)
        self.gps_error = 0.0 
        self.imu_accumulated_error = 0.0 

    def step(self, dt=1.0):
        """
        RÖVID IDŐTÁVÚ LÉPÉS (1 másodperc).
        Ezt használjuk a mozgáshoz, de az energiafogyasztást 
        átraktuk a simulate_day-be a pontosabb mérlegszámításért.
        """
        self.time_step += dt
        
        # 1. Mozgás (Keringés)
        angle = (self.time_step / self.orbital_period) * 2 * np.pi
        r = 705000.0 
        self.position = np.array([
            r * np.cos(angle),
            r * np.sin(angle),
            0.0
        ])
        
        # Megjegyzés: Az akku töltést/merítést kivettük innen és átraktuk
        # a simulate_day()-be, hogy a napelem hiba (solar_efficiency)
        # hatása drasztikusabb legyen napi szinten.

    def simulate_day(self):
        """
        EGY TELJES NAP SZIMULÁCIÓJA (Energy Budgeting).
        Ez a függvény felelős azért, hogy a napelem hiba látható legyen.
        """
        # Előretekerjük az időt egy nappal
        self.time_step += 86400 
        
        # 1. ENERGIA RENDSZER (A kritikus javítás)
        if self.battery_dead:
            # Ha az akku cellazárlatos, a kapacitás azonnal leesik és ott is marad
            self.battery_level = 15.0 
        else:
            # Napi energiamérleg számítás
            # Töltés: Névlegesen +50% kapacitás naponta (ha a napelem ép)
            # Ha solar_efficiency = 0.2 (törött), akkor csak +10% jön be!
            daily_production = 50.0 * self.solar_efficiency
            
            # Fogyasztás: A műhold napi alapfogyasztása -40% kapacitás
            daily_consumption = 40.0
            
            # Nettó változás
            net_change = daily_production - daily_consumption
            
            # Akku szint frissítése (0 és 100% között)
            self.battery_level = max(0.0, min(100.0, self.battery_level + net_change))

        # 2. IMU DRIFT (Napi akkumuláció)
        if self.imu_drift_rate > 0:
            # A drift mértéke naponta adódik össze
            daily_drift = np.random.normal(0.5, 0.1, 3) * self.imu_drift_rate
            self.imu_bias += daily_drift
            self.imu_accumulated_error = np.linalg.norm(self.imu_bias)

    def get_gps_measurement(self):
        """GPS mérés generálása"""
        if self.gps_timeout:
            self.gps_error = 9999.0
            return None 
            
        noise = np.random.normal(0, 5.0, 3) * self.gps_noise_factor
        measured_pos = self.position + noise + self.gps_bias
        
        # Valós hiba kiszámítása (hogy a szimulátor tudja)
        self.gps_error = np.linalg.norm(measured_pos - self.position)
        
        return measured_pos

    def get_imu_measurement(self):
        """IMU mérés generálása"""
        acc_true = np.array([0.0, 0.0, 9.81]) # Gravitáció helyett gyorsulás
        noise = np.random.normal(0, 0.05, 3)
        return acc_true + noise + self.imu_bias

    def get_telemetry(self):
        """Adatcsomag a rendszereknek"""
        self.get_gps_measurement() # Frissíti a gps_error-t
            
        return {
            "gps_position_error": self.gps_error,
            "imu_drift_error": self.imu_accumulated_error,
            "battery_level": self.battery_level,
            "timestamp_ms": int(self.time_step * 1000)
        }