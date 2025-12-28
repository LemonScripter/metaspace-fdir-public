import numpy as np
import random
from typing import Dict, Any, Optional

# EKF File Manager import
try:
    from backend.modules.ekf_file_manager import EKFFileManager
except ImportError:
    try:
        from modules.ekf_file_manager import EKFFileManager
    except ImportError:
        EKFFileManager = None

class EKFSimulator:
    """
    Hagyományos Extended Kalman Filter (a 'régi' technológia).
    """
    def __init__(self, landsat_model):
        self.model = landsat_model
        
        # Állapotbecslés (dummy)
        self.state = np.zeros(15)
        self.covariance = np.eye(15) * 10.0
        
        self.confidence = 100.0
        self.anomaly_detected = False
        self.detection_latency = 0
        
        # Metrikák
        self.scenes_today = 0
        self.data_loss_today = 0
        
        # EKF File Manager inicializálása (3 .ekf fájl kezelés)
        self.ekf_file_manager = EKFFileManager() if EKFFileManager is not None else None
        self.mission_day = 0  # Mission day counter

    def update(self):
        """
        EKF frissítési ciklus.
        A probléma: Az EKF a *szenzorokra* figyel, nem az akkumulátorra.
        Ha az akku lemerül, az EKF gyakran még "jónak" látja a navigációt,
        ezért engedi tovább a működést -> Dead Bus.
        
        REÁLIS VISELKEDÉS:
        - Solar panel hiba → akku lassan lemerül → GPS timeout (< 10%) → EKF lassan reagál
        - Battery failure → akku azonnal lemerül → GPS timeout → EKF lassan reagál
        - GPS antenna hiba → rossz GPS adat → EKF lassan reagál (heurisztikus próbálkozás)
        - IMU drift → fokozatos navigációs hiba → EKF lassan reagál
        """
        
        # 0. Először frissítjük a modellt (hogy a gps_error létezzen)
        # Egy rövid időlépés szimulálása
        try:
            self.model.simulate_step(0.1)  # 0.1 perc szimuláció
        except Exception as e:
            # Ha nem sikerül, folytatjuk, de logoljuk a hibát
            print(f"[EKF] Warning: simulate_step failed: {e}")
            pass
        
        # 0.5. Időbeli degradáció (wear and tear) - CSAK navigation-plan szimulációhoz
        # REALISZTIKUS: Normál működésben (nincs hiba) a confidence stabil marad (100%)
        # Fontos: Ez CSAK akkor fut le, ha van landsat_model (navigation-plan szimuláció)
        # A v3_fractal_sim NEM használ EKF-et, így NEM érinti!
        # Degradáció csak akkor, ha:
        # 1. Van valós komponens hiba (GPS, IMU, stb.)
        # 2. Vagy időbeli kopás (wear and tear) - de csak hosszú távon
        # Jelenleg: Nincs automatikus degradáció normál működésben
        # (A degradáció csak valós hibák esetén történik, amit a GPS/IMU észlel)
        
        # 1. Szenzor adatok lekérése
        gps = self.model.get_gps_measurement()
        
        # 2. Hiba logika (Szimulált EKF viselkedés)
        # REÁLIS: Ha az akku < 10%, a GPS jel eltűnik (nincs elég energia)
        # Az EKF ezt észleli, de lassan reagál (valószínűségszámítás, átlagolás)
        if gps is None:
            # GPS Timeout - Ezt észreveszi, de lassan
            # Reálisan: 1-2 nap alatt észleli a GPS timeout-ot
            # Heurisztikusan próbálja visszaállítani a kapcsolatot
            self.confidence -= 2.0  # Lassan csökken (átlagolva)
        else:
            # GPS van. Ha az akksi halott, az EKF ezt NEM látja a GPS jelben!
            # Ezért a confidence marad 100%, amíg a feszültség el nem tűnik teljesen.
            
            # Csak a GPS hibát venné észre, de azt is lassan (átlagolva)
            # GPS antenna hiba esetén: rossz adatot kap, heurisztikusan próbálja visszaterelni
            # Lassan csökken a bizalom (valószínűségszámítás, tehetetlenség)
            gps_error = getattr(self.model, 'gps_error', 0.0)
            if gps_error > 50.0:
                # Lassan csökken a bizalom (szimulálva a tehetetlenséget és heurisztikus próbálkozást)
                # Minél nagyobb a GPS hiba, annál gyorsabban csökken
                # De még mindig lassan (EKF jellemző: heurisztikus, valószínűségszámítás)
                # Az EKF heurisztikusan próbálja visszaterelni a műholdat, de lassan
                error_factor = min(2.0, (gps_error - 50.0) / 25.0)
                self.confidence -= (1.5 + error_factor)  # Lassabban csökken
            else:
                # Nincs hiba, vagy kicsi hiba -> confidence stabil marad
                # REALISZTIKUS: Normál működésben a confidence nem növekszik, csak degradáció miatt csökken
                # Csak akkor növekszik, ha valódi javulás van (pl. hiba után recovery)
                # Jelenleg: stabil marad (degradáció miatt már csökkent)
                pass  # Confidence nem változik normál működésben
        
        # Határolás
        self.confidence = max(0.0, min(100.0, self.confidence))
        
        # 3. Döntés
        # Az EKF csak akkor jelez hibát, ha nagyon biztos benne (60% alatt)
        if self.confidence < 60.0:
            self.anomaly_detected = True
            # Dinamikus detection latency számítás a hiba típusa alapján
            # Tudományos alap: EKF valószínűségszámítási módszere miatt lassan reagál
            self.detection_latency = self._calculate_detection_latency()
        else:
            self.anomaly_detected = False
            
        # 4. Adatgyűjtés (A végzetes hiba: Ha nincs hiba jelezve, gyűjtünk!)
        # Ha az akksi 18%, de az EKF 100%-ot mond, akkor gyűjtünk -> Selejt/Veszély
        # GPS antenna hiba esetén: Az EKF rossz adatot kap, de lassan reagál
        # Közben tovább gyűjt adatot (fölösleges/költséges fotók) -> data_loss nő
        if not self.anomaly_detected:
            # Ha nincs hiba jelezve, de van GPS hiba, akkor rossz adatot gyűjtünk
            gps_error = getattr(self.model, 'gps_error', 0.0)
            if gps_error > 50.0:
                # GPS hiba van, de az EKF még nem észlelte -> rossz adatot gyűjtünk
                # A data_loss növekszik, mert rossz minőségű adat készül
                self.scenes_today = 700  # Tovább gyűjt (rossz adat)
                # A data_loss arányos a GPS hibával (minél nagyobb a hiba, annál rosszabb az adat)
                data_quality = max(0.0, 1.0 - (gps_error / 100.0))
                self.data_loss_today = int(700 * (1.0 - data_quality))  # Fölösleges/költséges fotók
            else:
                self.scenes_today = 700
                self.data_loss_today = 0 # Látszólag minden oké (ez a veszély)
        else:
            self.scenes_today = 0
            self.data_loss_today = 700
        
        # 5. EKF végrehajtási fájlok mentése (3 .ekf fájl)
        # Automatikusan mentjük minden update ciklusban
        try:
            self.save_ekf_execution_files()
        except Exception as e:
            # Ha a fájl mentés sikertelen, folytatjuk (nem kritikus)
            pass
    
    def _calculate_detection_latency(self):
        """
        Dinamikus detection latency számítás a hiba típusa alapján.
        Tudományos alap: EKF valószínűségszámítási módszere miatt lassan reagál.
        
        Returns:
            int: Detection latency percben
        """
        gps = self.model.get_gps_measurement()
        
        # GPS timeout (akku < 10%): 1-2 nap (1440-2880 perc)
        # Az EKF lassan észleli, mert csak a GPS jel hiányát látja
        if gps is None:
            # 1-2 nap közötti véletlenszerű érték
            return random.randint(1440, 2880)  # 1-2 nap
        
        # GPS error (GPS antenna hiba vagy spoofing): 0.5-2 nap (720-2880 perc)
        # Az EKF heurisztikusan próbálja korrigálni, de lassan reagál
        gps_error = getattr(self.model, 'gps_error', 0.0)
        if gps_error > 50.0:
            # Minél nagyobb a hiba, annál gyorsabban észleli (de még mindig lassan)
            if gps_error > 80.0:
                # Nagy hiba: 0.5-1 nap
                return random.randint(720, 1440)
            else:
                # Közepes hiba: 1-2 nap
                return random.randint(1440, 2880)
        
        # IMU drift: 2-5 nap (2880-7200 perc)
        # Fokozatos hiba, az EKF lassan észleli
        if hasattr(self.model, 'imu_accumulated_error') and self.model.imu_accumulated_error > 0.2:
            # Minél nagyobb a drift, annál gyorsabban észleli
            if self.model.imu_accumulated_error > 0.5:
                # Nagy drift: 2-3 nap
                return random.randint(2880, 4320)
            else:
                # Közepes drift: 3-5 nap
                return random.randint(4320, 7200)
        
        # Alapértelmezett: 2-3 nap (ha nem tudjuk meghatározni a hiba típusát)
        return random.randint(2880, 4320)
    
    def generate_complete_ekf_sequence(self) -> Dict[str, Any]:
        """
        3 szintű EKF adatok generálása (hasonlóan a bio-kódokhoz).
        
        Returns:
            Dictionary 3 szintű EKF adatokkal (level1, level2, level3)
        """
        # LEVEL 1: Sensor-level EKF adatok
        level1_data = self._generate_level1_ekf()
        
        # LEVEL 2: Subsystem-level EKF adatok
        level2_data = self._generate_level2_ekf()
        
        # LEVEL 3: Mission-level EKF adatok
        level3_data = self._generate_level3_ekf()
        
        return {
            "level1": level1_data,
            "level2": level2_data,
            "level3": level3_data
        }
    
    def _generate_level1_ekf(self) -> Dict[str, Any]:
        """
        Level 1: Sensor-level EKF adatok.
        GPS, IMU, Star Tracker measurements + state estimates.
        """
        sensors = {}
        
        # GPS sensor
        gps_measurement = self.model.get_gps_measurement()
        if gps_measurement is not None:
            gps_pos = gps_measurement[:3] if isinstance(gps_measurement, np.ndarray) else [0.0, 0.0, 0.0]
            sensors["GPS"] = {
                "measurement": np.linalg.norm(gps_pos) if isinstance(gps_pos, np.ndarray) else 0.0,
                "state_estimate": self.state[0] if len(self.state) > 0 else 0.0,
                "covariance": float(self.covariance[0, 0]) if self.covariance.shape[0] > 0 else 0.0,
                "confidence": self.confidence
            }
        else:
            sensors["GPS"] = {
                "measurement": 0.0,
                "state_estimate": self.state[0] if len(self.state) > 0 else 0.0,
                "covariance": float(self.covariance[0, 0]) if self.covariance.shape[0] > 0 else 0.0,
                "confidence": self.confidence
            }
        
        # IMU sensor (simulated)
        sensors["IMU"] = {
            "measurement": 0.0,  # IMU measurement (simulated)
            "state_estimate": self.state[3] if len(self.state) > 3 else 0.0,
            "covariance": float(self.covariance[3, 3]) if self.covariance.shape[0] > 3 else 0.0,
            "confidence": self.confidence * 0.9  # IMU typically less reliable than GPS
        }
        
        # Star Tracker A
        sensors["STAR_TRACKER_A"] = {
            "measurement": 0.0,  # Star tracker measurement (simulated)
            "state_estimate": self.state[6] if len(self.state) > 6 else 0.0,
            "covariance": float(self.covariance[6, 6]) if self.covariance.shape[0] > 6 else 0.0,
            "confidence": self.confidence * 0.95
        }
        
        # Star Tracker B
        sensors["STAR_TRACKER_B"] = {
            "measurement": 0.0,  # Star tracker measurement (simulated)
            "state_estimate": self.state[7] if len(self.state) > 7 else 0.0,
            "covariance": float(self.covariance[7, 7]) if self.covariance.shape[0] > 7 else 0.0,
            "confidence": self.confidence * 0.95
        }
        
        return {
            "sensors": sensors
        }
    
    def _generate_level2_ekf(self) -> Dict[str, Any]:
        """
        Level 2: Subsystem-level EKF adatok.
        Navigation, Power, Payload, Comm subsystem health + aggregated state.
        """
        subsystems = {}
        
        # Navigation subsystem (GPS + IMU + Star Trackers)
        nav_health = self.confidence  # Navigation health = EKF confidence
        subsystems["navigation"] = {
            "health": nav_health,
            "state_vector": self.state.copy(),
            "covariance_trace": float(np.trace(self.covariance))
        }
        
        # Power subsystem (simulated - EKF doesn't directly monitor power)
        # EKF typically doesn't monitor power, so we use a default value
        power_health = 100.0 if not self.anomaly_detected else 50.0
        subsystems["power"] = {
            "health": power_health,
            "state_vector": np.zeros(15),
            "covariance_trace": 0.0
        }
        
        # Payload subsystem (simulated)
        payload_health = 100.0 if not self.anomaly_detected else 0.0
        subsystems["payload"] = {
            "health": payload_health,
            "state_vector": np.zeros(15),
            "covariance_trace": 0.0
        }
        
        # Communication subsystem (simulated)
        comm_health = 100.0 if not self.anomaly_detected else 50.0
        subsystems["comm"] = {
            "health": comm_health,
            "state_vector": np.zeros(15),
            "covariance_trace": 0.0
        }
        
        return {
            "subsystems": subsystems
        }
    
    def _generate_level3_ekf(self) -> Dict[str, Any]:
        """
        Level 3: Mission-level EKF adatok.
        Mission feasibility, anomaly detection, decision.
        """
        # Feasibility = confidence (EKF alapú)
        feasibility = self.confidence
        
        # Decision logic (EKF alapú)
        if self.anomaly_detected:
            if self.confidence < 30.0:
                decision = "EMERGENCY_HALT"
            elif self.confidence < 50.0:
                decision = "SAFE_MODE"
            else:
                decision = "REDUCE_OPERATIONS"
        else:
            if self.confidence >= 90.0:
                decision = "CONTINUE_NOMINAL"
            elif self.confidence >= 70.0:
                decision = "CONTINUE_WITH_MONITORING"
            else:
                decision = "CONTINUE_WITH_MONITORING"
        
        return {
            "feasibility": feasibility,
            "anomaly_detected": self.anomaly_detected,
            "detection_latency": self.detection_latency,
            "confidence": self.confidence,
            "decision": decision,
            "scenes_today": self.scenes_today,
            "data_loss_today": self.data_loss_today
        }
    
    def save_ekf_execution_files(self, mission_day: Optional[int] = None) -> Dict[str, Any]:
        """
        EKF végrehajtási fájlok mentése (3 .ekf fájl).
        
        Args:
            mission_day: Mission day (ha None, akkor self.mission_day)
        
        Returns:
            Dictionary fájl elérési utakkal
        """
        if mission_day is None:
            mission_day = self.mission_day
        
        if self.ekf_file_manager is None:
            return {}
        
        # EKF adatok generálása
        ekf_data = self.generate_complete_ekf_sequence()
        
        # Fájlok mentése
        try:
            file_paths = self.ekf_file_manager.save_ekf_files(
                ekf_data,
                mission_day=mission_day
            )
            return {
                "file_paths": file_paths,
                "ekf_data": ekf_data
            }
        except Exception as e:
            print(f"[EKF FILES] Warning: Failed to save EKF execution files: {e}")
            return {}