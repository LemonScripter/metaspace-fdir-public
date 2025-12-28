"""
MetaSpace Validation Runner
Futtatja a validációs teszteket és generál validációs jegyzőkönyvet.
"""
import sys
import os
import json
import unittest
from datetime import datetime
from io import StringIO
from typing import Dict, List, Any

# Útvonal beállítás
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(base_dir)

from backend.tests.verify_core import TestMetaSpacePhysics
from backend.modules.landsat9 import Landsat9Model
from backend.modules.metaspace import MetaSpaceSimulator
from backend.modules.ekf_model import EKFSimulator


class ValidationReportGenerator:
    """Validációs jegyzőkönyv generátor"""
    
    def __init__(self):
        self.report_dir = os.path.join(base_dir, "validation_reports")
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir, exist_ok=True)
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Futtatja az összes validációs tesztet"""
        
        # Unit tesztek futtatása
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTests(loader.loadTestsFromTestCase(TestMetaSpacePhysics))
        
        # Teszt eredmények rögzítése
        stream = StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=2)
        result = runner.run(suite)
        
        # Eredmények összegyűjtése
        test_results = {
            'total_tests': result.testsRun,
            'passed': result.testsRun - len(result.failures) - len(result.errors),
            'failed': len(result.failures),
            'errors': len(result.errors),
            'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
            'failures': [{'test': str(f[0]), 'error': str(f[1])} for f in result.failures],
            'errors': [{'test': str(e[0]), 'error': str(e[1])} for e in result.errors],
            'output': stream.getvalue()
        }
        
        return test_results
    
    def run_integration_tests(self) -> Dict[str, Any]:
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
            satellite.battery_level = 15.0  # Kritikus akku
            satellite.power_generation_w = 1100.0  # Solar panel hiba
            satellite.gps_error = 60.0  # GPS hiba
            satellite.imu_accumulated_error = 0.6  # IMU drift
            
            metaspace = MetaSpaceSimulator(satellite)
            metaspace.update()
            
            # Ellenőrzések
            test_passed = (
                metaspace.health['power'] == 0 and  # FAULT
                metaspace.health['gps'] == 0 and  # FAULT
                metaspace.health['imu'] == 0 and  # FAULT
                metaspace.mission_feasibility == 0 and  # Kritikus
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
        
        # Teszt 2: EKF vs MetaSpace reakcióidő összehasonlítás
        try:
            satellite = Landsat9Model()
            satellite.battery_level = 100.0
            satellite.gps_error = 0.0
            satellite.imu_accumulated_error = 0.0
            satellite._gps_antenna_failed = False
            satellite._gps_error_accumulated = 0.0
            
            # GPS measurement függvény beállítása
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
            
            # Hiba injektálása
            satellite.inject_failure('solar_panel')
            satellite.power_generation_w = 1100.0
            
            ekf.update()
            metaspace.update()
            
            # MetaSpace azonnal észleli, EKF lassan
            test_passed = (
                metaspace.anomaly_detected == True and
                metaspace.detection_latency < 100 and  # <100ms
                metaspace.mission_feasibility == 0
            )
            
            results['tests'].append({
                'name': 'EKF vs MetaSpace Reakcióidő',
                'status': 'PASSED' if test_passed else 'FAILED',
                'details': {
                    'metaspace_detected': metaspace.anomaly_detected,
                    'metaspace_latency_ms': metaspace.detection_latency,
                    'ekf_detected': ekf.anomaly_detected,
                    'ekf_latency_minutes': ekf.detection_latency if hasattr(ekf, 'detection_latency') else None
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
    
    def generate_report(self) -> Dict[str, Any]:
        """Generálja a teljes validációs jegyzőkönyvet"""
        
        timestamp = datetime.now()
        
        # Unit tesztek futtatasa
        print("[VALIDATION] Futtatas: Unit tesztek...")
        unit_results = self.run_all_tests()
        
        # Integracios tesztek futtatasa
        print("[VALIDATION] Futtatas: Integracios tesztek...")
        integration_results = self.run_integration_tests()
        
        # Összesített eredmények
        total_tests = unit_results['total_tests'] + integration_results['total']
        total_passed = unit_results['passed'] + integration_results['passed']
        total_failed = unit_results['failed'] + integration_results['failed']
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Jegyzőkönyv összeállítása
        report = {
            'metadata': {
                'timestamp': timestamp.isoformat(),
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
                'errors': unit_results['errors'],
                'success_rate': round(unit_results['success_rate'], 2),
                'failures': unit_results['failures'],
                'errors_list': unit_results['errors']
            },
            'integration_tests': {
                'total': integration_results['total'],
                'passed': integration_results['passed'],
                'failed': integration_results['failed'],
                'success_rate': round(integration_results['success_rate'], 2),
                'test_details': integration_results['tests']
            },
            'recommendations': self._generate_recommendations(unit_results, integration_results)
        }
        
        # Mentés JSON formátumban
        report_filename = f"validation_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(self.report_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[VALIDATION] Jegyzokonyv mentve: {report_path}")
        
        return report
    
    def _generate_recommendations(self, unit_results: Dict, integration_results: Dict) -> List[str]:
        """Generál javaslatokat a validációs eredmények alapján"""
        recommendations = []
        
        if unit_results['failed'] > 0:
            recommendations.append(f"⚠️ {unit_results['failed']} unit teszt sikertelen. Javítás szükséges.")
        
        if integration_results['failed'] > 0:
            recommendations.append(f"⚠️ {integration_results['failed']} integrációs teszt sikertelen. Rendszer szintű ellenőrzés szükséges.")
        
        if unit_results['success_rate'] < 95:
            recommendations.append("⚠️ Unit teszt lefedettség alacsony (<95%). További tesztek hozzáadása ajánlott.")
        
        if integration_results['success_rate'] < 100:
            recommendations.append("⚠️ Integrációs teszt lefedettség nem 100%. További tesztek hozzáadása ajánlott.")
        
        if unit_results['success_rate'] >= 95 and integration_results['success_rate'] == 100:
            recommendations.append("✅ Minden teszt sikeres! A rendszer validálva van.")
        
        return recommendations


def run_validation() -> Dict[str, Any]:
    """Fő függvény a validáció futtatásához"""
    generator = ValidationReportGenerator()
    return generator.generate_report()


if __name__ == '__main__':
    print("=" * 70)
    print("METASPACE VALIDACIOS JEGYZOKONYV GENERALAS")
    print("=" * 70)
    report = run_validation()
    
    print("\n" + "=" * 70)
    print("OSSZEFOGLALO")
    print("=" * 70)
    print(f"Osszes teszt: {report['summary']['total_tests']}")
    print(f"Sikeres: {report['summary']['passed']}")
    print(f"Sikertelen: {report['summary']['failed']}")
    print(f"Sikeres arany: {report['summary']['success_rate']}%")
    print(f"Statusz: {report['summary']['status']}")
    print("=" * 70)

