# verify_env.py
import sys
import os

print("--- METASPACE KÖRNYEZET ELLENŐRZÉSE ---")

# 1. Python verzió ellenőrzése
print(f"[OK] Python verzió: {sys.version.split()[0]}")

# 2. Import ellenőrzés
try:
    import flask
    import numpy
    import cryptography
    from cryptography.fernet import Fernet
    print("[OK] Függőségek (Flask, Numpy, Crypto) betöltve.")
except ImportError as e:
    print(f"[HIBA] Hiányzó modul: {e}")
    sys.exit(1)

# 3. Secure Bridge és Kulcs tesztelése
print("\n--- SECURE ENCLAVE TESZT ---")
key_file = "metaspace_master.key"
vault_file = os.path.join("backend", "secrets", "metaspace.vault")

if not os.path.exists(key_file):
    print(f"[HIBA] Nem található a kulcsfájl: {key_file}")
    print("Futtasd le a tools/encryptor.py-t először!")
    sys.exit(1)

if not os.path.exists(vault_file):
    print(f"[HIBA] Nem található a vault fájl: {vault_file}")
    sys.exit(1)

print("[OK] Kulcs és Vault fájlok jelen vannak.")

# Próbáljuk meg betölteni a Bridge-et
sys.path.append(os.path.join(os.getcwd(), "backend"))
try:
    from modules.secure_bridge import SecureBridge
    
    print("Kísérlet a titkos mag feloldására...")
    if SecureBridge.initialize(key_file):
        print("[SIKER] A Secure Bridge sikeresen inicializálva!")
        
        # Próbáljunk lekérni egy titkos osztályt
        try:
            GSC = SecureBridge.get_class("VHDL_Synth", "GlobalSynchronousClock")
            print(f"[SIKER] Titkos osztály elérve: {GSC.__name__}")
            print("\nA RENDSZER KÉSZEN ÁLL A SZIMULÁCIÓRA.")
        except Exception as e:
            print(f"[HIBA] Osztály lekérési hiba: {e}")
    else:
        print("[HIBA] A Secure Bridge inicializálása sikertelen (rossz kulcs?).")

except Exception as e:
    print(f"[KRITIKUS HIBA] {e}")