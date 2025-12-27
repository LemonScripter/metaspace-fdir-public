import uuid

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
    def __init__(self):
        self.mission_requirements = ["logic", "navigation", "power", "comm"]
        self.nodes = []
        self.regen_rate = 8.5 # Alapértelmezett Bio-Code sebesség
        self.reset_constellation()

    def reset_constellation(self):
        """Konstelláció alaphelyzetbe állítása."""
        self.nodes = [
            HolographicNode("Main CPU Core", "CPU", "compute", ["logic", "storage"]),
            HolographicNode("Star Tracker A", "ST_A", "sensor", ["navigation"]),
            HolographicNode("Star Tracker B", "ST_B", "sensor", ["navigation"]),
            HolographicNode("Power Controller", "EPS", "actuator", ["power"]),
            HolographicNode("High-Gain Antenna", "ANT", "sensor", ["comm"]),
            HolographicNode("Battery Array", "BATT", "sensor", ["power"])
        ]
        self.nodes[0].is_master = True

    def set_regen_rate(self, rate):
        """A regeneráció sebességének dinamikus módosítása."""
        try:
            self.regen_rate = float(rate)
        except (ValueError, TypeError):
            self.regen_rate = 8.5

    def inject_chaos_and_calculate(self, killed_ids):
        """Káosz injektálás és master migration."""
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

        return self._evaluate_feasibility(active_nodes, events)

    def process_regeneration(self):
        """Szuverén regenerációs ciklus a beállított rátával."""
        active_nodes = [n for n in self.nodes if n.health > 0]
        power_ok = any("power" in n.capabilities for n in active_nodes)
        events = []
        
        if power_ok:
            for node in self.nodes:
                if node.health < 100:
                    old_h = node.health
                    node.health = min(100.0, node.health + self.regen_rate)
                    if old_h == 0 and node.health > 0:
                        events.append(f"BIO-CODE: {node.name} re-initialized.")
                    if node.health == 100.0 and old_h < 100.0:
                        events.append(f"SUCCESS: {node.name} restored.")
                    elif node.health < 100 and len(events) < 2:
                        events.append(f"REGEN: {node.name} increasing.")
        
        return self._evaluate_feasibility([n for n in self.nodes if n.health > 0], events)

    def _migrate_master(self, active_nodes):
        """GIP alapú master választási logika."""
        for req in ["logic", "navigation", "comm", "power"]:
            for node in active_nodes:
                if req in node.capabilities:
                    node.is_master = True
                    return

    def _evaluate_feasibility(self, active_nodes, events=[]):
        """Küldetés stabilitási mutatóinak kiszámítása."""
        available_caps = {cap for n in active_nodes for cap in n.capabilities}
        met = [r for r in self.mission_requirements if r in available_caps]
        score = (len(met) / len(self.mission_requirements)) * 100
        return {
            "feasibility": score,
            "integrity_status": "VERIFIED" if score == 100 else "DEGRADED",
            "met_requirements": met,
            "missing_requirements": [r for r in self.mission_requirements if r not in available_caps],
            "active_nodes_count": len(active_nodes),
            "nodes": [n.get_telemetry() for n in self.nodes],
            "events": events
        }