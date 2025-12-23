"""
Encryption utilities for securing biometric data.
"""
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import numpy as np

from config.settings import settings


class EncryptionService:
    """Service for encrypting and decrypting biometric descriptors."""
    
    def __init__(self, key: str = None):
        """Initialize encryption service with a key."""
        self.key = key or settings.encryption_key
        self._cipher = self._create_cipher()
    
    def _create_cipher(self) -> Fernet:
        """Create a Fernet cipher from the encryption key."""
        # Derive a proper key from the encryption key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'biometric-cicd-salt',  # In production, use a random salt stored securely
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.key.encode()))
        return Fernet(key)
    
    def encrypt_descriptor(self, descriptor: np.ndarray) -> bytes:
        """
        Encrypt a biometric descriptor.
        
        Args:
            descriptor: NumPy array containing biometric features
            
        Returns:
            Encrypted bytes
        """
        # Convert numpy array to bytes
        descriptor_bytes = descriptor.tobytes()
        # Encrypt
        encrypted = self._cipher.encrypt(descriptor_bytes)
        return encrypted
    
    def decrypt_descriptor(self, encrypted_data: bytes, shape: tuple, dtype=np.float64) -> np.ndarray:
        """
        Decrypt a biometric descriptor.
        
        Args:
            encrypted_data: Encrypted bytes
            shape: Original shape of the numpy array
            dtype: Data type of the numpy array
            
        Returns:
            Decrypted NumPy array
        """
        # Decrypt
        decrypted_bytes = self._cipher.decrypt(encrypted_data)
        # Convert back to numpy array
        descriptor = np.frombuffer(decrypted_bytes, dtype=dtype)
        return descriptor.reshape(shape)


def pseudonymize_identifier(identifier: str) -> str:
    """
    Create a pseudonymized identifier using SHA-256.
    
    Args:
        identifier: Original identifier (username, email, etc.)
        
    Returns:
        Pseudonymized identifier (64-character hex string)
    """
    return hashlib.sha256(identifier.encode()).hexdigest()


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.
    Note: In production, use bcrypt via passlib (done in auth service).
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()


# Create a global encryption service instance
encryption_service = EncryptionService()
