# tools/encryptor.py
import json
import os
from cryptography.fernet import Fernet

# 1. Kulcs generálása (VAGY betöltése, ha már van)
KEY_FILE = "metaspace_master.key"

if not os.path.exists(KEY_FILE):
    print("Új mesterkulcs generálása...")
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as kf:
        kf.write(key)
else:
    print("Meglévő mesterkulcs használata...")
    with open(KEY_FILE, "rb") as kf:
        key = kf.read()

cipher = Fernet(key)

# 2. A nyers fájlok beolvasása
secret_payload = {}
raw_dir = "raw_secrets"

# Itt definiáljuk a fájlneveket és a modulneveket, ahogy hivatkozni akarunk rájuk
files_to_encrypt = {
    "core_v14_gsc.py": "VHDL_Synth",
    "sovereign_swarm_v13.py": "Sovereign_Shield",
    "logic_lock_v10.py": "Logic_Lock"
}

print("Fájlok beolvasása és csomagolása...")
for filename, module_name in files_to_encrypt.items():
    path = os.path.join(raw_dir, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            secret_payload[module_name] = f.read()
            print(f"  [OK] {filename} -> Modul: {module_name}")
    else:
        print(f"  [HIBA] Nem található: {path}")
        exit(1)

# 3. Titkosítás
json_data = json.dumps(secret_payload).encode("utf-8")
encrypted_data = cipher.encrypt(json_data)

# 4. Mentés a backend titkos mappájába
output_dir = "backend/secrets"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "metaspace.vault")

with open(output_path, "wb") as f:
    f.write(encrypted_data)

print(f"\nSIKER! A titkosított tároló létrejött: {output_path}")
print(f"FIGYELEM: A '{KEY_FILE}' fájlt SOHA ne töltsd fel a GitHubra!")
print("Tarts belőle biztonsági másolatot offline (pl. pendrive-on).")