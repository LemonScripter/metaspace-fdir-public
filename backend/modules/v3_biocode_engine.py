"""
MetaSpace V3.2 - 3-Level Bio-Code Generation Engine
Determinisztikus védelmi logika bio-kódban kódolva.
"""
import hashlib
from typing import Dict, List, Any, Tuple
from datetime import datetime
import numpy as np


class V3BioCodeEngine:
    """
    3-Level Bio-Code Generation Engine for V3 Neural Network.
    
    Level 1: Node health → 64-bit bio-code
    Level 2: Module aggregation → 32-bit bio-code
    Level 3: Mission decision → 64-bit bio-code
    """
    
    def __init__(self):
        # Sensor/Node ID mapping (16-bit)
        self.node_id_map = {
            "CPU": 0x0001,
            "ST_A": 0x0002,
            "ST_B": 0x0003,
            "EPS": 0x0004,
            "ANT": 0x0005,
            "BATT": 0x0006
        }
        
        # Module ID mapping (8-bit)
        self.module_id_map = {
            "logic": 0x01,
            "navigation": 0x02,
            "power": 0x03,
            "comm": 0x04
        }
        
        # Status encoding (4-bit)
        self.status_encoding = {
            "OPERATIONAL": 0b0000,  # 0
            "HEALING": 0b0001,      # 1
            "DEGRADED": 0b0010,     # 2
            "WARNING": 0b0011,      # 3
            "DEAD": 0b0100,         # 4
            "CRITICAL": 0b0101      # 5
        }
        
        # Trend encoding (4-bit)
        self.trend_encoding = {
            "IMPROVING": 0b0000,    # 0
            "STABLE": 0b0001,       # 1
            "DEGRADING": 0b0010,    # 2
            "CRITICAL": 0b0011      # 3
        }
        
        # Action codes (24-bit)
        self.action_codes = {
            "CONTINUE_NOMINAL": 0x000001,
            "CONTINUE_WITH_MONITORING": 0x000002,
            "REDUCE_IMAGING_RATE": 0x000003,
            "SWITCH_TO_FALLBACK": 0x000004,
            "SAFE_MODE": 0x000005,
            "EMERGENCY_HALT": 0x000006
        }
        
        # Module weights for weighted feasibility calculation
        self.module_weights = {
            "logic": 0.30,      # 30% - CPU kritikus
            "navigation": 0.25, # 25% - Star Tracker kritikus
            "power": 0.25,      # 25% - Power kritikus
            "comm": 0.20        # 20% - Antenna fontos
        }
    
    def generate_level1_biocode(self, node_id: str, health: float, status: str) -> int:
        """
        Level 1: Node health → 64-bit bio-code
        
        Structure:
        - Bits 48-63: Node ID (16 bits)
        - Bits 44-47: Status (4 bits)
        - Bits 12-43: Health % normalized to 32 bits (0-100 → 0-2^32)
        - Bits 0-11: Confidence (12 bits, 0-4095)
        
        Args:
            node_id: Node identifier (CPU, ST_A, ST_B, etc.)
            health: Health percentage (0-100)
            status: Status string (OPERATIONAL, HEALING, etc.)
        
        Returns:
            64-bit integer bio-code
        """
        node_id_code = self.node_id_map.get(node_id, 0x0000)
        status_code = self.status_encoding.get(status, 0b1111)
        
        # Normalize health to 32-bit range (0-100 → 0-2^32)
        health_normalized = int(np.clip(health, 0, 100) * (2**32) / 100)
        
        # Confidence based on health (higher health = higher confidence)
        confidence = int(min(4095, health * 40.95))
        
        # Pack into 64-bit integer
        biocode = (
            (node_id_code << 48) |                    # Bits 48-63: Node ID
            (status_code << 44) |                     # Bits 44-47: Status
            ((health_normalized & 0xFFFFFFFF) << 12) | # Bits 12-43: Health
            (confidence & 0xFFF)                       # Bits 0-11: Confidence
        )
        
        return biocode
    
    def decode_level1_biocode(self, biocode: int) -> Dict[str, Any]:
        """Decode Level 1 bio-code"""
        node_id_code = (biocode >> 48) & 0xFFFF
        status_code = (biocode >> 44) & 0x0F
        health_normalized = (biocode >> 12) & 0xFFFFFFFF
        confidence = biocode & 0xFFF
        
        # Reverse normalization
        health = (health_normalized / (2**32)) * 100
        
        # Find node ID
        node_id = next((k for k, v in self.node_id_map.items() if v == node_id_code), "UNKNOWN")
        
        # Find status
        status = next((k for k, v in self.status_encoding.items() if v == status_code), "UNKNOWN")
        
        return {
            "node_id": node_id,
            "health": round(health, 2),
            "status": status,
            "confidence": confidence,
            "biocode_hex": f"0x{biocode:016X}"
        }
    
    def generate_level2_biocode(self, module_name: str, level1_codes: List[int], 
                                health_history: List[float] = None) -> int:
        """
        Level 2: Module aggregation → 32-bit bio-code
        
        Structure:
        - Bits 24-31: Module ID (8 bits)
        - Bits 16-23: Health % (8 bits, 0-100)
        - Bits 12-15: Trend (4 bits)
        - Bits 0-11: Risk score (12 bits, 0-4095)
        
        Args:
            module_name: Module name (logic, navigation, power, comm)
            level1_codes: List of Level 1 bio-codes for this module
            health_history: Optional health history for trend calculation
        
        Returns:
            32-bit integer bio-code
        """
        module_id = self.module_id_map.get(module_name, 0x00)
        
        # Decode Level 1 codes to get health values
        health_values = []
        for code in level1_codes:
            decoded = self.decode_level1_biocode(code)
            health_values.append(decoded["health"])
        
        # Calculate module health (weighted average if history provided)
        if health_history and len(health_history) > 0:
            # Recent measurements weighted more
            weights = np.exp(-np.arange(len(health_history)) * 0.1)
            weights /= weights.sum()
            module_health = int(np.clip(np.average(health_history, weights=weights), 0, 100))
        else:
            module_health = int(np.clip(np.mean(health_values) if health_values else 0, 0, 100))
        
        # Calculate trend
        if health_history and len(health_history) >= 2:
            trend_value = health_history[-1] - health_history[-2]
            if trend_value < -5:
                trend = self.trend_encoding["DEGRADING"]
            elif trend_value > 5:
                trend = self.trend_encoding["IMPROVING"]
            elif abs(trend_value) > 10:
                trend = self.trend_encoding["CRITICAL"]
            else:
                trend = self.trend_encoding["STABLE"]
        else:
            trend = self.trend_encoding["STABLE"]
        
        # Calculate risk score (0-4095)
        # Risk = (100 - health) * 20 + trend_penalty + variance_penalty
        health_risk = (100 - module_health) * 20
        trend_penalty = trend * 100
        variance_penalty = min(np.std(health_values) * 100, 1000) if len(health_values) > 1 else 0
        risk_score = int(np.clip(health_risk + trend_penalty + variance_penalty, 0, 4095))
        
        # Pack into 32-bit integer
        biocode = (
            (module_id << 24) |           # Bits 24-31: Module ID
            (module_health << 16) |       # Bits 16-23: Health %
            (trend << 12) |               # Bits 12-15: Trend
            (risk_score & 0xFFF)          # Bits 0-11: Risk score
        )
        
        return biocode
    
    def decode_level2_biocode(self, biocode: int) -> Dict[str, Any]:
        """Decode Level 2 bio-code"""
        module_id = (biocode >> 24) & 0xFF
        module_health = (biocode >> 16) & 0xFF
        trend_code = (biocode >> 12) & 0x0F
        risk_score = biocode & 0xFFF
        
        # Find module name
        module_name = next((k for k, v in self.module_id_map.items() if v == module_id), "UNKNOWN")
        
        # Find trend
        trend = next((k for k, v in self.trend_encoding.items() if v == trend_code), "UNKNOWN")
        
        return {
            "module_name": module_name,
            "health": module_health,
            "trend": trend,
            "risk_score": risk_score,
            "biocode_hex": f"0x{biocode:08X}"
        }
    
    def generate_level3_biocode(self, mission_day: int, feasibility: float, 
                                action: str, safety_margin: int) -> int:
        """
        Level 3: Mission decision → 64-bit bio-code
        
        Structure:
        - Bits 48-63: Mission day (16 bits)
        - Bits 32-47: Feasibility % (16 bits, 0-100)
        - Bits 8-31: Action code (24 bits)
        - Bits 0-7: Safety margin (8 bits, 0-255)
        
        Args:
            mission_day: Mission day number
            feasibility: Feasibility percentage (0-100)
            action: Action string
            safety_margin: Safety margin (0-255)
        
        Returns:
            64-bit integer bio-code
        """
        action_code = self.action_codes.get(action, 0x000000)
        feasibility_int = int(np.clip(feasibility, 0, 100))
        
        # Pack into 64-bit integer
        biocode = (
            ((mission_day & 0xFFFF) << 48) |           # Bits 48-63: Mission day
            (feasibility_int << 32) |                  # Bits 32-47: Feasibility %
            ((action_code & 0xFFFFFF) << 8) |          # Bits 8-31: Action
            (safety_margin & 0xFF)                     # Bits 0-7: Safety margin
        )
        
        return biocode
    
    def decode_level3_biocode(self, biocode: int) -> Dict[str, Any]:
        """Decode Level 3 bio-code"""
        mission_day = (biocode >> 48) & 0xFFFF
        feasibility = (biocode >> 32) & 0xFFFF
        action_code = (biocode >> 8) & 0xFFFFFF
        safety_margin = biocode & 0xFF
        
        # Find action name
        action = next((k for k, v in self.action_codes.items() if v == action_code), "UNKNOWN")
        
        return {
            "mission_day": mission_day,
            "feasibility_percent": feasibility,
            "action": action,
            "safety_margin": safety_margin,
            "biocode_hex": f"0x{biocode:016X}"
        }
    
    def calculate_weighted_feasibility(self, nodes: List[Any], 
                                       active_nodes: List[Any]) -> Tuple[float, str]:
        """
        Súlyozott feasibility számítás magyarázattal.
        
        Args:
            nodes: Összes node
            active_nodes: Aktív node-ok
        
        Returns:
            (feasibility_score, explanation_string)
        """
        # Számoljuk ki minden modul health-jét
        module_health = {}
        module_explanations = []
        
        for module_name, weight in self.module_weights.items():
            # Keressük meg azokat a node-okat, amelyek ezt a capability-t támogatják
            module_nodes = [n for n in active_nodes if module_name in n.capabilities]
            
            if module_nodes:
                # Átlagos health a modul node-ok között
                avg_health = np.mean([n.health for n in module_nodes])
                module_health[module_name] = avg_health
                
                node_names = ", ".join([n.name for n in module_nodes])
                module_explanations.append(
                    f"{module_name}({weight*100:.0f}%): {avg_health:.1f}% "
                    f"[{node_names}]"
                )
            else:
                # Nincs aktív node ezzel a capability-vel
                module_health[module_name] = 0.0
                module_explanations.append(
                    f"{module_name}({weight*100:.0f}%): 0% [NINCS AKTIV NODE]"
                )
        
        # Súlyozott átlag számítás
        feasibility_score = sum(
            module_health[module] * weight 
            for module, weight in self.module_weights.items()
        )
        feasibility_score = np.clip(feasibility_score, 0, 100)
        
        # Magyarázat összeállítása
        explanation = "Sulyozott szamitas: " + " + ".join([
            f"{module}({weight*100:.0f}%)*{module_health[module]:.1f}%"
            for module, weight in self.module_weights.items()
        ]) + f" = {feasibility_score:.2f}%"
        
        detailed_explanation = "\n".join(module_explanations)
        
        return feasibility_score, f"{explanation}\n\nReszletes:\n{detailed_explanation}"
    
    def determine_action(self, feasibility: float, module_health: Dict[str, float]) -> str:
        """
        Döntés a feasibility alapján.
        
        Decision tree:
        - >= 90%: CONTINUE_NOMINAL
        - >= 75%: CONTINUE_WITH_MONITORING
        - >= 60%: REDUCE_IMAGING_RATE
        - >= 40%: SWITCH_TO_FALLBACK
        - >= 20%: SAFE_MODE
        - < 20%: EMERGENCY_HALT
        """
        # Kritikus esetek ellenőrzése
        if module_health.get("power", 100) < 20:
            return "EMERGENCY_HALT"
        
        if feasibility >= 90:
            return "CONTINUE_NOMINAL"
        elif feasibility >= 75:
            return "CONTINUE_WITH_MONITORING"
        elif feasibility >= 60:
            return "REDUCE_IMAGING_RATE"
        elif feasibility >= 40:
            return "SWITCH_TO_FALLBACK"
        elif feasibility >= 20:
            return "SAFE_MODE"
        else:
            return "EMERGENCY_HALT"
    
    def generate_complete_biocode_sequence(self, nodes: List[Any], 
                                          active_nodes: List[Any],
                                          mission_day: int = 0) -> Dict[str, Any]:
        """
        Teljes 3-level bio-kód pipeline generálása.
        
        Args:
            nodes: Összes node
            active_nodes: Aktív node-ok
            mission_day: Mission day szám
        
        Returns:
            Teljes bio-kód hierarchia
        """
        # Level 1: Node bio-codes
        level1_codes = {}
        for node in nodes:
            status = "OPERATIONAL" if node.health > 75 else (
                "HEALING" if 0 < node.health <= 75 else "DEAD"
            )
            biocode = self.generate_level1_biocode(node.id, node.health, status)
            level1_codes[node.id] = biocode
        
        # Level 2: Module bio-codes
        level2_codes = {}
        for module_name in self.module_weights.keys():
            # Keressük meg a modulhoz tartozó node-okat
            module_nodes = [n for n in active_nodes if module_name in n.capabilities]
            if module_nodes:
                module_l1_codes = [level1_codes[n.id] for n in module_nodes if n.id in level1_codes]
                if module_l1_codes:
                    health_history = [n.health for n in module_nodes]
                    biocode = self.generate_level2_biocode(module_name, module_l1_codes, health_history)
                    level2_codes[module_name] = biocode
        
        # Súlyozott feasibility számítás
        feasibility, explanation = self.calculate_weighted_feasibility(nodes, active_nodes)
        
        # Action meghatározása
        module_health_dict = {
            module: next(
                (n.health for n in active_nodes if module in n.capabilities),
                0.0
            )
            for module in self.module_weights.keys()
        }
        action = self.determine_action(feasibility, module_health_dict)
        
        # Safety margin számítás (40% kritikus küszöb)
        critical_threshold = 40
        safety_margin = int(max(0, feasibility - critical_threshold))
        
        # Level 3: Mission bio-code
        level3_biocode = self.generate_level3_biocode(mission_day, feasibility, action, safety_margin)
        
        return {
            "mission_day": mission_day,
            "level1": {
                "biocodes": {k: f"0x{v:016X}" for k, v in level1_codes.items()},
                "count": len(level1_codes),
                "total_bytes": len(level1_codes) * 8
            },
            "level2": {
                "biocodes": {k: f"0x{v:08X}" for k, v in level2_codes.items()},
                "count": len(level2_codes),
                "total_bytes": len(level2_codes) * 4
            },
            "level3": {
                "biocode": f"0x{level3_biocode:016X}",
                "feasibility": round(feasibility, 2),
                "feasibility_explanation": explanation,
                "action": action,
                "safety_margin": safety_margin,
                "total_bytes": 8
            },
            "compression_ratio": (len(level1_codes) * 8) / 8 if level1_codes else 1.0
        }

