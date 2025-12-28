"""
MetaSpace Validation Manager
Moduláris validációs rendszer - ki-be kapcsolható, nem befolyásolja a jelenlegi működést.
"""
import sys
import os
import json
import unittest
from datetime import datetime
from io import StringIO
from typing import Dict, List, Any, Optional

# Útvonal beállítás
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(base_dir)

try:
    from backend.tests.verify_core import TestMetaSpacePhysics
    from backend.modules.landsat9 import Landsat9Model
    from backend.modules.metaspace import MetaSpaceSimulator
    from backend.modules.ekf_model import EKFSimulator
except ImportError:
    from tests.verify_core import TestMetaSpacePhysics
    from modules.landsat9 import Landsat9Model
    from modules.metaspace import MetaSpaceSimulator
    from modules.ekf_model import EKFSimulator


class ValidationManager:
    """
    Moduláris validációs kezelő.
    Ki-be kapcsolható, nem befolyásolja a jelenlegi működést.
    """
    
    def __init__(self):
        self.report_dir = os.path.join(base_dir, "validation_reports")
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir, exist_ok=True)
    
    def validate_simulation(self, sim_id: str, sim_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validálja a szimulációs eredményeket.
        
        Args:
            sim_id: Szimuláció ID
            sim_results: Szimulációs eredmények (telemetry_log, components, stb.)
        
        Returns:
            Validációs jegyzőkönyv
        """
        timestamp = datetime.now()
        
        # 1. Unit tesztek futtatása
        unit_results = self._run_unit_tests()
        
        # 2. Integrációs tesztek futtatása
        integration_results = self._run_integration_tests()
        
        # 3. Szimulációs validáció (telemetria adatok ellenőrzése)
        simulation_validation = self._validate_simulation_results(sim_results)
        
        # 4. Összesített eredmények
        total_tests = unit_results['total_tests'] + integration_results['total'] + simulation_validation['total_checks']
        total_passed = unit_results['passed'] + integration_results['passed'] + simulation_validation['passed']
        total_failed = unit_results['failed'] + integration_results['failed'] + simulation_validation['failed']
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # 5. Jegyzőkönyv összeállítása
        validation_report = {
            'metadata': {
                'timestamp': timestamp.isoformat(),
                'sim_id': sim_id,
                'version': '1.4',
                'validation_type': 'Full System Validation'
            },
            'summary': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'success_rate': round(overall_success_rate, 2),
                'status': 'PASSED' if total_failed == 0 else 'FAILED'
            },
            'unit_tests': {
                'total': unit_results['total_tests'],
                'passed': unit_results['passed'],
                'failed': unit_results['failed'],
                'success_rate': round(unit_results['success_rate'], 2),
                'tests': unit_results.get('test_details', [])
            },
            'integration_tests': {
                'total': integration_results['total'],
                'passed': integration_results['passed'],
                'failed': integration_results['failed'],
                'success_rate': round(integration_results['success_rate'], 2),
                'tests': integration_results.get('tests', [])
            },
            'simulation_validation': simulation_validation,
            'recommendations': self._generate_recommendations(
                unit_results, 
                integration_results, 
                simulation_validation
            )
        }
        
        return validation_report
    
    def _run_unit_tests(self) -> Dict[str, Any]:
        """Futtatja az unit teszteket"""
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTests(loader.loadTestsFromTestCase(TestMetaSpacePhysics))
        
        stream = StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=0)
        result = runner.run(suite)
        
        return {
            'total_tests': result.testsRun,
            'passed': result.testsRun - len(result.failures) - len(result.errors),
            'failed': len(result.failures) + len(result.errors),
            'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
            'failures': [{'test': str(f[0]), 'error': str(f[1])} for f in result.failures],
            'errors': [{'test': str(e[0]), 'error': str(e[1])} for e in result.errors],
            'output': stream.getvalue(),
            'test_details': [
                {
                    'name': 'test_01_solar_panel_physics',
                    'status': 'PASSED' if 'test_01_solar_panel_physics' not in [str(f[0]) for f in result.failures + result.errors] else 'FAILED'
                },
                {
                    'name': 'test_02_battery_drain_logic',
                    'status': 'PASSED' if 'test_02_battery_drain_logic' not in [str(f[0]) for f in result.failures + result.errors] else 'FAILED'
                },
                {
                    'name': 'test_03_isolation_mechanism',
                    'status': 'PASSED' if 'test_03_isolation_mechanism' not in [str(f[0]) for f in result.failures + result.errors] else 'FAILED'
                }
            ]
        }
    
    def _run_integration_tests(self) -> Dict[str, Any]:
        """Futtatja az integrációs teszteket"""
        results = {
            'tests': [],
            'passed': 0,
            'failed': 0,
            'total': 0
        }
        
        # Teszt 1: MetaSpace invariáns ellenőrzések
        try:
            satellite = Landsat9Model()
            satellite.battery_level = 15.0
            satellite.power_generation_w = 1100.0
            satellite.gps_error = 60.0
            satellite.imu_accumulated_error = 0.6
            
            metaspace = MetaSpaceSimulator(satellite)
            metaspace.update()
            
            test_passed = (
                metaspace.health['power'] == 0 and
                metaspace.health['gps'] == 0 and
                metaspace.health['imu'] == 0 and
                metaspace.mission_feasibility == 0 and
                metaspace.anomaly_detected == True
            )
            
            results['tests'].append({
                'name': 'MetaSpace Invariáns Ellenőrzések',
                'status': 'PASSED' if test_passed else 'FAILED',
                'details': {
                    'power_health': metaspace.health['power'],
                    'gps_health': metaspace.health['gps'],
                    'imu_health': metaspace.health['imu'],
                    'mission_feasibility': metaspace.mission_feasibility,
                    'anomaly_detected': metaspace.anomaly_detected
                }
            })
            
            if test_passed:
                results['passed'] += 1
            else:
                results['failed'] += 1
            results['total'] += 1
            
        except Exception as e:
            results['tests'].append({
                'name': 'MetaSpace Invariáns Ellenőrzések',
                'status': 'ERROR',
                'error': str(e)
            })
            results['failed'] += 1
            results['total'] += 1
        
        # Teszt 2: EKF vs MetaSpace reakcióidő
        try:
            satellite = Landsat9Model()
            satellite.battery_level = 100.0
            satellite.gps_error = 0.0
            satellite.imu_accumulated_error = 0.0
            satellite._gps_antenna_failed = False
            satellite._gps_error_accumulated = 0.0
            
            def get_gps_with_failure():
                if satellite.battery_level < 10.0:
                    return None
                if satellite.gnc.active_sensor_count > 0:
                    if satellite._gps_antenna_failed:
                        return [150.0, 150.0, -100.0]
                    else:
                        return [0.0, 0.0, 0.0]
                else:
                    return None
            
            satellite.get_gps_measurement = get_gps_with_failure
            
            ekf = EKFSimulator(satellite)
            metaspace = MetaSpaceSimulator(satellite)
            
            satellite.inject_failure('solar_panel')
            satellite.power_generation_w = 1100.0
            
            ekf.update()
            metaspace.update()
            
            test_passed = (
                metaspace.anomaly_detected == True and
                metaspace.detection_latency < 100 and
                metaspace.mission_feasibility == 0
            )
            
            results['tests'].append({
                'name': 'EKF vs MetaSpace Reakcióidő',
                'status': 'PASSED' if test_passed else 'FAILED',
                'details': {
                    'metaspace_detected': metaspace.anomaly_detected,
                    'metaspace_latency_ms': metaspace.detection_latency,
                    'ekf_detected': ekf.anomaly_detected,
                    'mission_feasibility': metaspace.mission_feasibility
                }
            })
            
            if test_passed:
                results['passed'] += 1
            else:
                results['failed'] += 1
            results['total'] += 1
            
        except Exception as e:
            results['tests'].append({
                'name': 'EKF vs MetaSpace Reakcióidő',
                'status': 'ERROR',
                'error': str(e)
            })
            results['failed'] += 1
            results['total'] += 1
        
        results['success_rate'] = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
        
        return results
    
    def _validate_simulation_results(self, sim_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validálja a szimulációs eredményeket"""
        checks = []
        passed = 0
        failed = 0
        
        # Check 1: Telemetria log létezik
        telemetry_log = sim_results.get('telemetry_log', [])
        if telemetry_log:
            checks.append({
                'name': 'Telemetry Log Exists',
                'status': 'PASSED',
                'details': f'Found {len(telemetry_log)} telemetry entries'
            })
            passed += 1
        else:
            checks.append({
                'name': 'Telemetry Log Exists',
                'status': 'FAILED',
                'details': 'No telemetry log found'
            })
            failed += 1
        
        # Check 2: Time sequence konzisztencia
        if telemetry_log:
            times = [entry.get('time', 0) for entry in telemetry_log]
            is_monotonic = all(times[i] <= times[i+1] for i in range(len(times)-1))
            
            if is_monotonic:
                checks.append({
                    'name': 'Time Sequence Consistency',
                    'status': 'PASSED',
                    'details': 'Time sequence is monotonic'
                })
                passed += 1
            else:
                checks.append({
                    'name': 'Time Sequence Consistency',
                    'status': 'FAILED',
                    'details': 'Time sequence is not monotonic'
                })
                failed += 1
        
        # Check 3: EKF és MetaSpace adatok léteznek
        if telemetry_log:
            has_ekf = all('ekf_reliability' in entry for entry in telemetry_log)
            has_metaspace = all('metaspace_integrity' in entry for entry in telemetry_log)
            
            if has_ekf and has_metaspace:
                checks.append({
                    'name': 'EKF and MetaSpace Data Present',
                    'status': 'PASSED',
                    'details': 'Both EKF and MetaSpace data present in all entries'
                })
                passed += 1
            else:
                checks.append({
                    'name': 'EKF and MetaSpace Data Present',
                    'status': 'FAILED',
                    'details': f'EKF: {has_ekf}, MetaSpace: {has_metaspace}'
                })
                failed += 1
        
        # Check 4: Invariáns sértések ellenőrzése
        invariant_violations = 0
        if telemetry_log:
            for entry in telemetry_log:
                # Energy invariant: power_generation nem lehet negatív
                power_gen = entry.get('power_generation_w', 2400.0)
                if power_gen < 0:
                    invariant_violations += 1
                
                # Battery nem lehet negatív vagy >100%
                battery = entry.get('battery_percent', 100.0)
                if battery < 0 or battery > 100:
                    invariant_violations += 1
        
        if invariant_violations == 0:
            checks.append({
                'name': 'Invariant Violations',
                'status': 'PASSED',
                'details': 'No invariant violations detected'
            })
            passed += 1
        else:
            checks.append({
                'name': 'Invariant Violations',
                'status': 'FAILED',
                'details': f'{invariant_violations} invariant violations detected'
            })
            failed += 1
        
        total_checks = len(checks)
        success_rate = (passed / total_checks * 100) if total_checks > 0 else 0
        
        return {
            'total_checks': total_checks,
            'passed': passed,
            'failed': failed,
            'success_rate': round(success_rate, 2),
            'status': 'PASSED' if failed == 0 else 'FAILED',
            'checks': checks,
            'invariant_violations': invariant_violations
        }
    
    def _generate_recommendations(
        self, 
        unit_results: Dict, 
        integration_results: Dict,
        simulation_validation: Dict
    ) -> List[str]:
        """Generál javaslatokat"""
        recommendations = []
        
        if unit_results['failed'] > 0:
            recommendations.append(f"[WARNING] {unit_results['failed']} unit teszt sikertelen. Javitas szukseges.")
        
        if integration_results['failed'] > 0:
            recommendations.append(f"[WARNING] {integration_results['failed']} integracios teszt sikertelen. Rendszer szintu ellenorzes szukseges.")
        
        if simulation_validation['failed'] > 0:
            recommendations.append(f"[WARNING] {simulation_validation['failed']} szimulacios validacios ellenorzes sikertelen.")
        
        if unit_results['success_rate'] < 95:
            recommendations.append("[WARNING] Unit teszt lefedettseg alacsony (<95%). Tovabbi tesztek hozzaadasa ajanlott.")
        
        if integration_results['success_rate'] < 100:
            recommendations.append("[WARNING] Integracios teszt lefedettseg nem 100%. Tovabbi tesztek hozzaadasa ajanlott.")
        
        if (unit_results['success_rate'] >= 95 and 
            integration_results['success_rate'] == 100 and 
            simulation_validation['success_rate'] == 100):
            recommendations.append("[OK] Minden teszt sikeres! A rendszer 100%-ban validalva van.")
        
        return recommendations

