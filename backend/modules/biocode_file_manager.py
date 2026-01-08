"""
Bio-Code File Manager - 3 .bio fájl generálása és kezelése
Műhold és küldetés irányítása bio-kód fájlokkal.
Validálás titkosított fájlok szerint.
"""
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import struct

# Validációs engine import (titkosított validációhoz)
try:
    from backend.modules.v3_validation_engine import V3ValidationEngine
except ImportError:
    try:
        from modules.v3_validation_engine import V3ValidationEngine
    except ImportError:
        V3ValidationEngine = None


class BioCodeFileManager:
    """
    3 .bio fájl generálása és kezelése:
    1. level1.bio - Node health bio-kódok (műhold komponensek)
    2. level2.bio - Module aggregation bio-kódok (alrendszerek)
    3. level3.bio - Mission decision bio-kódok (küldetés irányítás)
    """
    
    def __init__(self, output_dir: str = "backend/biocodes", validation_engine: Optional[Any] = None):
        """
        Args:
            output_dir: Könyvtár, ahol a .bio fájlokat mentjük
            validation_engine: V3ValidationEngine instance (opcionális, ha None, akkor létrehozunk egyet)
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Validációs engine inicializálása (ha nincs megadva)
        if validation_engine is None and V3ValidationEngine is not None:
            self.validation_engine = V3ValidationEngine()
        else:
            self.validation_engine = validation_engine
    
    def save_biocode_files(self, biocode_data: Dict[str, Any], 
                          mission_day: int = 0,
                          timestamp: Optional[str] = None,
                          biocode_engine: Optional[Any] = None,
                          validate: bool = True) -> Dict[str, Any]:
        """
        3 .bio fájl mentése a műhold irányításához.
        Validálás titkosított fájlok szerint (ha validate=True).
        
        Args:
            biocode_data: Teljes bio-kód hierarchia (level1, level2, level3)
            mission_day: Mission day szám
            timestamp: Időbélyeg (opcionális)
            biocode_engine: V3BioCodeEngine instance (validációhoz)
            validate: Validáljuk-e a bio-kódokat titkosított fájlok szerint
        
        Returns:
            Dictionary a fájl elérési utakkal és validációs eredményekkel
        """
        if not timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        file_paths = {}
        validation_results = {}
        
        # VALIDÁCIÓ (titkosított fájlok szerint)
        if validate and self.validation_engine is not None and biocode_engine is not None:
            try:
                # Bio-code validáció titkosított fájlokkal
                validation_result = self.validation_engine.validate_operation(
                    operation="biocode_file_save",
                    nodes=[],  # Nincs szükség node-okra a bio-code validációhoz
                    active_nodes=[],
                    feasibility=0.0,
                    biocode_data=biocode_data,
                    biocode_engine=biocode_engine,
                    regen_active=False
                )
                
                # Validációs eredmények kinyerése
                validation_results = {
                    "passed": all(inv.get("passed", False) for inv in validation_result.get("invariants", {}).values()),
                    "invariants": validation_result.get("invariants", {}),
                    "encrypted_validation": validation_result.get("invariants", {}).get("biocode_encrypted_validation", {})
                }
                
                # Ha a validáció sikertelen, warning-ot adunk, de mentjük a fájlokat
                if not validation_results["passed"]:
                    print(f"[BIOCODE FILE MANAGER] Warning: Bio-code validation failed, but files will be saved anyway.")
                    print(f"[BIOCODE FILE MANAGER] Validation details: {validation_results}")
            except Exception as e:
                print(f"[BIOCODE FILE MANAGER] Warning: Validation error: {e}")
                validation_results = {
                    "passed": False,
                    "error": str(e)
                }
        
        # 1. level1.bio - Node health bio-kódok (bináris formátum)
        level1_path = os.path.join(self.output_dir, f"level1_{mission_day:04d}_{timestamp}.bio")
        self._save_level1_bio(level1_path, biocode_data.get("level1", {}))
        file_paths["level1"] = level1_path
        
        # 2. level2.bio - Module aggregation bio-kódok (bináris formátum)
        level2_path = os.path.join(self.output_dir, f"level2_{mission_day:04d}_{timestamp}.bio")
        self._save_level2_bio(level2_path, biocode_data.get("level2", {}))
        file_paths["level2"] = level2_path
        
        # 3. level3.bio - Mission decision bio-kódok (bináris formátum)
        level3_path = os.path.join(self.output_dir, f"level3_{mission_day:04d}_{timestamp}.bio")
        self._save_level3_bio(level3_path, biocode_data.get("level3", {}), mission_day)
        file_paths["level3"] = level3_path
        
        return {
            "file_paths": file_paths,
            "validation": validation_results
        }
    
    def _save_level1_bio(self, filepath: str, level1_data: Dict[str, Any]):
        """
        Level 1 .bio fájl mentése (Node health bio-kódok).
        
        Formátum:
        - Header: 16 bytes (magic number + version + node count)
        - Data: 8 bytes × node count (64-bit bio-code per node)
        """
        biocodes = level1_data.get("biocodes", {})
        
        with open(filepath, "wb") as f:
            # Header: Magic number (4 bytes) + Version (2 bytes) + Node count (2 bytes) + Reserved (8 bytes)
            magic = b'BIO1'  # Bio-code Level 1 magic number
            version = struct.pack('<H', 1)  # Version 1
            node_count = struct.pack('<H', len(biocodes))
            reserved = b'\x00' * 8
            
            f.write(magic + version + node_count + reserved)
            
            # Data: Node ID (2 bytes) + Bio-code (8 bytes) per node
            for node_id, biocode_hex in biocodes.items():
                # Node ID lookup (16-bit)
                node_id_code = self._get_node_id_code(node_id)
                biocode_int = int(biocode_hex, 16)
                
                f.write(struct.pack('<HQ', node_id_code, biocode_int))
    
    def _save_level2_bio(self, filepath: str, level2_data: Dict[str, Any]):
        """
        Level 2 .bio fájl mentése (Module aggregation bio-kódok).
        
        Formátum:
        - Header: 16 bytes (magic number + version + module count)
        - Data: 4 bytes × module count (32-bit bio-code per module)
        """
        biocodes = level2_data.get("biocodes", {})
        
        with open(filepath, "wb") as f:
            # Header: Magic number (4 bytes) + Version (2 bytes) + Module count (2 bytes) + Reserved (8 bytes)
            magic = b'BIO2'  # Bio-code Level 2 magic number
            version = struct.pack('<H', 1)  # Version 1
            module_count = struct.pack('<H', len(biocodes))
            reserved = b'\x00' * 8
            
            f.write(magic + version + module_count + reserved)
            
            # Data: Module ID (1 byte) + Bio-code (4 bytes) per module
            for module_name, biocode_hex in biocodes.items():
                # Module ID lookup (8-bit)
                module_id_code = self._get_module_id_code(module_name)
                biocode_int = int(biocode_hex, 16)
                
                f.write(struct.pack('<BI', module_id_code, biocode_int))
    
    def _save_level3_bio(self, filepath: str, level3_data: Dict[str, Any], mission_day: int):
        """
        Level 3 .bio fájl mentése (Mission decision bio-kódok).
        
        Formátum:
        - Header: 16 bytes (magic number + version + mission day)
        - Data: 8 bytes (64-bit bio-code) + feasibility + action + safety margin
        """
        biocode_hex = level3_data.get("biocode", "")
        feasibility = level3_data.get("feasibility", 0.0)
        action = level3_data.get("action", "")
        safety_margin = level3_data.get("safety_margin", 0)
        
        with open(filepath, "wb") as f:
            # Header: Magic number (4 bytes) + Version (2 bytes) + Mission day (2 bytes) + Reserved (8 bytes)
            magic = b'BIO3'  # Bio-code Level 3 magic number
            version = struct.pack('<H', 1)  # Version 1
            mission_day_packed = struct.pack('<H', mission_day)
            reserved = b'\x00' * 8
            
            f.write(magic + version + mission_day_packed + reserved)
            
            # Data: Bio-code (8 bytes) + Feasibility (4 bytes float) + Action code (4 bytes) + Safety margin (1 byte) + Reserved (3 bytes)
            if biocode_hex:
                biocode_int = int(biocode_hex, 16)
            else:
                biocode_int = 0
            
            action_code = self._get_action_code(action)
            
            f.write(struct.pack('<QfIB', biocode_int, feasibility, action_code, safety_margin))
            f.write(b'\x00' * 3)  # Reserved bytes
    
    def load_biocode_files(self, level1_path: str, level2_path: str, level3_path: str) -> Dict[str, Any]:
        """
        3 .bio fájl betöltése.
        
        Args:
            level1_path: Level 1 .bio fájl elérési útja
            level2_path: Level 2 .bio fájl elérési útja
            level3_path: Level 3 .bio fájl elérési útja
        
        Returns:
            Bio-kód adatok dictionary
        """
        result = {
            "level1": {},
            "level2": {},
            "level3": {}
        }
        
        # Level 1 betöltése
        if os.path.exists(level1_path):
            result["level1"] = self._load_level1_bio(level1_path)
        
        # Level 2 betöltése
        if os.path.exists(level2_path):
            result["level2"] = self._load_level2_bio(level2_path)
        
        # Level 3 betöltése
        if os.path.exists(level3_path):
            result["level3"] = self._load_level3_bio(level3_path)
        
        return result
    
    def _load_level1_bio(self, filepath: str) -> Dict[str, Any]:
        """Level 1 .bio fájl betöltése"""
        with open(filepath, "rb") as f:
            # Header olvasása
            magic = f.read(4)
            if magic != b'BIO1':
                raise ValueError(f"Invalid Level 1 bio file: wrong magic number")
            
            version = struct.unpack('<H', f.read(2))[0]
            node_count = struct.unpack('<H', f.read(2))[0]
            f.read(8)  # Reserved
            
            # Data olvasása
            biocodes = {}
            for _ in range(node_count):
                node_id_code, biocode_int = struct.unpack('<HQ', f.read(10))
                node_id = self._get_node_id_from_code(node_id_code)
                biocodes[node_id] = f"0x{biocode_int:016X}"
            
            return {
                "version": version,
                "count": node_count,
                "biocodes": biocodes
            }
    
    def _load_level2_bio(self, filepath: str) -> Dict[str, Any]:
        """Level 2 .bio fájl betöltése"""
        with open(filepath, "rb") as f:
            # Header olvasása
            magic = f.read(4)
            if magic != b'BIO2':
                raise ValueError(f"Invalid Level 2 bio file: wrong magic number")
            
            version = struct.unpack('<H', f.read(2))[0]
            module_count = struct.unpack('<H', f.read(2))[0]
            f.read(8)  # Reserved
            
            # Data olvasása
            biocodes = {}
            for _ in range(module_count):
                module_id_code, biocode_int = struct.unpack('<BI', f.read(5))
                module_name = self._get_module_name_from_code(module_id_code)
                biocodes[module_name] = f"0x{biocode_int:08X}"
            
            return {
                "version": version,
                "count": module_count,
                "biocodes": biocodes
            }
    
    def _load_level3_bio(self, filepath: str) -> Dict[str, Any]:
        """Level 3 .bio fájl betöltése"""
        with open(filepath, "rb") as f:
            # Header olvasása
            magic = f.read(4)
            if magic != b'BIO3':
                raise ValueError(f"Invalid Level 3 bio file: wrong magic number")
            
            version = struct.unpack('<H', f.read(2))[0]
            mission_day = struct.unpack('<H', f.read(2))[0]
            f.read(8)  # Reserved
            
            # Data olvasása
            biocode_int, feasibility, action_code, safety_margin = struct.unpack('<QfIB', f.read(17))
            f.read(3)  # Reserved
            
            action = self._get_action_from_code(action_code)
            
            return {
                "version": version,
                "mission_day": mission_day,
                "biocode": f"0x{biocode_int:016X}",
                "feasibility": feasibility,
                "action": action,
                "safety_margin": safety_margin
            }
    
    def _get_node_id_code(self, node_id: str) -> int:
        """Node ID string → 16-bit code"""
        node_id_map = {
            "OLI2": 0x0001, "TIRS2": 0x0002, "ST_A": 0x0003, "ST_B": 0x0004,
            "EPS": 0x0005, "OBC": 0x0006, "X_BAND": 0x0007, "S_BAND": 0x0008
        }
        return node_id_map.get(node_id, 0x0000)
    
    def _get_node_id_from_code(self, code: int) -> str:
        """16-bit code → Node ID string"""
        code_to_node = {
            0x0001: "OLI2", 0x0002: "TIRS2", 0x0003: "ST_A", 0x0004: "ST_B",
            0x0005: "EPS", 0x0006: "OBC", 0x0007: "X_BAND", 0x0008: "S_BAND"
        }
        return code_to_node.get(code, "UNKNOWN")
    
    def _get_module_id_code(self, module_name: str) -> int:
        """Module name → 8-bit code"""
        module_id_map = {
            "payload": 0x01, "power": 0x02, "navigation": 0x03, "comm": 0x04
        }
        return module_id_map.get(module_name, 0x00)
    
    def _get_module_name_from_code(self, code: int) -> str:
        """8-bit code → Module name"""
        code_to_module = {
            0x01: "payload", 0x02: "power", 0x03: "navigation", 0x04: "comm"
        }
        return code_to_module.get(code, "UNKNOWN")
    
    def _get_action_code(self, action: str) -> int:
        """Action string → 32-bit code"""
        action_codes = {
            "CONTINUE_NOMINAL": 0x000001,
            "CONTINUE_WITH_MONITORING": 0x000002,
            "REDUCE_IMAGING_RATE": 0x000003,
            "SWITCH_TO_FALLBACK": 0x000004,
            "SAFE_MODE": 0x000005,
            "EMERGENCY_HALT": 0x000006
        }
        return action_codes.get(action, 0x000000)
    
    def _get_action_from_code(self, code: int) -> str:
        """32-bit code → Action string"""
        code_to_action = {
            0x000001: "CONTINUE_NOMINAL",
            0x000002: "CONTINUE_WITH_MONITORING",
            0x000003: "REDUCE_IMAGING_RATE",
            0x000004: "SWITCH_TO_FALLBACK",
            0x000005: "SAFE_MODE",
            0x000006: "EMERGENCY_HALT"
        }
        return code_to_action.get(code, "UNKNOWN")
    
    def get_latest_biocode_files(self, mission_day: Optional[int] = None) -> Dict[str, str]:
        """
        Legutóbbi .bio fájlok elérési útjainak lekérése.
        
        Args:
            mission_day: Mission day (opcionális, ha None, akkor legutóbbi)
        
        Returns:
            Dictionary a fájl elérési utakkal
        """
        if not os.path.exists(self.output_dir):
            return {}
        
        files = os.listdir(self.output_dir)
        
        # Level 1, 2, 3 fájlok szűrése
        level1_files = [f for f in files if f.startswith("level1_") and f.endswith(".bio")]
        level2_files = [f for f in files if f.startswith("level2_") and f.endswith(".bio")]
        level3_files = [f for f in files if f.startswith("level3_") and f.endswith(".bio")]
        
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

