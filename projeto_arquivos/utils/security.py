"""
Módulo de Segurança do Sistema
Gerencia criptografia, licenças e proteções
"""

from cryptography.fernet import Fernet
import base64
import platform
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import json
import os

class SecureConfig:
    """Gerencia strings sensíveis criptografadas"""
    
    @staticmethod
    def get_key():
        """Gera chave baseada no sistema"""
        machine_id = platform.node() + platform.machine()
        key = base64.urlsafe_b64encode(machine_id.encode()[:32].ljust(32, b'0'))
        return key
    
    @staticmethod
    def encrypt(text: str) -> str:
        """Criptografa texto"""
        f = Fernet(SecureConfig.get_key())
        return f.encrypt(text.encode()).decode()
    
    @staticmethod
    def decrypt(encrypted: str) -> str:
        """Descriptografa texto"""
        f = Fernet(SecureConfig.get_key())
        return f.decrypt(encrypted.encode()).decode()


class LicenseManager:
    """Gerencia licenças do sistema"""
    
    def __init__(self):
        self.license_file = Path('license.dat')
        self.secret = "SGP2.0-SECRETO-2026"  # Mudar para algo único
    
    def get_machine_id(self):
        """Obtém ID único da máquina"""
        machine_info = f"{platform.node()}{platform.machine()}{platform.processor()}"
        return hashlib.sha256(machine_info.encode()).hexdigest()[:16]
    
    def generate_license_key(self, machine_id, expiration_days=365):
        """Gera chave de licença"""
        expiration = (datetime.now() + timedelta(days=expiration_days)).isoformat()
        data = f"{machine_id}|{expiration}|{self.secret}"
        license_hash = hashlib.sha256(data.encode()).hexdigest()
        return f"{machine_id}-{license_hash[:8]}-{license_hash[8:16]}"
    
    def verify_license(self):
        """Verifica licença"""
        # Se arquivo de licença não existe, permitir (modo desenvolvimento)
        if not self.license_file.exists():
            # Em produção, mudar para return False, "Licença não encontrada"
            return True, "Modo desenvolvimento"
        
        try:
            license_data = json.loads(self.license_file.read_text())
            machine_id = self.get_machine_id()
            
            if license_data.get('machine_id') != machine_id:
                return False, "Licença inválida para esta máquina"
            
            # Verificar expiração se houver
            if 'expiration' in license_data:
                expiration = datetime.fromisoformat(license_data.get('expiration'))
                if datetime.now() > expiration:
                    return False, "Licença expirada"
            
            return True, "Licença válida"
        
        except Exception as e:
            return False, f"Erro: {e}"
    
    def save_license(self, license_key):
        """Salva licença"""
        parts = license_key.split('-')
        if len(parts) != 3:
            return False, "Formato inválido"
        
        machine_id = parts[0]
        if machine_id != self.get_machine_id():
            return False, "Licença inválida para este computador"
        
        license_data = {
            'machine_id': machine_id,
            'key': license_key,
            'activated_at': datetime.now().isoformat()
        }
        
        self.license_file.write_text(json.dumps(license_data, indent=2))
        return True, "Licença ativada"
