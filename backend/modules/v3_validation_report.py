"""
MetaSpace V3.2 - Validation Report Generator
Összesített validációs jelentés generálása SHA-256 hash-szel.
"""
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional


class V3ValidationReportGenerator:
    """
    Validációs jelentés generátor V3 Neural Network számára.
    SHA-256 hash generálás, JSON fájl mentés.
    """
    
    def __init__(self, report_dir: str = None):
        """
        Args:
            report_dir: Jelentések könyvtára (alapértelmezett: v3_validation_reports)
        """
        if report_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            report_dir = os.path.join(base_dir, "v3_validation_reports")
        
        self.report_dir = report_dir
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir, exist_ok=True)
        
        # Operations log (összesített)
        self.operations_log = []
        self.latest_report = None
    
    def generate_validation_id(self, biocode_data: Dict[str, Any],
                              all_node_states: List[Dict[str, Any]],
                              all_operations: List[Dict[str, Any]],
                              timestamp: str) -> str:
        """
        SHA-256 hash generálás hamisíthatlan azonosítóhoz.
        
        Args:
            biocode_data: Bio-kód adatok
            all_node_states: Összes node állapot
            all_operations: Összes művelet
            timestamp: Timestamp
        
        Returns:
            SHA-256 hash hex string
        """
        # Nonce generálás (véletlenszerű salt)
        import secrets
        nonce = secrets.token_hex(16)
        
        # Hash input összeállítása (determinisztikus sorrend)
        hash_input = (
            json.dumps(biocode_data, sort_keys=True) +
            json.dumps(all_node_states, sort_keys=True) +
            json.dumps(all_operations, sort_keys=True) +
            timestamp +
            nonce
        )
        
        # SHA-256 hash
        validation_id = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
        
        return validation_id
    
    def add_operation(self, operation: str, validation_result: Dict[str, Any],
                     nodes: List[Any], feasibility: float, biocode_data: Dict[str, Any] = None):
        """
        Művelet hozzáadása az operations log-hoz.
        
        Args:
            operation: Művelet típusa
            validation_result: Validációs eredmény
            nodes: Node-ok
            feasibility: Feasibility
            biocode_data: Bio-kód adatok
        """
        node_states = [{
            "id": n.id,
            "name": n.name,
            "health": n.health,
            "is_master": n.is_master,
            "capabilities": n.capabilities,
            "status": "OPERATIONAL" if n.health > 75 else (
                "HEALING" if 0 < n.health <= 75 else "DEAD"
            )
        } for n in nodes]
        
        self.operations_log.append({
            "operation": operation,
            "timestamp": validation_result.get("timestamp", datetime.now().isoformat()),
            "validated": validation_result.get("overall_status") == "PASSED",
            "feasibility": feasibility,
            "node_states": node_states,
            "validation_status": validation_result.get("overall_status"),
            "biocode_level3": biocode_data.get("level3", {}).get("biocode") if biocode_data else None
        })
    
    def generate_report(self, nodes: List[Any], active_nodes: List[Any],
                       biocode_data: Dict[str, Any],
                       all_validation_results: List[Dict[str, Any]],
                       simulation_active: bool = True,
                       force_save: bool = False) -> Dict[str, Any]:
        """
        Összesített validációs jelentés generálása.
        
        Args:
            nodes: Összes node
            active_nodes: Aktív node-ok
            biocode_data: Bio-kód adatok
            all_validation_results: Összes validációs eredmény
        
        Returns:
            Validációs jelentés
        """
        timestamp = datetime.now().isoformat()
        
        # Node állapotok
        all_node_states = [{
            "id": n.id,
            "name": n.name,
            "health": n.health,
            "is_master": n.is_master,
            "capabilities": n.capabilities,
            "status": "OPERATIONAL" if n.health > 75 else (
                "HEALING" if 0 < n.health <= 75 else "DEAD"
            )
        } for n in nodes]
        
        # Összesített invariáns eredmények
        aggregated_invariants = {}
        for validation_result in all_validation_results:
            for name, result in validation_result.get("invariants", {}).items():
                if name not in aggregated_invariants:
                    aggregated_invariants[name] = {
                        "description": result.get("description", ""),
                        "passed_count": 0,
                        "failed_count": 0,
                        "last_status": None,
                        "last_details": None
                    }
                
                if result.get("passed", False):
                    aggregated_invariants[name]["passed_count"] += 1
                else:
                    aggregated_invariants[name]["failed_count"] += 1
                
                aggregated_invariants[name]["last_status"] = result.get("passed", False)
                aggregated_invariants[name]["last_details"] = result.get("details", "")
        
        # Összesített matematikai eredmények
        aggregated_mathematics = {}
        for validation_result in all_validation_results:
            for name, result in validation_result.get("mathematics", {}).items():
                if name not in aggregated_mathematics:
                    aggregated_mathematics[name] = {
                        "valid_count": 0,
                        "invalid_count": 0,
                        "last_valid": None,
                        "last_proof": None
                    }
                
                if result.get("valid", False):
                    aggregated_mathematics[name]["valid_count"] += 1
                else:
                    aggregated_mathematics[name]["invalid_count"] += 1
                
                aggregated_mathematics[name]["last_valid"] = result.get("valid", False)
                aggregated_mathematics[name]["last_proof"] = result.get("proof", "")
        
        # Overall status meghatározása
        overall_status = "PASSED"
        total_operations = len(all_validation_results)
        passed_operations = sum(1 for r in all_validation_results 
                               if r.get("overall_status") == "PASSED")
        
        if total_operations == 0:
            overall_status = "UNKNOWN"
        elif passed_operations < total_operations:
            overall_status = "FAILED"
        
        # SHA-256 hash generálás
        # Ha nincs bio-kód, akkor is generálhatunk jelentést (csak validációs adatokkal)
        validation_id = self.generate_validation_id(
            biocode_data if biocode_data else {},
            all_node_states,
            self.operations_log,
            timestamp
        )
        
        # Jelentés összeállítása
        # Ha nincs bio-kód, akkor csak feasibility-t használjuk (a _evaluate_feasibility-ból)
        feasibility_value = biocode_data.get("level3", {}).get("feasibility", 0) if biocode_data else 0
        feasibility_explanation = biocode_data.get("level3", {}).get("feasibility_explanation", "") if biocode_data else ""
        action_value = biocode_data.get("level3", {}).get("action", "") if biocode_data else ""
        
        # Ha nincs bio-kód, akkor a feasibility-t a result-ból kell venni
        # De mivel a jelentés generálásnál már nincs result, ezért csak akkor generálunk jelentést, ha van bio-kód
        # VAGY: később generáljuk a bio-kódot a jelentéshez
        
        report = {
            "validation_id": validation_id,
            "timestamp": timestamp,
            "mission_state": {
                "biocode_level3": biocode_data.get("level3", {}).get("biocode") if biocode_data else None,
                "biocode_level2": biocode_data.get("level2", {}).get("biocodes", {}) if biocode_data else {},
                "biocode_level1": biocode_data.get("level1", {}).get("biocodes", {}) if biocode_data else {},
                "feasibility": feasibility_value,
                "feasibility_explanation": feasibility_explanation,
                "action": action_value,
                "safety_margin": biocode_data.get("level3", {}).get("safety_margin", 0) if biocode_data else 0,
                "active_nodes_count": len(active_nodes),
                "total_nodes_count": len(nodes),
                "biocode_generated": biocode_data is not None
            },
            "invariants": aggregated_invariants,
            "mathematics": aggregated_mathematics,
            "operations_log": self.operations_log,
            "overall_status": overall_status,
            "summary": {
                "total_operations": total_operations,
                "passed_operations": passed_operations,
                "failed_operations": total_operations - passed_operations,
                "success_rate": (passed_operations / total_operations * 100) if total_operations > 0 else 0
            }
        }
        
        # Fájl mentés logika:
        # - Csak akkor generálunk fájlt, ha force_save == True (szimuláció befejeződött)
        # - VAGY ha aktív szimuláció, de csak ritkán (minden 20. műveletnél)
        # Ez biztosítja, hogy nem generálódik nonstop jelentés
        
        should_save_file = False
        if biocode_data:
            # Ha force_save == True (szimuláció befejeződött), akkor mindig mentünk
            if force_save:
                should_save_file = True
            # Ha aktív szimuláció, akkor csak ritkán (minden 20. műveletnél)
            elif simulation_active:
                total_ops = len(all_validation_results)
                # Csak akkor mentünk, ha minden 20. műveletnél vagyunk (vagy ha kevés művelet van)
                if total_ops <= 3 or total_ops % 20 == 0:
                    should_save_file = True
        
        if should_save_file:
            filename = f"v3_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{validation_id[:8]}.json"
            filepath = os.path.join(self.report_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # Régi jelentések törlése (csak az utolsó 2 szimuláció maradjon meg)
            self._cleanup_old_reports(max_reports=2)
        
        # Legutóbbi jelentés tárolása (mindig, bio-kóddal vagy anélkül)
        self.latest_report = report
        
        return report
    
    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """Legutóbbi validációs jelentés lekérése"""
        return self.latest_report
    
    def clear_operations_log(self):
        """Operations log törlése (új szimuláció kezdetén)"""
        self.operations_log = []
    
    def _cleanup_old_reports(self, max_reports: int = 2):
        """
        Régi validációs jelentések törlése.
        Csak az utolsó N szimuláció jelentései maradnak meg.
        
        Args:
            max_reports: Maximum megmaradó jelentések száma (alapértelmezett: 2)
        """
        try:
            # Összes V3 validation report fájl listázása
            report_files = []
            if os.path.exists(self.report_dir):
                for filename in os.listdir(self.report_dir):
                    if filename.startswith('v3_validation_report_') and filename.endswith('.json'):
                        filepath = os.path.join(self.report_dir, filename)
                        # Módosítási idő alapján rendezés
                        mtime = os.path.getmtime(filepath)
                        report_files.append((mtime, filepath))
            
            # Rendezés: legfrissebb előre
            report_files.sort(key=lambda x: x[0], reverse=True)
            
            # Törlés: csak az utolsó N maradjon meg
            if len(report_files) > max_reports:
                files_to_delete = report_files[max_reports:]
                for _, filepath in files_to_delete:
                    try:
                        os.remove(filepath)
                        print(f"[V3 VALIDATION] Törölve régi jelentés: {os.path.basename(filepath)}")
                    except Exception as e:
                        print(f"[V3 VALIDATION] Hiba jelentés törlésekor: {e}")
        except Exception as e:
            print(f"[V3 VALIDATION] Hiba régi jelentések törlésekor: {e}")

