import os
import json
import sys
from cryptography.fernet import Fernet

class SecureBridge:
    _loaded_modules = {}
    _initialized = False

    @staticmethod
    def initialize(key_path_or_content=None):
        """
        Betölti és dekódolja a MetaSpace magot a memóriába.
        """
        if SecureBridge._initialized:
            return True

        key = None
        
        # 1. Próbáljuk meg környezeti változóból
        env_key = os.environ.get("METASPACE_MASTER_KEY")
        if env_key:
            key = env_key.encode()
        
        # 2. Ha nincs, próbáljuk fájlból
        elif key_path_or_content and os.path.exists(key_path_or_content):
            with open(key_path_or_content, "rb") as kf:
                key = kf.read()
        
        if not key:
            print("[SECURE BRIDGE] ERROR: No Master Key found!")
            return False

        try:
            cipher = Fernet(key)
            
            # A titkosított vault keresése
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            vault_path = os.path.join(base_dir, "secrets", "metaspace.vault")
            
            if not os.path.exists(vault_path):
                print(f"[SECURE BRIDGE] ERROR: Vault not found at {vault_path}")
                return False

            with open(vault_path, "rb") as f:
                encrypted_data = f.read()

            decrypted_json = cipher.decrypt(encrypted_data)
            payload = json.loads(decrypted_json)
            
            print("[METASPACE] Secure Core decrypted. Loading modules into RAM...")
            
            # Modulok betöltése
            for module_name, source_code in payload.items():
                module_scope = {}
                exec(source_code, module_scope)
                SecureBridge._loaded_modules[module_name] = module_scope
                print(f"  [SECURE LOAD] Module loaded: {module_name}")

            SecureBridge._initialized = True
            return True  # <--- FONTOS: Ez jelzi a sikert a hívónak!

        except Exception as e:
            print(f"[SECURE BRIDGE] CRITICAL FAILURE: {str(e)}")
            return False

    @staticmethod
    def get_class(module_name, class_name):
        if not SecureBridge._initialized:
            raise RuntimeError("MetaSpace Core is locked! Call initialize() first.")
        
        if module_name not in SecureBridge._loaded_modules:
            raise ValueError(f"Module '{module_name}' not found.")
            
        module = SecureBridge._loaded_modules[module_name]
        if class_name not in module:
            raise ValueError(f"Class '{class_name}' not found in module '{module_name}'.")
            
        return module[class_name]