"""Data encryption utilities for at-rest data protection."""

import base64
import os
from typing import Any, Dict, Optional

import boto3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config.settings import settings

class EncryptionService:
    """Service for handling data encryption and decryption."""
    
    def __init__(self):
        self.kms = boto3.client('kms',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self._key_cache: Dict[str, bytes] = {}
        
    def _get_data_key(self, key_id: str) -> bytes:
        """Get data key from KMS, using cache if available."""
        if key_id in self._key_cache:
            return self._key_cache[key_id]
            
        response = self.kms.generate_data_key(
            KeyId=key_id,
            KeySpec='AES_256'
        )
        
        # Cache the plaintext key
        self._key_cache[key_id] = response['Plaintext']
        
        return response['Plaintext']
        
    def encrypt_value(self, value: Any, context: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Encrypt a value using KMS-generated data key."""
        if not isinstance(value, (str, bytes)):
            value = str(value)
            
        # Get data key from KMS
        data_key = self._get_data_key(settings.KMS_KEY_ID)
        
        # Create Fernet instance for symmetric encryption
        f = Fernet(base64.urlsafe_b64encode(data_key))
        
        # Encrypt the value
        if isinstance(value, str):
            value = value.encode()
        encrypted_value = f.encrypt(value)
        
        return {
            'value': base64.b64encode(encrypted_value).decode('utf-8'),
            'context': context or {}
        }
        
    def decrypt_value(self, encrypted_data: Dict[str, str]) -> str:
        """Decrypt a value using KMS-generated data key."""
        # Get data key from KMS
        data_key = self._get_data_key(settings.KMS_KEY_ID)
        
        # Create Fernet instance for symmetric decryption
        f = Fernet(base64.urlsafe_b64encode(data_key))
        
        # Decrypt the value
        encrypted_value = base64.b64decode(encrypted_data['value'])
        decrypted_value = f.decrypt(encrypted_value)
        
        return decrypted_value.decode('utf-8')

# Global encryption service instance
encryption_service = EncryptionService()