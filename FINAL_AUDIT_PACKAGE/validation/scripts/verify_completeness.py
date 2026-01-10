import os
import json
import sys

def load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return None

def verify_completeness():
    print("===================================================")
    print("      MetaSpace Audit Completeness Verification    ")
    print("===================================================")
    print(f"Timestamp: {os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}")
    print("---------------------------------------------------")

    # Define the Audit Requirements (Critical Gaps)
    requirements = [
        {
            "id": "GAP-1.1",
            "name": "Code Verification (MMS)",
            "file": "results/mms_verification_report.json",
            "check": lambda d: d['status'] == 'PASS' and d['observed_order'] > 3.8
        },
        {
            "id": "GAP-2.1",
            "name": "Model Validation (Physics)",
            "file": "results/model_validation_report.json",
            "check": lambda d: d['status'] == 'PASS' and d['metrics']['correlation'] > 0.99
        },
        {
            "id": "GAP-3.1",
            "name": "SIL 3 Safety Assessment",
            "file": "results/safety_sil3_report.json",
            "check": lambda d: d['results']['sil_classification'] == 'SIL 3' and d['results']['pfd_avg'] < 1e-3
        },
        {
            "id": "GAP-4.1",
            "name": "FDIR Performance Metrics",
            "file": "results/fdir_performance_report.json",
            "check": lambda d: all(m['missed_detection_count'] == 0 for m in d['metrics'].values())
        }
    ]

    all_passed = True
    
    print(f"{ 'GAP ID':<10} | { 'Requirement Name':<30} | { 'Status':<10} | { 'Details'}")
    print("-" * 80)

    for req in requirements:
        data = load_json(req['file'])
        
        status = "MISSING"
        details = "File not found"
        
        if data:
            try:
                if req['check'](data):
                    status = "PASS"
                    if req['id'] == "GAP-1.1":
                        details = f"Order: {data['observed_order']:.2f}, GCI: {data['gci_percent']:.2f}%"
                    elif req['id'] == "GAP-2.1":
                        details = f"Corr: {data['metrics']['correlation']:.4f}, MAE: {data['metrics']['mae_percent']:.2f}%"
                    elif req['id'] == "GAP-3.1":
                        details = f"PFD: {data['results']['pfd_avg']:.2e} ({data['results']['sil_classification']})"
                    elif req['id'] == "GAP-4.1":
                        mean_ttd = data['metrics']['gps_antenna']['mean_ttd_ms']
                        details = f"Mean TTD: {mean_ttd:.2f}ms, 100% Detection"
                else:
                    status = "FAIL"
                    details = "Criteria not met in report"
                    all_passed = False
            except Exception as e:
                status = "ERROR"
                details = str(e)
                all_passed = False
        else:
            all_passed = False

        color_code = "" # No ANSI in Windows generic shell usually safe, or use simple text
        print(f"{req['id']:<10} | {req['name']:<30} | {status:<10} | {details}")

    print("-" * 80)
    
    if all_passed:
        print("\n>> VERDICT: READY FOR REPOSITORY COMMIT.")
        print("   All Critical Gaps are addressed with verified artifacts.")
    else:
        print("\n>> VERDICT: INCOMPLETE.")
        print("   Please fix the MISSING or FAIL items before committing.")
    
    print("===================================================")

if __name__ == "__main__":
    verify_completeness()
