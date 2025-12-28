"""
Teszt script a validációs hibák okainak feltárásához.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'backend')

from modules.v3_neural_core import NeuralFractalNetwork

def test_validation_failures():
    """Teszteljük, hogy milyen esetekben lehet FAILED művelet."""
    print("=" * 80)
    print("VALIDACIOS HIBAK OKAINAK FELTARASA")
    print("=" * 80)
    
    network = NeuralFractalNetwork()
    
    # Teszt 1: Normál műveletek
    print("\n[1] NORMAL MŰVELETEK TESZTELESE:")
    print("-" * 80)
    result1 = network.inject_chaos_and_calculate(['ST_A'])
    print(f"Chaos injection validation: {result1.get('validation', {}).get('status', 'N/A')}")
    if result1.get('validation', {}).get('status') == 'FAILED':
        print(f"  Hiba: {result1.get('validation', {}).get('errors', [])}")
    
    result2 = network.process_regeneration()
    print(f"Regeneration validation: {result2.get('validation', {}).get('status', 'N/A')}")
    if result2.get('validation', {}).get('status') == 'FAILED':
        print(f"  Hiba: {result2.get('validation', {}).get('errors', [])}")
    
    # Teszt 2: Bio-kód konzisztencia ellenőrzés
    print("\n[2] BIO-KOD KONZISZTENCIA TESZTELESE:")
    print("-" * 80)
    active_nodes = [n for n in network.nodes if n.health > 0]
    biocode_data = network.biocode_engine.generate_complete_biocode_sequence(
        network.nodes, active_nodes, network.mission_day
    )
    
    # Dekódoljuk a Level 3 bio-kódot
    level3_hex = biocode_data.get("level3", {}).get("biocode", "")
    if level3_hex:
        level3_int = int(level3_hex, 16)
        decoded = network.biocode_engine.decode_level3_biocode(level3_int)
        
        expected_feasibility = biocode_data.get("level3", {}).get("feasibility", 0)
        decoded_feasibility = decoded.get("feasibility_percent", 0)
        diff = abs(expected_feasibility - decoded_feasibility)
        
        print(f"Expected feasibility: {expected_feasibility:.2f}%")
        print(f"Decoded feasibility: {decoded_feasibility}%")
        print(f"Difference: {diff:.2f}%")
        print(f"Tolerance: 1.0%")
        print(f"Konzisztens: {diff <= 1.0}")
        
        if diff > 1.0:
            print(f"  FIGYELEM: Bio-kód konzisztencia hiba! Diff={diff:.2f}% > 1.0%")
    
    # Teszt 3: Edge case-ek
    print("\n[3] EDGE CASE TESZTELESE:")
    print("-" * 80)
    
    # Teszt 3.1: Minden node 0% health
    print("\n[3.1] Minden node 0% health:")
    for node in network.nodes:
        node.health = 0.0
    active_nodes = [n for n in network.nodes if n.health > 0]
    result3 = network._evaluate_feasibility(active_nodes, [], None)
    print(f"Feasibility: {result3['feasibility']}%")
    print(f"Action: {result3['action']}")
    
    # Teszt 3.2: Feasibility > 100% (nem kellene előfordulnia)
    print("\n[3.2] Feasibility > 100% teszt:")
    # Ez nem kellene előfordulnia, de teszteljük
    result4 = network.validation_engine.validate_operation(
        "test",
        network.nodes,
        active_nodes,
        150.0,  # > 100%
        None,
        None,
        False
    )
    print(f"Validation status: {result4['overall_status']}")
    if result4['overall_status'] == 'FAILED':
        print(f"  Hiba: {result4.get('errors', [])}")
    
    # Teszt 3.3: Bio-kód nélküli validáció
    print("\n[3.3] Bio-kód nélküli validáció:")
    result5 = network.validation_engine.validate_operation(
        "chaos_injection",
        network.nodes,
        active_nodes,
        50.0,
        None,  # Nincs bio-kód
        None,
        False
    )
    print(f"Validation status: {result5['overall_status']}")
    if result5['overall_status'] == 'FAILED':
        print(f"  Hiba: {result5.get('errors', [])}")
    
    # Teszt 4: Validációs jelentés elemzése
    print("\n[4] VALIDACIOS JELENTES ELEMZESE:")
    print("-" * 80)
    report = network.get_latest_validation_report()
    if report:
        print(f"Overall status: {report.get('overall_status', 'N/A')}")
        print(f"Total operations: {report.get('summary', {}).get('total_operations', 0)}")
        print(f"Passed operations: {report.get('summary', {}).get('passed_operations', 0)}")
        print(f"Failed operations: {report.get('summary', {}).get('failed_operations', 0)}")
        print(f"Success rate: {report.get('summary', {}).get('success_rate', 0):.1f}%")
        
        # Nézzük meg a műveletek logját
        if report.get('operations_log'):
            print("\nOperations log:")
            for i, op in enumerate(report['operations_log'][-5:], 1):  # Utolsó 5 művelet
                print(f"  {i}. {op.get('operation', 'N/A')}: {op.get('validation_status', 'N/A')}")
                if op.get('validation_status') == 'FAILED':
                    print(f"     Hiba: {op.get('validation_result', {}).get('errors', [])}")
    
    print("\n" + "=" * 80)
    print("TESZT BEFEJEZVE")
    print("=" * 80)

if __name__ == "__main__":
    test_validation_failures()

