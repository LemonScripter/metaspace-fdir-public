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

class KalmanFilter3D:
    """
    Standard Linear Kalman Filter for 3D Position & Velocity estimation.
    State Vector (x): [pos_x, pos_y, pos_z, vel_x, vel_y, vel_z]
    """
    def __init__(self, dt=1.0, process_noise=0.1, measurement_noise=10.0):
        self.dt = dt
        
        # 1. State Vector [x, y, z, vx, vy, vz]
        self.x = np.zeros(6)
        
        # 2. State Transition Matrix (F) - Constant Velocity Model
        # x_new = x_old + vx * dt
        self.F = np.eye(6)
        self.F[0, 3] = dt
        self.F[1, 4] = dt
        self.F[2, 5] = dt
        
        # 3. Measurement Matrix (H)
        # We only measure Position (x, y, z), not Velocity
        self.H = np.zeros((3, 6))
        self.H[0, 0] = 1
        self.H[1, 1] = 1
        self.H[2, 2] = 1
        
        # 4. Covariance Matrix (P) - Initial uncertainty
        self.P = np.eye(6) * 100.0
        
        # 5. Process Noise Covariance (Q) - Uncertainty in the physics model
        self.Q = np.eye(6) * process_noise
        
        # 6. Measurement Noise Covariance (R) - Sensor noise
        self.R = np.eye(3) * measurement_noise

    def predict(self):
        """
        Prediction Step: Project the state ahead based on physics (F).
        Increases uncertainty (P).
        """
        # x = F * x
        self.x = np.dot(self.F, self.x)
        # P = F * P * F^T + Q
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q

    def update(self, measurement):
        """
        Correction Step: Update with new measurement.
        Decreases uncertainty (P).
        """
        z = np.array(measurement)
        
        # Innovation (Residual): y = z - H * x
        y = z - np.dot(self.H, self.x)
        
        # Innovation Covariance: S = H * P * H^T + R
        S = np.dot(np.dot(self.H, self.P), self.H.T) + self.R
        
        # Optimal Kalman Gain: K = P * H^T * inv(S)
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        
        # Update State: x = x + K * y
        self.x = self.x + np.dot(K, y)
        
        # Update Covariance: P = (I - K * H) * P
        I = np.eye(6)
        self.P = np.dot((I - np.dot(K, self.H)), self.P)

    def get_confidence(self):
        """
        Calculate confidence based on the trace of Covariance Matrix (P).
        Lower trace = Higher confidence.
        """
        # Trace represents the sum of variances (uncertainty)
        trace = np.trace(self.P)
        
        # Map trace to 0-100% scale
        # Example: Trace < 10 -> 100%, Trace > 1000 -> 0%
        # Using an exponential decay function for realistic falloff
        # confidence = 100 * exp(-k * trace)
        
        # Tuning parameter: determines how fast confidence drops with uncertainty
        k = 0.005 
        confidence = 100.0 * np.exp(-k * trace)
        return max(0.0, min(100.0, confidence))

class EKFSimulator:
    """
    Real Mathematical EKF Implementation (Steel-man argument).
    
    Demonstrates:
    1. Precise navigation when sensors work.
    2. "Battery Blindness": The math works perfectly even if the battery is dying.
    3. Natural degradation: Confidence drops mathematically when data is lost.
    """
    def __init__(self, landsat_model):
        self.model = landsat_model
        
        # Initialize the real Mathematical Filter
        # dt=0.1 min (6 seconds), matches simulate_step
        self.kf = KalmanFilter3D(dt=0.1, process_noise=0.1, measurement_noise=50.0)
        
        # Initial State
        self.confidence = 100.0
        self.anomaly_detected = False
        self.detection_latency = 0
        
        # Metrikák
        self.scenes_today = 0
        self.data_loss_today = 0
        
        self.ekf_file_manager = EKFFileManager() if EKFFileManager is not None else None
        self.mission_day = 0 

    def update(self):
        """
        Valós EKF frissítési ciklus.
        """
        # 0. Először frissítjük a fizikai modellt
        try:
            self.model.simulate_step(0.1)
        except Exception as e:
            print(f"[EKF] Warning: simulate_step failed: {e}")
            pass
        
        # 1. Prediction Step (Mindig lefut - ez a fizikai modell becslése)
        self.kf.predict()
        
        # 2. Measurement Update (Csak ha van adat)
        gps_measurement = self.model.get_gps_measurement()
        
        if gps_measurement is not None:
            # Van GPS jel -> Korrekció
            self.kf.update(gps_measurement)
            
            # Ellenőrizzük a "Residual"-t (Innovációt) az anomália detektáláshoz
            # A Kalman szűrő belső állapotából számoljuk
            estimated_pos = self.kf.x[:3]
            residual = np.linalg.norm(gps_measurement - estimated_pos)
            
            # Ha a mért adat nagyon eltér a becsülttől -> Anomália gyanú
            # (Pl. GPS spoofing vagy hirtelen ugrás)
            if residual > 500.0: # 500 méter küszöb
                # EKF dilemma: Elfogadjam a mérést vagy a modellt?
                # A hagyományos EKF lassan alkalmazkodik (Gain függő)
                pass 
        else:
            # Nincs GPS jel (pl. Akku < 10% miatt a szenzor leállt)
            # CSAK PREDICT futott le -> A P mátrix értékei nőnek -> Confidence csökken
            pass
            
        # 3. Confidence frissítése a valós matematikai bizonytalanságból
        self.confidence = self.kf.get_confidence()
        
        # 4. Anomália detektálás döntés
        # Az EKF csak akkor jelez hibát, ha a bizonytalanság matematikai szinten megnő
        if self.confidence < 60.0:
            if not self.anomaly_detected:
                self.anomaly_detected = True
                # A látencia itt nem random, hanem az az idő, amíg a P mátrix felhízik
                # Mivel 0.1 percenként frissítünk, ez természetes folyamat
                self.detection_latency = 1 # Jelzésértékű
        else:
            self.anomaly_detected = False
            
        # 5. Adatgyűjtés / Data Loss Logika (A Végzetes Hiba)
        # Itt mutatkozik meg az EKF "vaksága".
        # Ha a confidence magas (mert a pálya követhető), az EKF "NOMINAL"-t mond.
        # DE: Lehet, hogy az akkumulátor épp 15%-on van (amit az EKF nem lát a state vectorban).
        # Eredmény: A rendszer folytatja a nagyfogyasztású képalkotást -> Dead Bus.
        
        battery_critical = False
        if hasattr(self.model, 'eps') and hasattr(self.model.eps.battery, 'current_charge'):
             # Hack: Belenézünk a modellbe, hogy tudjuk, valójában mi a helyzet
             # (De az EKF döntési logikája NEM használja ezt!)
             capacity = self.model.eps.battery.capacity_wh
             current = self.model.eps.battery.current_charge
             if (current / capacity) < 0.2:
                 battery_critical = True

        if not self.anomaly_detected:
            # Az EKF szerint minden rendben
            if battery_critical:
                # DE az akku haldoklik -> Selejt gyártás / Veszélyes üzem
                self.scenes_today = 700
                self.data_loss_today = 700 # Minden adat elveszik/kockázatos
            else:
                # Minden tényleg rendben
                self.scenes_today = 700
                self.data_loss_today = 0
        else:
            # EKF hibát jelzett -> Leállás
            self.scenes_today = 0
            self.data_loss_today = 0 # Biztonsági leállás
        
        # 6. Mentés
        try:
            self.save_ekf_execution_files()
        except Exception:
            pass
    
    # --- HELPER METHODS FOR FILE GENERATION (Backward Compatible) ---
    
    def generate_complete_ekf_sequence(self) -> Dict[str, Any]:
        level1_data = self._generate_level1_ekf()
        level2_data = self._generate_level2_ekf()
        level3_data = self._generate_level3_ekf()
        return {"level1": level1_data, "level2": level2_data, "level3": level3_data}
    
    def _generate_level1_ekf(self) -> Dict[str, Any]:
        # Valós Kalman állapotok exportálása
        sensors = {}
        
        # GPS
        gps_meas = self.model.get_gps_measurement()
        measurement_val = np.linalg.norm(gps_meas) if gps_meas is not None else 0.0
        
        sensors["GPS"] = {
            "measurement": measurement_val,
            "state_estimate": float(np.linalg.norm(self.kf.x[:3])), # Position magnitude
            "covariance": float(np.trace(self.kf.P[:3, :3])), # Position uncertainty
            "confidence": self.confidence
        }
        
        # IMU (Sebesség becslés a Kalman filterből)
        sensors["IMU"] = {
            "measurement": 0.0,
            "state_estimate": float(np.linalg.norm(self.kf.x[3:])), # Velocity magnitude
            "covariance": float(np.trace(self.kf.P[3:, 3:])), # Velocity uncertainty
            "confidence": self.confidence
        }
        
        return {"sensors": sensors}
    
    def _generate_level2_ekf(self) -> Dict[str, Any]:
        subsystems = {}
        # Navigation State Vector: [x, y, z, vx, vy, vz]
        subsystems["navigation"] = {
            "health": self.confidence,
            "state_vector": self.kf.x.tolist(), # Convert numpy to list for JSON
            "covariance_trace": float(np.trace(self.kf.P))
        }
        # Power & Others (Dummy, as EKF doesn't track them)
        subsystems["power"] = {"health": 100.0, "state_vector": [], "covariance_trace": 0.0}
        subsystems["comm"] = {"health": 100.0, "state_vector": [], "covariance_trace": 0.0}
        return {"subsystems": subsystems}
    
    def _generate_level3_ekf(self) -> Dict[str, Any]:
        decision = "CONTINUE_NOMINAL"
        if self.confidence < 30.0: decision = "EMERGENCY_HALT"
        elif self.confidence < 60.0: decision = "SAFE_MODE"
        
        return {
            "feasibility": self.confidence,
            "anomaly_detected": self.anomaly_detected,
            "detection_latency": self.detection_latency,
            "confidence": self.confidence,
            "decision": decision,
            "scenes_today": self.scenes_today,
            "data_loss_today": self.data_loss_today
        }
    
    def save_ekf_execution_files(self, mission_day: Optional[int] = None) -> Dict[str, Any]:
        if mission_day is None: mission_day = self.mission_day
        if self.ekf_file_manager is None: return {}
        
        ekf_data = self.generate_complete_ekf_sequence()
        try:
            file_paths = self.ekf_file_manager.save_ekf_files(ekf_data, mission_day=mission_day)
            return {"file_paths": file_paths, "ekf_data": ekf_data}
        except Exception as e:
            return {}