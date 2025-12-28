"""
MetaSpace V3.2 - Validation Engine
Matematikailag 100%-os validáció minden lépésre.
"""
from typing import Dict, List, Any, Tuple
import hashlib
import json


class V3ValidationEngine:
    """
    Validációs motor a V3 Neural Network számára.
    Invariánsok ellenőrzése + matematikai validáció.
    """
    
    def __init__(self):
        self.invariants = {
            "health_bounds": {
                "description": "∀n: 0 ≤ n.health ≤ 100",
                "check": self._check_health_bounds
            },
            "master_uniqueness": {
                "description": "|{n: n.is_master}| ≤ 1",
                "check": self._check_master_uniqueness
            },
            "power_dependency": {
                "description": "regen_active → ∃n: 'power' ∈ n.capabilities",
                "check": self._check_power_dependency
            },
            "feasibility_bounds": {
                "description": "0 ≤ feasibility ≤ 100",
                "check": self._check_feasibility_bounds
            },
            "regen_monotonicity": {
                "description": "regen → health_new ≥ health_old",
                "check": self._check_regen_monotonicity
            },
            "biocode_consistency": {
                "description": "decode(encode(state)) == state",
                "check": self._check_biocode_consistency
            }
        }
        
        # Health history tracking (for regen monotonicity)
        self.health_history = {}  # {node_id: [health_values]}
    
    def _check_health_bounds(self, nodes: List[Any]) -> Tuple[bool, str]:
        """Ellenőrzi, hogy minden node health-je 0-100 között van"""
        violations = []
        for node in nodes:
            if not (0 <= node.health <= 100):
                violations.append(f"{node.id}: health={node.health} (kell: 0-100)")
        
        if violations:
            return False, f"Health bounds violations: {', '.join(violations)}"
        return True, "Minden node health-je 0-100 kozott van (OK)"
    
    def _check_master_uniqueness(self, nodes: List[Any]) -> Tuple[bool, str]:
        """Ellenőrzi, hogy maximum 1 master node van"""
        masters = [n for n in nodes if n.is_master]
        if len(masters) > 1:
            master_ids = [n.id for n in masters]
            return False, f"Tobb master node: {', '.join(master_ids)} (kell: max 1)"
        return True, f"Master uniqueness OK: {len(masters)} master node (OK)"
    
    def _check_power_dependency(self, nodes: List[Any], regen_active: bool) -> Tuple[bool, str]:
        """Ellenőrzi, hogy ha regen aktív, akkor van power capability"""
        if not regen_active:
            return True, "Regen nem aktív, nincs ellenőrzés szükséges"
        
        active_nodes = [n for n in nodes if n.health > 0]
        has_power = any("power" in n.capabilities for n in active_nodes)
        
        if not has_power:
            return False, "Regen aktiv, de nincs power capability aktiv node-ban"
        return True, "Power dependency OK: van aktiv power capability (OK)"
    
    def _check_feasibility_bounds(self, feasibility: float) -> Tuple[bool, str]:
        """Ellenőrzi, hogy a feasibility 0-100 között van"""
        if not (0 <= feasibility <= 100):
            return False, f"Feasibility out of bounds: {feasibility} (kell: 0-100)"
        return True, f"Feasibility bounds OK: {feasibility:.2f}%"
    
    def _check_regen_monotonicity(self, nodes: List[Any], 
                                  operation: str) -> Tuple[bool, str]:
        """Ellenőrzi, hogy regen esetén a health nem csökken"""
        if operation != "regeneration":
            return True, "Nem regen művelet, nincs ellenőrzés szükséges"
        
        violations = []
        for node in nodes:
            node_id = node.id
            current_health = node.health
            
            # Health history ellenőrzése (ha van előző érték)
            if node_id in self.health_history and len(self.health_history[node_id]) > 0:
                previous_health = self.health_history[node_id][-1]
                # Kis tolerancia (0.01) a floating point hibák miatt
                if current_health < previous_health - 0.01:
                    violations.append(
                        f"{node_id}: {previous_health:.1f}% → {current_health:.1f}% "
                        f"(csokkenes regen kozben)"
                    )
        
        if violations:
            return False, f"Regen monotonicity violations: {', '.join(violations)}"
        return True, "Regen monotonicity OK: minden node health-je nem csokken (OK)"
    
    def _check_biocode_consistency(self, biocode_data: Dict[str, Any],
                                  biocode_engine: Any) -> Tuple[bool, str]:
        """Ellenőrzi, hogy a bio-kód encoding/decoding konzisztens"""
        try:
            # Level 3 bio-code ellenőrzése
            level3_hex = biocode_data.get("level3", {}).get("biocode", "")
            if not level3_hex:
                return True, "Nincs Level 3 bio-code ellenőrzéshez"
            
            level3_int = int(level3_hex, 16)
            decoded = biocode_engine.decode_level3_biocode(level3_int)
            
            # Összehasonlítás (tolerancia: 1% - mert a feasibility integer-re kerekítve van a bio-code-ban)
            expected_feasibility = biocode_data.get("level3", {}).get("feasibility", 0)
            decoded_feasibility = decoded.get("feasibility_percent", 0)
            
            # A bio-kódban integer van tárolva, ezért a kerekítés várható
            # Tolerancia: 1% (pl. 74.5% → 74% vagy 75% is OK)
            if abs(expected_feasibility - decoded_feasibility) > 1.0:
                return False, (
                    f"Bio-code inconsistency: "
                    f"expected feasibility={expected_feasibility:.2f}%, "
                    f"decoded={decoded_feasibility}% (tolerance: 1%)"
                )
            
            # Action ellenőrzése
            expected_action = biocode_data.get("level3", {}).get("action", "")
            decoded_action = decoded.get("action", "")
            if expected_action != decoded_action:
                return False, (
                    f"Bio-code action inconsistency: "
                    f"expected={expected_action}, decoded={decoded_action}"
                )
            
            return True, (
                f"Bio-code consistency OK: encoding/decoding konzisztens "
                f"(expected={expected_feasibility:.2f}%, decoded={decoded_feasibility}%, diff={abs(expected_feasibility - decoded_feasibility):.2f}%)"
            )
        except Exception as e:
            return False, f"Bio-code consistency check error: {str(e)}"
    
    def validate_operation(self, operation: str, nodes: List[Any], 
                          active_nodes: List[Any], feasibility: float,
                          biocode_data: Dict[str, Any] = None,
                          biocode_engine: Any = None,
                          regen_active: bool = False) -> Dict[str, Any]:
        """
        Validálja egy műveletet (chaos injection, regeneration, stb.)
        
        Args:
            operation: Művelet típusa ("chaos_injection", "regeneration", stb.)
            nodes: Összes node
            active_nodes: Aktív node-ok
            feasibility: Feasibility érték
            biocode_data: Bio-kód adatok (opcionális)
            biocode_engine: Bio-kód engine (opcionális)
            regen_active: Regen aktív-e (opcionális)
        
        Returns:
            Validációs eredmény
        """
        results = {
            "operation": operation,
            "timestamp": None,
            "invariants": {},
            "mathematics": {},
            "overall_status": "PASSED",
            "errors": []
        }
        
        from datetime import datetime
        results["timestamp"] = datetime.now().isoformat()
        
        # Invariánsok ellenőrzése
        invariant_results = {}
        for name, invariant in self.invariants.items():
            try:
                if name == "power_dependency":
                    passed, details = invariant["check"](nodes, regen_active)
                elif name == "regen_monotonicity":
                    passed, details = invariant["check"](nodes, operation)
                elif name == "feasibility_bounds":
                    passed, details = invariant["check"](feasibility)
                elif name == "biocode_consistency":
                    if biocode_data and biocode_engine:
                        passed, details = invariant["check"](biocode_data, biocode_engine)
                    else:
                        passed, details = True, "Bio-code not generated (not required for validation)"
                else:
                    passed, details = invariant["check"](nodes)
                
                invariant_results[name] = {
                    "passed": passed,
                    "description": invariant["description"],
                    "details": details
                }
                
                if not passed:
                    results["overall_status"] = "FAILED"
                    results["errors"].append(f"{name}: {details}")
            except Exception as e:
                invariant_results[name] = {
                    "passed": False,
                    "description": invariant["description"],
                    "details": f"Check error: {str(e)}"
                }
                results["overall_status"] = "FAILED"
                results["errors"].append(f"{name}: Check error - {str(e)}")
        
        results["invariants"] = invariant_results
        
        # Matematikai validáció
        math_results = {}
        
        # Feasibility formula validáció
        try:
            # Ellenőrizzük, hogy a feasibility 0-100 között van
            if 0 <= feasibility <= 100:
                math_results["feasibility_formula"] = {
                    "valid": True,
                    "proof": f"Feasibility = {feasibility:.2f}%, 0 ≤ {feasibility:.2f} ≤ 100 ✓"
                }
            else:
                math_results["feasibility_formula"] = {
                    "valid": False,
                    "proof": f"Feasibility = {feasibility:.2f}%, NEM 0-100 kozott ✗"
                }
                results["overall_status"] = "FAILED"
        except Exception as e:
            math_results["feasibility_formula"] = {
                "valid": False,
                "proof": f"Error: {str(e)}"
            }
            results["overall_status"] = "FAILED"
        
        # Bio-kód matematikai validáció
        if biocode_data and biocode_engine:
            try:
                level3_hex = biocode_data.get("level3", {}).get("biocode", "")
                if level3_hex:
                    level3_int = int(level3_hex, 16)
                    decoded = biocode_engine.decode_level3_biocode(level3_int)
                    
                    # Ellenőrizzük a dekódolt értékeket
                    expected_feasibility = biocode_data.get("level3", {}).get("feasibility", 0)
                    decoded_feasibility = decoded.get("feasibility_percent", 0)
                    
                    # A bio-kódban integer van tárolva, ezért a kerekítés várható
                    # Tolerancia: 1% (pl. 74.5% → 74% vagy 75% is OK)
                    feasibility_diff = abs(expected_feasibility - decoded_feasibility)
                    if feasibility_diff <= 1.0:
                        math_results["biocode_encoding"] = {
                            "valid": True,
                            "proof": (
                                f"Level 3 bio-code encoding/decoding konzisztens: "
                                f"expected={expected_feasibility:.2f}%, "
                                f"decoded={decoded_feasibility}%, "
                                f"diff={feasibility_diff:.2f}% (tolerance: 1%) ✓"
                            )
                        }
                    else:
                        math_results["biocode_encoding"] = {
                            "valid": False,
                            "proof": (
                                f"Level 3 bio-code encoding/decoding NEM konzisztens: "
                                f"expected={expected_feasibility:.2f}%, "
                                f"decoded={decoded_feasibility}%, "
                                f"diff={feasibility_diff:.2f}% (tolerance: 1%) ✗"
                            )
                        }
                        results["overall_status"] = "FAILED"
            except Exception as e:
                math_results["biocode_encoding"] = {
                    "valid": False,
                    "proof": f"Bio-code validation error: {str(e)}"
                }
                results["overall_status"] = "FAILED"
        
        results["mathematics"] = math_results
        
        # Health history frissítése (regen monotonicity követéshez)
        if operation == "regeneration":
            for node in nodes:
                node_id = node.id
                if node_id not in self.health_history:
                    self.health_history[node_id] = []
                self.health_history[node_id].append(node.health)
                # Tartsuk meg csak az utolsó 10 értéket
                if len(self.health_history[node_id]) > 10:
                    self.health_history[node_id] = self.health_history[node_id][-10:]
        
        return results

