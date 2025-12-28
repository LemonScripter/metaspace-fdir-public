"""
EKF File Manager - 3 .ekf fájl generálása és kezelése
EKF-alapú végrehajtási fájlok 3 szinten (hasonlóan a bio-fájlokhoz).
"""
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import struct
import numpy as np


class EKFFileManager:
    """
    3 .ekf fájl generálása és kezelése:
    1. level1.ekf - Sensor-level EKF adatok (GPS, IMU, star tracker measurements, state estimates)
    2. level2.ekf - Subsystem-level EKF adatok (navigation, power, payload subsystem health)
    3. level3.ekf - Mission-level EKF adatok (mission feasibility, anomaly detection, decision)
    """
    
    def __init__(self, output_dir: str = "backend/ekf_execution"):
        """
        Args:
            output_dir: Könyvtár, ahol a .ekf fájlokat mentjük
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_ekf_files(self, ekf_data: Dict[str, Any], 
                       mission_day: int = 0,
                       timestamp: Optional[str] = None) -> Dict[str, str]:
        """
        3 .ekf fájl mentése az EKF-alapú végrehajtáshoz.
        
        Args:
            ekf_data: Teljes EKF hierarchia (level1, level2, level3)
            mission_day: Mission day szám
            timestamp: Időbélyeg (opcionális)
        
        Returns:
            Dictionary a fájl elérési utakkal
        """
        if not timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        file_paths = {}
        
        # 1. level1.ekf - Sensor-level EKF adatok (bináris formátum)
        level1_path = os.path.join(self.output_dir, f"level1_{mission_day:04d}_{timestamp}.ekf")
        self._save_level1_ekf(level1_path, ekf_data.get("level1", {}))
        file_paths["level1"] = level1_path
        
        # 2. level2.ekf - Subsystem-level EKF adatok (bináris formátum)
        level2_path = os.path.join(self.output_dir, f"level2_{mission_day:04d}_{timestamp}.ekf")
        self._save_level2_ekf(level2_path, ekf_data.get("level2", {}))
        file_paths["level2"] = level2_path
        
        # 3. level3.ekf - Mission-level EKF adatok (bináris formátum)
        level3_path = os.path.join(self.output_dir, f"level3_{mission_day:04d}_{timestamp}.ekf")
        self._save_level3_ekf(level3_path, ekf_data.get("level3", {}), mission_day)
        file_paths["level3"] = level3_path
        
        return file_paths
    
    def _save_level1_ekf(self, filepath: str, level1_data: Dict[str, Any]):
        """
        Level 1 .ekf fájl mentése (Sensor-level EKF adatok).
        
        Formátum:
        - Header: 16 bytes (magic number + version + sensor count)
        - Data: Sensor measurements + state estimates per sensor
        """
        sensors = level1_data.get("sensors", {})
        
        with open(filepath, "wb") as f:
            # Header: Magic number (4 bytes) + Version (2 bytes) + Sensor count (2 bytes) + Reserved (8 bytes)
            magic = b'EKF1'  # EKF Level 1 magic number
            version = struct.pack('<H', 1)  # Version 1
            sensor_count = struct.pack('<H', len(sensors))
            reserved = b'\x00' * 8
            
            f.write(magic + version + sensor_count + reserved)
            
            # Data: Sensor ID (2 bytes) + Measurement (8 bytes float) + State estimate (8 bytes float) + Covariance (8 bytes float) + Confidence (4 bytes float)
            for sensor_id, sensor_data in sensors.items():
                sensor_id_code = self._get_sensor_id_code(sensor_id)
                measurement = float(sensor_data.get("measurement", 0.0))
                state_estimate = float(sensor_data.get("state_estimate", 0.0))
                covariance = float(sensor_data.get("covariance", 0.0))
                confidence = float(sensor_data.get("confidence", 0.0))
                
                f.write(struct.pack('<Hdddf', sensor_id_code, measurement, state_estimate, covariance, confidence))
    
    def _save_level2_ekf(self, filepath: str, level2_data: Dict[str, Any]):
        """
        Level 2 .ekf fájl mentése (Subsystem-level EKF adatok).
        
        Formátum:
        - Header: 16 bytes (magic number + version + subsystem count)
        - Data: Subsystem health + aggregated state per subsystem
        """
        subsystems = level2_data.get("subsystems", {})
        
        with open(filepath, "wb") as f:
            # Header: Magic number (4 bytes) + Version (2 bytes) + Subsystem count (2 bytes) + Reserved (8 bytes)
            magic = b'EKF2'  # EKF Level 2 magic number
            version = struct.pack('<H', 1)  # Version 1
            subsystem_count = struct.pack('<H', len(subsystems))
            reserved = b'\x00' * 8
            
            f.write(magic + version + subsystem_count + reserved)
            
            # Data: Subsystem ID (1 byte) + Health (4 bytes float) + State vector (15 × 8 bytes float) + Covariance trace (8 bytes float)
            for subsystem_name, subsystem_data in subsystems.items():
                subsystem_id_code = self._get_subsystem_id_code(subsystem_name)
                health = float(subsystem_data.get("health", 0.0))
                state_vector = subsystem_data.get("state_vector", np.zeros(15))
                covariance_trace = float(subsystem_data.get("covariance_trace", 0.0))
                
                # Subsystem ID + Health
                f.write(struct.pack('<Bf', subsystem_id_code, health))
                
                # State vector (15 floats)
                if isinstance(state_vector, np.ndarray):
                    state_vector = state_vector.flatten()[:15]  # Ensure 15 elements
                else:
                    state_vector = list(state_vector)[:15] if len(state_vector) >= 15 else list(state_vector) + [0.0] * (15 - len(state_vector))
                
                for val in state_vector:
                    f.write(struct.pack('<d', float(val)))
                
                # Covariance trace
                f.write(struct.pack('<d', covariance_trace))
    
    def _save_level3_ekf(self, filepath: str, level3_data: Dict[str, Any], mission_day: int):
        """
        Level 3 .ekf fájl mentése (Mission-level EKF adatok).
        
        Formátum:
        - Header: 16 bytes (magic number + version + mission day)
        - Data: Mission feasibility + anomaly detection + decision
        """
        feasibility = level3_data.get("feasibility", 0.0)
        anomaly_detected = level3_data.get("anomaly_detected", False)
        detection_latency = level3_data.get("detection_latency", 0)
        confidence = level3_data.get("confidence", 0.0)
        decision = level3_data.get("decision", "")
        scenes_today = level3_data.get("scenes_today", 0)
        data_loss_today = level3_data.get("data_loss_today", 0)
        
        with open(filepath, "wb") as f:
            # Header: Magic number (4 bytes) + Version (2 bytes) + Mission day (2 bytes) + Reserved (8 bytes)
            magic = b'EKF3'  # EKF Level 3 magic number
            version = struct.pack('<H', 1)  # Version 1
            mission_day_packed = struct.pack('<H', mission_day)
            reserved = b'\x00' * 8
            
            f.write(magic + version + mission_day_packed + reserved)
            
            # Data: Feasibility (4 bytes float) + Anomaly detected (1 byte bool) + Detection latency (4 bytes int) + Confidence (4 bytes float) + Decision code (4 bytes) + Scenes (4 bytes int) + Data loss (4 bytes int) + Reserved (4 bytes)
            decision_code = self._get_decision_code(decision)
            
            f.write(struct.pack('<f?IfIII', 
                               feasibility, 
                               anomaly_detected, 
                               detection_latency, 
                               confidence, 
                               decision_code, 
                               scenes_today, 
                               data_loss_today))
            f.write(b'\x00' * 4)  # Reserved bytes
    
    def load_ekf_files(self, level1_path: str, level2_path: str, level3_path: str) -> Dict[str, Any]:
        """
        3 .ekf fájl betöltése.
        
        Args:
            level1_path: Level 1 .ekf fájl elérési útja
            level2_path: Level 2 .ekf fájl elérési útja
            level3_path: Level 3 .ekf fájl elérési útja
        
        Returns:
            EKF adatok dictionary
        """
        result = {
            "level1": {},
            "level2": {},
            "level3": {}
        }
        
        # Level 1 betöltése (csak ha létezik és nem üres)
        if level1_path and os.path.exists(level1_path) and os.path.getsize(level1_path) > 0:
            try:
                result["level1"] = self._load_level1_ekf(level1_path)
            except Exception as e:
                print(f"[EKF FileManager] Warning: Failed to load level1 from {level1_path}: {e}")
        
        # Level 2 betöltése (csak ha létezik és nem üres)
        if level2_path and os.path.exists(level2_path) and os.path.getsize(level2_path) > 0:
            try:
                result["level2"] = self._load_level2_ekf(level2_path)
            except Exception as e:
                print(f"[EKF FileManager] Warning: Failed to load level2 from {level2_path}: {e}")
        
        # Level 3 betöltése (csak ha létezik és nem üres)
        if level3_path and os.path.exists(level3_path) and os.path.getsize(level3_path) > 0:
            try:
                result["level3"] = self._load_level3_ekf(level3_path)
            except Exception as e:
                print(f"[EKF FileManager] Warning: Failed to load level3 from {level3_path}: {e}")
        
        return result
    
    def _load_level1_ekf(self, filepath: str) -> Dict[str, Any]:
        """Level 1 .ekf fájl betöltése"""
        with open(filepath, "rb") as f:
            # Header olvasása
            magic = f.read(4)
            if magic != b'EKF1':
                raise ValueError(f"Invalid Level 1 EKF file: wrong magic number")
            
            version = struct.unpack('<H', f.read(2))[0]
            sensor_count = struct.unpack('<H', f.read(2))[0]
            f.read(8)  # Reserved
            
            # Data olvasása
            # Formátum: H (2 bytes) + d (8 bytes) + d (8 bytes) + d (8 bytes) + f (4 bytes) = 30 bytes
            sensors = {}
            for _ in range(sensor_count):
                data_bytes = f.read(30)
                if len(data_bytes) < 30:
                    # Ha nincs elég adat, akkor a fájl hiányos vagy rossz formátumú
                    print(f"[EKF FileManager] Warning: Level 1 file incomplete, expected 30 bytes, got {len(data_bytes)}")
                    break
                sensor_id_code, measurement, state_estimate, covariance, confidence = struct.unpack('<Hdddf', data_bytes)
                sensor_id = self._get_sensor_id_from_code(sensor_id_code)
                sensors[sensor_id] = {
                    "measurement": float(measurement),
                    "state_estimate": float(state_estimate),
                    "covariance": float(covariance),
                    "confidence": float(confidence)
                }
            
            return {
                "version": int(version),
                "count": int(sensor_count),
                "sensors": sensors
            }
    
    def _load_level2_ekf(self, filepath: str) -> Dict[str, Any]:
        """Level 2 .ekf fájl betöltése"""
        with open(filepath, "rb") as f:
            # Header olvasása
            magic = f.read(4)
            if magic != b'EKF2':
                raise ValueError(f"Invalid Level 2 EKF file: wrong magic number")
            
            version = struct.unpack('<H', f.read(2))[0]
            subsystem_count = struct.unpack('<H', f.read(2))[0]
            f.read(8)  # Reserved
            
            # Data olvasása
            subsystems = {}
            for _ in range(subsystem_count):
                subsystem_id_code, health = struct.unpack('<Bf', f.read(5))
                subsystem_name = self._get_subsystem_name_from_code(subsystem_id_code)
                
                # State vector (15 floats)
                state_vector = []
                for _ in range(15):
                    val = struct.unpack('<d', f.read(8))[0]
                    state_vector.append(val)
                
                # Covariance trace
                covariance_trace = struct.unpack('<d', f.read(8))[0]
                
                subsystems[subsystem_name] = {
                    "health": float(health),
                    "state_vector": [float(v) for v in state_vector],  # Listává konvertálás JSON szerializáláshoz
                    "covariance_trace": float(covariance_trace)
                }
            
            return {
                "version": int(version),
                "count": int(subsystem_count),
                "subsystems": subsystems
            }
    
    def _load_level3_ekf(self, filepath: str) -> Dict[str, Any]:
        """Level 3 .ekf fájl betöltése"""
        with open(filepath, "rb") as f:
            # Header olvasása
            magic = f.read(4)
            if magic != b'EKF3':
                raise ValueError(f"Invalid Level 3 EKF file: wrong magic number")
            
            version = struct.unpack('<H', f.read(2))[0]
            mission_day = struct.unpack('<H', f.read(2))[0]
            f.read(8)  # Reserved
            
            # Data olvasása
            # Formátum: f (4 bytes) + ? (1 byte) + I (4 bytes) + f (4 bytes) + I (4 bytes) + I (4 bytes) + I (4 bytes) = 25 bytes
            feasibility, anomaly_detected, detection_latency, confidence, decision_code, scenes_today, data_loss_today = struct.unpack('<f?IfIII', f.read(25))
            f.read(4)  # Reserved
            
            decision = self._get_decision_from_code(decision_code)
            
            return {
                "version": int(version),
                "mission_day": int(mission_day),
                "feasibility": float(feasibility),
                "anomaly_detected": bool(anomaly_detected),
                "detection_latency": int(detection_latency),
                "confidence": float(confidence),
                "decision": str(decision),
                "scenes_today": int(scenes_today),
                "data_loss_today": int(data_loss_today)
            }
    
    def _get_sensor_id_code(self, sensor_id: str) -> int:
        """Sensor ID string → 16-bit code"""
        sensor_id_map = {
            "GPS": 0x0001,
            "IMU": 0x0002,
            "STAR_TRACKER_A": 0x0003,
            "STAR_TRACKER_B": 0x0004,
            "MAGNETOMETER": 0x0005,
            "SUN_SENSOR": 0x0006
        }
        return sensor_id_map.get(sensor_id, 0x0000)
    
    def _get_sensor_id_from_code(self, code: int) -> str:
        """16-bit code → Sensor ID string"""
        code_to_sensor = {
            0x0001: "GPS",
            0x0002: "IMU",
            0x0003: "STAR_TRACKER_A",
            0x0004: "STAR_TRACKER_B",
            0x0005: "MAGNETOMETER",
            0x0006: "SUN_SENSOR"
        }
        return code_to_sensor.get(code, "UNKNOWN")
    
    def _get_subsystem_id_code(self, subsystem_name: str) -> int:
        """Subsystem name → 8-bit code"""
        subsystem_id_map = {
            "navigation": 0x01,
            "power": 0x02,
            "payload": 0x03,
            "comm": 0x04,
            "thermal": 0x05
        }
        return subsystem_id_map.get(subsystem_name, 0x00)
    
    def _get_subsystem_name_from_code(self, code: int) -> str:
        """8-bit code → Subsystem name"""
        code_to_subsystem = {
            0x01: "navigation",
            0x02: "power",
            0x03: "payload",
            0x04: "comm",
            0x05: "thermal"
        }
        return code_to_subsystem.get(code, "UNKNOWN")
    
    def _get_decision_code(self, decision: str) -> int:
        """Decision string → 32-bit code"""
        decision_codes = {
            "CONTINUE_NOMINAL": 0x000001,
            "CONTINUE_WITH_MONITORING": 0x000002,
            "REDUCE_OPERATIONS": 0x000003,
            "SAFE_MODE": 0x000004,
            "EMERGENCY_HALT": 0x000005,
            "ANOMALY_DETECTED": 0x000006
        }
        return decision_codes.get(decision, 0x000000)
    
    def _get_decision_from_code(self, code: int) -> str:
        """32-bit code → Decision string"""
        code_to_decision = {
            0x000001: "CONTINUE_NOMINAL",
            0x000002: "CONTINUE_WITH_MONITORING",
            0x000003: "REDUCE_OPERATIONS",
            0x000004: "SAFE_MODE",
            0x000005: "EMERGENCY_HALT",
            0x000006: "ANOMALY_DETECTED"
        }
        return code_to_decision.get(code, "UNKNOWN")
    
    def get_latest_ekf_files(self, mission_day: Optional[int] = None) -> Dict[str, str]:
        """
        Legutóbbi .ekf fájlok elérési útjainak lekérése.
        
        Args:
            mission_day: Mission day (opcionális, ha None, akkor legutóbbi)
        
        Returns:
            Dictionary a fájl elérési utakkal
        """
        if not os.path.exists(self.output_dir):
            return {}
        
        files = os.listdir(self.output_dir)
        
        # Level 1, 2, 3 fájlok szűrése
        level1_files = [f for f in files if f.startswith("level1_") and f.endswith(".ekf")]
        level2_files = [f for f in files if f.startswith("level2_") and f.endswith(".ekf")]
        level3_files = [f for f in files if f.startswith("level3_") and f.endswith(".ekf")]
        
        # Mission day szerint szűrés (ha megadva)
        if mission_day is not None:
            day_str = f"{mission_day:04d}"
            level1_files = [f for f in level1_files if f"_" + day_str + "_" in f]
            level2_files = [f for f in level2_files if f"_" + day_str + "_" in f]
            level3_files = [f for f in level3_files if f"_" + day_str + "_" in f]
        
        # Legutóbbi fájlok (timestamp szerint rendezve)
        level1_files.sort(reverse=True)
        level2_files.sort(reverse=True)
        level3_files.sort(reverse=True)
        
        result = {}
        if level1_files:
            result["level1"] = os.path.join(self.output_dir, level1_files[0])
        if level2_files:
            result["level2"] = os.path.join(self.output_dir, level2_files[0])
        if level3_files:
            result["level3"] = os.path.join(self.output_dir, level3_files[0])
        
        return result

