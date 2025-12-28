"""
Navigációs Terv Modul - Landsat-9 Repülési Terv
Bio-kód vezérlésű navigációs terv végrehajtás.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class NavigationPlan:
    """
    Landsat-9 navigációs terv kezelése.
    Bio-kód alapú task végrehajtás.
    """
    
    def __init__(self, plan_data: Dict[str, Any]):
        """
        Args:
            plan_data: Navigációs terv JSON adatok
        """
        self.mission_day = plan_data.get("mission_day", 0)
        self.date = plan_data.get("date", "")
        self.orbits = plan_data.get("orbits", [])
        self.downlink_windows = plan_data.get("downlink_windows", [])
        
        # Orbit paraméterek (Landsat-9 spec)
        self.orbital_period_minutes = 99.0
        self.orbital_altitude_km = 705.0
        self.orbits_per_day = 14.5
    
    def get_current_orbit(self, current_time_utc: str) -> Optional[Dict[str, Any]]:
        """
        Jelenlegi orbit meghatározása időpont alapján.
        
        Args:
            current_time_utc: UTC időpont (HH:MM:SS formátum)
        
        Returns:
            Jelenlegi orbit dictionary vagy None
        """
        for orbit in self.orbits:
            orbit_start = orbit.get("start_time", "")
            orbit_end = orbit.get("end_time", "")
            
            if orbit_start <= current_time_utc <= orbit_end:
                return orbit
        
        return None
    
    def get_upcoming_tasks(self, current_time_utc: str, lookahead_minutes: int = 60) -> List[Dict[str, Any]]:
        """
        Közelgő task-ok lekérése.
        
        Args:
            current_time_utc: Jelenlegi UTC időpont
            lookahead_minutes: Hány perc előre nézzünk
        
        Returns:
            Közelgő task-ok listája
        """
        upcoming_tasks = []
        current_dt = self._time_to_datetime(current_time_utc)
        lookahead_dt = current_dt + timedelta(minutes=lookahead_minutes)
        
        for orbit in self.orbits:
            orbit_start = self._time_to_datetime(orbit.get("start_time", ""))
            orbit_end = self._time_to_datetime(orbit.get("end_time", ""))
            
            # Ha az orbit a lookahead időtartamon belül van
            if orbit_start <= lookahead_dt and orbit_end >= current_dt:
                for task in orbit.get("tasks", []):
                    task_window = task.get("window", {})
                    task_start = self._time_to_datetime(task_window.get("start", ""))
                    task_end = self._time_to_datetime(task_window.get("end", ""))
                    
                    # Ha a task a lookahead időtartamon belül van
                    if task_start <= lookahead_dt and task_end >= current_dt:
                        upcoming_tasks.append(task)
        
        return sorted(upcoming_tasks, key=lambda t: t.get("window", {}).get("start", ""))
    
    def get_task_at_time(self, time_utc: str) -> Optional[Dict[str, Any]]:
        """
        Adott időpontban végrehajtandó task meghatározása.
        
        Args:
            time_utc: UTC időpont (HH:MM:SS formátum)
        
        Returns:
            Task dictionary vagy None
        """
        for orbit in self.orbits:
            for task in orbit.get("tasks", []):
                task_window = task.get("window", {})
                task_start = task_window.get("start", "")
                task_end = task_window.get("end", "")
                
                if task_start <= time_utc <= task_end:
                    return task
        
        return None
    
    def _time_to_datetime(self, time_str: str) -> datetime:
        """
        HH:MM:SS string konvertálása datetime objektummá (ma dátummal).
        """
        try:
            hour, minute, second = map(int, time_str.split(":"))
            today = datetime.now().replace(hour=hour, minute=minute, second=second, microsecond=0)
            return today
        except:
            return datetime.now()
    
    @staticmethod
    def load_from_file(filepath: str) -> 'NavigationPlan':
        """
        Navigációs terv betöltése JSON fájlból.
        
        Args:
            filepath: JSON fájl elérési útja
        
        Returns:
            NavigationPlan objektum
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            plan_data = json.load(f)
        return NavigationPlan(plan_data)
    
    @staticmethod
    def create_sample_plan() -> 'NavigationPlan':
        """
        Minta navigációs terv létrehozása (teszteléshez).
        """
        sample_data = {
            "mission_day": 150,
            "date": "2025-06-15",
            "orbits": [
                {
                    "orbit_number": 1,
                    "start_time": "00:00:00",
                    "end_time": "01:39:00",
                    "tasks": [
                        {
                            "task_id": "IMG_001",
                            "type": "imaging",
                            "target": {
                                "name": "Amazonas Rainforest",
                                "coordinates": {"lat": -3.4653, "lon": -62.2159},
                                "priority": "HIGH"
                            },
                            "window": {
                                "start": "00:15:00",
                                "end": "00:20:00",
                                "duration_seconds": 300
                            },
                            "required_nodes": ["OLI2", "TIRS2", "ST_A", "ST_B"],
                            "required_modules": ["payload", "navigation"],
                            "power_consumption_w": 1200,
                            "data_production_gb": 15.2
                        },
                        {
                            "task_id": "ATT_001",
                            "type": "attitude_maneuver",
                            "purpose": "Point payload at target",
                            "window": {
                                "start": "00:30:00",
                                "end": "00:31:00",
                                "duration_seconds": 60
                            },
                            "required_nodes": ["ST_A", "ST_B", "OBC"],
                            "required_modules": ["navigation"],
                            "power_consumption_w": 800
                        }
                    ],
                    "eclipse": {
                        "entry": "01:00:00",
                        "exit": "01:35:00",
                        "duration_minutes": 35
                    }
                }
            ],
            "downlink_windows": [
                {
                    "window_id": "DL_001",
                    "station": "Alaska (Fairbanks)",
                    "window": {
                        "start": "12:00:00",
                        "end": "12:15:00",
                        "duration_seconds": 900
                    },
                    "required_nodes": ["X_BAND", "OBC"],
                    "data_rate_mbps": 800,
                    "priority": "HIGH"
                }
            ]
        }
        
        return NavigationPlan(sample_data)

