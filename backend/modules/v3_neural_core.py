import uuid

# V3 Validációs modulok importálása
try:
    from backend.modules.v3_biocode_engine import V3BioCodeEngine
    from backend.modules.v3_validation_engine import V3ValidationEngine
    from backend.modules.v3_validation_report import V3ValidationReportGenerator
    from backend.modules.biocode_file_manager import BioCodeFileManager
except ImportError:
    from modules.v3_biocode_engine import V3BioCodeEngine
    from modules.v3_validation_engine import V3ValidationEngine
    from modules.v3_validation_report import V3ValidationReportGenerator
    from modules.biocode_file_manager import BioCodeFileManager

class HolographicNode:
    """
    MetaSpace v3.2 - Neural Fractal Node with Autonomous Regeneration.
    Szuverén egység, amely önállóan kezeli saját integritását.
    """
    def __init__(self, name, node_id_alias, node_type, capabilities):
        self.internal_id = str(uuid.uuid4())[:8]
        self.id = node_id_alias
        self.name = name
        self.node_type = node_type
        self.capabilities = capabilities
        self.health = 100.0
        self.is_master = False
        
    def get_telemetry(self):
        """Valós idejű állapotjelentés a hálózat felé."""
        return {
            "id": self.id,
            "name": self.name,
            "health": round(self.health, 1),
            "type": self.node_type,
            "capabilities": self.capabilities if self.health > 15 else [], # Funkcióvesztés küszöb
            "status": "OPERATIONAL" if self.health > 75 else ("HEALING" if 0 < self.health <= 75 else "DEAD"),
            "is_master": self.is_master
        }

class NeuralFractalNetwork:
    """
    A Landsat-9 holografikus hálózati motorja modulálható öngyógyítással.
    """
    def __init__(self, landsat_model=None):
        # ✅ VALÓDI: Landsat-9 kritikus alrendszerek (mission requirements)
        # Forrás: Landsat-9 mission specification
        self.mission_requirements = ["payload", "navigation", "power", "comm"]
        self.nodes = []
        self.regen_rate = 8.5 # Alapértelmezett Bio-Code sebesség
        
        # V3 Validációs rendszer inicializálása
        self.biocode_engine = V3BioCodeEngine()
        self.validation_engine = V3ValidationEngine()
        self.report_generator = V3ValidationReportGenerator()
        self.biocode_file_manager = BioCodeFileManager()  # 3 .bio fájl kezelés
        self.mission_day = 0  # Mission day counter
        self.validation_results = []  # Összesített validációs eredmények
        self.simulation_active = False  # Szimuláció aktív-e (csak akkor generálunk jelentést, ha True)
        
        # VALÓS SZIMULÁCIÓ: Landsat9Model kapcsolat (opcionális, backward compatible)
        self.landsat_model = landsat_model  # Valós fizikai modell (None is lehet, ha nincs)
        
        self.reset_constellation()

    def reset_constellation(self):
        """Konstelláció alaphelyzetbe állítása Landsat-9 valódi komponensekkel."""
        # ✅ VALÓDI: Landsat-9 valódi komponens nevek és alrendszerek
        # Forrás: NASA Landsat-9 specification
        self.nodes = [
            HolographicNode("OLI-2", "OLI2", "payload", ["payload"]),  # Operational Land Imager-2
            HolographicNode("TIRS-2", "TIRS2", "payload", ["payload"]),  # Thermal Infrared Sensor-2
            HolographicNode("Star Tracker A", "ST_A", "sensor", ["navigation"]),  # GNC subsystem
            HolographicNode("Star Tracker B", "ST_B", "sensor", ["navigation"]),  # GNC subsystem
            HolographicNode("EPS", "EPS", "actuator", ["power"]),  # Electrical Power System
            HolographicNode("OBC", "OBC", "compute", ["payload", "navigation"]),  # Onboard Computer
            HolographicNode("X-band Transponder", "X_BAND", "sensor", ["comm"]),  # Communication
            HolographicNode("S-band Transponder", "S_BAND", "sensor", ["comm"])  # Communication
        ]
        # ✅ VALÓDI: OBC (Onboard Computer) a master node Landsat-9 spec szerint
        obc_node = next((n for n in self.nodes if n.id == "OBC"), None)
        if obc_node:
            obc_node.is_master = True
        
        # Validációs rendszer reset
        self.validation_results = []
        self.report_generator.clear_operations_log()
        self.mission_day = 0
        self.simulation_active = False  # Szimuláció reset után inaktív

    def set_regen_rate(self, rate):
        """A regeneráció sebességének dinamikus módosítása."""
        try:
            self.regen_rate = float(rate)
        except (ValueError, TypeError):
            self.regen_rate = 8.5

    def inject_chaos_and_calculate(self, killed_ids):
        """Káosz injektálás és master migration."""
        # Szimuláció aktiválása (chaos injection = szimuláció kezdete)
        self.simulation_active = True
        
        events = []
        for node in self.nodes:
            if node.id in killed_ids:
                node.health = 0.0
                node.is_master = False
                events.append(f"IMPACT: {node.name} failure.")

        active_nodes = [n for n in self.nodes if n.health > 0]
        if active_nodes and not any(n.is_master for n in active_nodes):
            self._migrate_master(active_nodes)
            events.append("MASTER MIGRATION: Failover active.")

        result = self._evaluate_feasibility(active_nodes, events)
        
        # AUTOMATIKUS VALIDÁCIÓ (csak akkor, ha van aktív szimuláció)
        # Chaos injection mindig aktiválja a szimulációt
        if self.simulation_active:
            try:
                # Validáció bio-kód NÉLKÜL (gyorsabb, csak invariánsok + matematika)
                validation_result = self.validation_engine.validate_operation(
                    operation="chaos_injection",
                    nodes=self.nodes,
                    active_nodes=active_nodes,
                    feasibility=result["feasibility"],
                    biocode_data=None,  # Nincs bio-kód, csak validáció
                    biocode_engine=None,
                    regen_active=False
                )
                
                # Bio-kód generálás csak jelentés generáláshoz (ritkábban)
                # Pl. minden 5. műveletnél, vagy csak jelentés kérésnél
                biocode_data = None
                should_generate_biocode = (len(self.validation_results) % 5 == 0) or (len(self.validation_results) == 0)
                
                if should_generate_biocode:
                    biocode_data = self.biocode_engine.generate_complete_biocode_sequence(
                        self.nodes, active_nodes, self.mission_day
                    )
                
                # Operations log frissítése
                self.report_generator.add_operation(
                    "chaos_injection",
                    validation_result,
                    self.nodes,
                    result["feasibility"],
                    biocode_data
                )
                
                # Validációs eredmények tárolása
                self.validation_results.append(validation_result)
                
                # Összesített jelentés generálása (itt kell a bio-kód)
                # Csak akkor generálunk fájlt, ha van aktív szimuláció (ritkán)
                if biocode_data:
                    aggregated_report = self.report_generator.generate_report(
                        self.nodes,
                        active_nodes,
                        biocode_data,
                        self.validation_results,
                        simulation_active=self.simulation_active,
                        force_save=False  # Chaos injection-nél nem kell fájl mentés
                    )
                    
                    # Validációs adatok hozzáadása az eredményhez
                    result["validation"] = {
                        "status": validation_result["overall_status"],
                        "biocode_level3": biocode_data.get("level3", {}).get("biocode"),
                        "validation_id": aggregated_report.get("validation_id")
                    }
                else:
                    result["validation"] = {
                        "status": validation_result["overall_status"]
                    }
            except Exception as e:
                # Validációs hiba esetén warning, de művelet folytatódik
                print(f"[V3 VALIDATION] Warning: Validation failed: {e}")
                result["validation"] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        else:
            # Nincs aktív szimuláció (nem kellene előfordulnia chaos injection-nél)
            result["validation"] = {
                "status": "INACTIVE",
                "message": "Nincs aktív szimuláció"
            }
        
        return result

    def process_regeneration(self):
        """
        Szuverén regenerációs ciklus BIO-KÓD ALAPJÁN.
        A bio-kód determinisztikusan vezérli az öngyógyítást.
        """
        # 0. LÉPÉS: VALÓS SZIMULÁCIÓ - Node health szinkronizálása Landsat9Model komponensekkel
        # REALISZTIKUS: Node health = valós komponens health (nem random degradáció)
        # Fontos: Ez CSAK akkor fut le, ha van landsat_model (navigation-plan szimuláció)
        # A v3_fractal_sim NEM használ landsat_model-t (None), így NEM érinti!
        if self.landsat_model is not None:
            # Valós komponens health-t használunk a node-okhoz
            # EPS (power subsystem)
            eps_node = next((n for n in self.nodes if n.id == "EPS"), None)
            if eps_node and hasattr(self.landsat_model.eps, 'battery'):
                # Battery health alapján
                battery_health = getattr(self.landsat_model.eps.battery, 'health', 100.0)
                eps_node.health = battery_health
            
            # GNC (navigation subsystem) - Star Tracker health
            st_a_node = next((n for n in self.nodes if n.id == "ST_A"), None)
            st_b_node = next((n for n in self.nodes if n.id == "ST_B"), None)
            if st_a_node and len(self.landsat_model.gnc.star_trackers) > 0:
                st_a_node.health = getattr(self.landsat_model.gnc.star_trackers[0], 'health', 100.0)
            if st_b_node and len(self.landsat_model.gnc.star_trackers) > 1:
                st_b_node.health = getattr(self.landsat_model.gnc.star_trackers[1], 'health', 100.0)
            
            # Payload (OLI2, TIRS2) - jelenleg nincs valós komponens, de lehet hozzáadni
            # Comm (X_BAND, S_BAND) - jelenleg nincs valós komponens, de lehet hozzáadni
        # Ha nincs landsat_model (pl. v3_fractal_sim), akkor NEM csinálunk semmit
        # (A meglévő szimulációk működnek tovább, ahogy eddig - NEM ÉRINTJÜK!)
        
        # 1. LÉPÉS: Bio-kód generálás az aktuális állapotból
        active_nodes = [n for n in self.nodes if n.health > 0]
        biocode_data = self.biocode_engine.generate_complete_biocode_sequence(
            self.nodes, active_nodes, self.mission_day
        )
        
        # 1.5. LÉPÉS: 3 .bio fájl mentése (műhold irányítás) + VALIDÁCIÓ
        try:
            save_result = self.biocode_file_manager.save_biocode_files(
                biocode_data, 
                mission_day=self.mission_day,
                biocode_engine=self.biocode_engine,
                validate=True  # Validálás titkosított fájlok szerint
            )
            biocode_data["_file_paths"] = save_result.get("file_paths", {})  # Fájl elérési utak hozzáadása
            biocode_data["_validation"] = save_result.get("validation", {})  # Validációs eredmények hozzáadása
            
            # Validációs eredmények logolása
            if save_result.get("validation", {}).get("passed", False):
                print(f"[BIOCODE FILES] Saved and validated: {list(save_result.get('file_paths', {}).values())}")
            else:
                validation_details = save_result.get("validation", {})
                print(f"[BIOCODE FILES] Warning: Files saved but validation failed: {validation_details}")
        except Exception as e:
            # Ha a fájl mentés sikertelen, folytatjuk (nem kritikus)
            print(f"Warning: Failed to save bio-code files: {e}")
        
        # 2. LÉPÉS: Bio-kód alapján döntés - a Level 3 bio-kódból dekódoljuk az értékeket
        # Ez biztosítja, hogy a bio-kód vezérelje a műholdat, nem az architektúra
        level3_hex = biocode_data.get("level3", {}).get("biocode", "")
        if level3_hex:
            level3_int = int(level3_hex, 16)
            decoded_level3 = self.biocode_engine.decode_level3_biocode(level3_int)
            action = decoded_level3.get("action", "CONTINUE_NOMINAL")
            feasibility = decoded_level3.get("feasibility_percent", 0)
            safety_margin = decoded_level3.get("safety_margin", 0)
        else:
            # Fallback (nem kellene előfordulnia)
            action = biocode_data.get("level3", {}).get("action", "CONTINUE_NOMINAL")
            feasibility = biocode_data.get("level3", {}).get("feasibility", 0)
            safety_margin = biocode_data.get("level3", {}).get("safety_margin", 0)
        
        # REGENERÁCIÓ ELŐTTI health értékek mentése (regen_monotonicity check-hez)
        previous_health_dict = {node.id: node.health for node in self.nodes}
        
        # 3. LÉPÉS: Bio-kód alapján determinisztikus öngyógyítás
        power_ok = any("power" in n.capabilities for n in active_nodes)
        events = []
        
        # Bio-kód alapján döntés: ha action engedélyezi, és van power, akkor regenerálunk
        should_regenerate = (
            power_ok and 
            action not in ["EMERGENCY_HALT", "SAFE_MODE"] and
            feasibility > 20  # Minimum feasibility küszöb
        )
        
        if should_regenerate:
            # Bio-kód alapján determinisztikus regeneráció
            for node in self.nodes:
                if node.health < 100:
                    old_h = node.health
                    # Safety margin alapján módosított regen rate (0-100% között)
                    adjusted_regen = self.regen_rate * (1 + safety_margin / 100.0)
                    node.health = min(100.0, node.health + adjusted_regen)
                    
                    if old_h == 0 and node.health > 0:
                        events.append(f"BIO-CODE: {node.name} re-initialized (biocode-driven).")
                    if node.health == 100.0 and old_h < 100.0:
                        events.append(f"SUCCESS: {node.name} restored (biocode-driven).")
                    elif node.health < 100 and len(events) < 2:
                        events.append(f"REGEN: {node.name} increasing (safety_margin={safety_margin}).")
        else:
            # Bio-kód tiltja a regenerációt
            if not power_ok:
                events.append("BIO-CODE: Regeneration blocked (no power capability).")
            elif action in ["EMERGENCY_HALT", "SAFE_MODE"]:
                events.append(f"BIO-CODE: Regeneration blocked (action={action}).")
            elif feasibility <= 20:
                events.append(f"BIO-CODE: Regeneration blocked (feasibility={feasibility:.1f}% too low).")
        
        # Bio-kód adatok átadása a _evaluate_feasibility-nek (bio-kód vezérlés)
        result = self._evaluate_feasibility([n for n in self.nodes if n.health > 0], events, biocode_data)
        
        # Ellenőrizzük, hogy van-e aktív szimuláció (van-e node ami nem 100%-os)
        has_damaged_nodes = any(n.health < 100.0 for n in self.nodes)
        
        # Szimuláció befejezésének ellenőrzése
        simulation_just_finished = False
        
        # Ha nincs power capability ÉS vannak sérült node-ok, akkor a szimuláció befejeződik
        # (mert nem lehet regenerálni, végtelen ciklusba ragadna)
        if not power_ok and has_damaged_nodes and self.simulation_active:
            # Szimuláció befejeződik: nincs power, nem lehet regenerálni
            self.simulation_active = False
            simulation_just_finished = True
            events.append("SIMULATION ENDED: No power capability - regeneration impossible.")
        elif not has_damaged_nodes and result["feasibility"] >= 100.0 and self.simulation_active:
            # Szimuláció most fejeződött be: minden node 100%-os
            self.simulation_active = False
            simulation_just_finished = True
        
        # 4. LÉPÉS: AUTOMATIKUS VALIDÁCIÓ (100% matematikai bizonyítás)
        # Csak akkor generálunk jelentést, ha van aktív szimuláció VAGY éppen most fejeződött be
        if self.simulation_active or simulation_just_finished:
            try:
                # Previous health dict átadása a validációs engine-nek (regen_monotonicity check-hez)
                self.validation_engine._previous_health_dict = previous_health_dict
                
                validation_result = self.validation_engine.validate_operation(
                    operation="regeneration",
                    nodes=self.nodes,
                    active_nodes=active_nodes,
                    feasibility=result["feasibility"],
                    biocode_data=biocode_data,  # Bio-kód MINDIG generálva (műhold működés része)
                    biocode_engine=self.biocode_engine,
                    regen_active=should_regenerate
                )
                
                # Previous health dict törlése a validáció után
                if hasattr(self.validation_engine, '_previous_health_dict'):
                    delattr(self.validation_engine, '_previous_health_dict')
                
                # Operations log frissítése
                self.report_generator.add_operation(
                    "regeneration",
                    validation_result,
                    self.nodes,
                    result["feasibility"],
                    biocode_data
                )
                
                # Validációs eredmények tárolása
                self.validation_results.append(validation_result)
                
                # Összesített jelentés generálása (bio-kód MINDIG van)
                # Csak akkor generálunk fájlt, ha a szimuláció éppen most fejeződött be
                # vagy ha aktív szimuláció (de csak ritkán, hogy ne generálódjon nonstop)
                aggregated_report = self.report_generator.generate_report(
                    self.nodes,
                    active_nodes,
                    biocode_data,
                    self.validation_results,
                    simulation_active=self.simulation_active,
                    force_save=simulation_just_finished  # Szimuláció végén mindig mentünk
                )
                
                # Validációs adatok hozzáadása az eredményhez
                result["validation"] = {
                    "status": validation_result["overall_status"],
                    "biocode_level3": biocode_data.get("level3", {}).get("biocode"),
                    "validation_id": aggregated_report.get("validation_id"),
                    "action": action,
                    "safety_margin": safety_margin,
                    "regeneration_driven_by_biocode": True
                }
                result["biocode"] = biocode_data  # Bio-kód mindig része az eredménynek
            except Exception as e:
                # Validációs hiba esetén warning, de művelet folytatódik
                print(f"[V3 VALIDATION] Warning: Validation failed: {e}")
                result["validation"] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        else:
            # Nincs aktív szimuláció, csak bio-kód adatok (validáció nélkül)
            result["biocode"] = biocode_data
            result["validation"] = {
                "status": "INACTIVE",
                "message": "Nincs aktív szimuláció - jelentés generálás kihagyva"
            }
        
        # Mission day növelése
        self.mission_day += 1
        
        return result

    def _migrate_master(self, active_nodes):
        """GIP alapú master választási logika."""
        for req in ["payload", "navigation", "comm", "power"]:  # ✅ VALÓDI: Landsat-9 kritikus alrendszerek
            for node in active_nodes:
                if req in node.capabilities:
                    node.is_master = True
                    return

    def _evaluate_feasibility(self, active_nodes, events=[], biocode_data=None):
        """
        Küldetés stabilitási mutatóinak kiszámítása.
        
        Ha van bio-kód adat, akkor azt használja (bio-kód vezérlés).
        Különben a régi módszert használja (backward compatibility).
        """
        if biocode_data and biocode_data.get("level3", {}).get("biocode"):
            # BIO-KÓD VEZÉRLÉS: A Level 3 bio-kódból dekódoljuk az értékeket
            level3_hex = biocode_data.get("level3", {}).get("biocode", "")
            level3_int = int(level3_hex, 16)
            decoded_level3 = self.biocode_engine.decode_level3_biocode(level3_int)
            
            feasibility_score = decoded_level3.get("feasibility_percent", 0)
            action = decoded_level3.get("action", "CONTINUE_NOMINAL")
            safety_margin = decoded_level3.get("safety_margin", 0)
            explanation = biocode_data.get("level3", {}).get("feasibility_explanation", 
                f"Bio-kod vezert szamitas: {feasibility_score:.2f}%")
        else:
            # BACKWARD COMPATIBILITY: Régi módszer (közvetlen számítás)
            feasibility_score, explanation = self.biocode_engine.calculate_weighted_feasibility(
                self.nodes, active_nodes
            )
            
            # Action meghatározása
            module_health_dict = {
                module: next(
                    (n.health for n in active_nodes if module in n.capabilities),
                    0.0
                )
                for module in self.biocode_engine.module_weights.keys()
            }
            action = self.biocode_engine.determine_action(feasibility_score, module_health_dict)
            
            # Safety margin
            critical_threshold = 40
            safety_margin = int(max(0, feasibility_score - critical_threshold))
        
        # Available capabilities (backward compatibility)
        available_caps = {cap for n in active_nodes for cap in n.capabilities}
        met = [r for r in self.mission_requirements if r in available_caps]
        
        return {
            "feasibility": round(feasibility_score, 2),
            "feasibility_explanation": explanation,
            "action": action,
            "safety_margin": safety_margin,
            "integrity_status": "VERIFIED" if feasibility_score == 100 else "DEGRADED",
            "met_requirements": met,
            "missing_requirements": [r for r in self.mission_requirements if r not in available_caps],
            "active_nodes_count": len(active_nodes),
            "nodes": [n.get_telemetry() for n in self.nodes],
            "events": events
        }
    
    def get_latest_validation_report(self):
        """Legutóbbi validációs jelentés lekérése"""
        return self.report_generator.get_latest_report()
    
    def increment_mission_day(self):
        """Mission day növelése"""
        self.mission_day += 1