"""
Data encryption and security utilities
"""
import base64
import secrets
from typing import Union, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import logging
from ..config import settings

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service for data encryption and decryption"""
    
    def __init__(self):
        self.fernet_key = self._get_or_create_fernet_key()
        self.fernet = Fernet(self.fernet_key)
    
    def _get_or_create_fernet_key(self) -> bytes:
        """Get or create Fernet encryption key"""
        # In production, this should be stored securely (e.g., in a key management service)
        key_file = "/tmp/ai_printer_fernet.key"
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    def encrypt_string(self, data: str) -> str:
        """Encrypt a string and return base64 encoded result"""
        encrypted_data = self.fernet.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_string(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded string"""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Failed to decrypt data")
    
    def encrypt_sensitive_data(self, data: dict) -> str:
        """Encrypt sensitive data (like API keys, tokens)"""
        import json
        json_data = json.dumps(data)
        return self.encrypt_string(json_data)
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> dict:
        """Decrypt sensitive data"""
        import json
        decrypted_json = self.decrypt_string(encrypted_data)
        return json.loads(decrypted_json)
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    def hash_data(self, data: str, salt: bytes = None) -> Tuple[str, str]:
        """Hash data with salt using SHA-256"""
        if salt is None:
            salt = os.urandom(32)
        
        digest = hashes.Hash(hashes.SHA256())
        digest.update(salt)
        digest.update(data.encode())
        hash_value = digest.finalize()
        
        return base64.b64encode(hash_value).decode(), base64.b64encode(salt).decode()


class FileEncryption:
    """Service for file encryption and decryption"""
    
    def __init__(self):
        self.key = self._derive_key_from_password(settings.SECRET_KEY)
    
    def _derive_key_from_password(self, password: str) -> bytes:
        """Derive encryption key from password"""
        password_bytes = password.encode()
        salt = b'ai_printer_salt_2023'  # In production, use a unique salt per file
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password_bytes)
    
    def encrypt_file(self, file_data: bytes) -> bytes:
        """Encrypt file data"""
        # Generate a random initialization vector
        iv = os.urandom(16)
        
        # Create cipher
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # Pad data to block size
        padded_data = self._pad_data(file_data)
        
        # Encrypt
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return IV + encrypted data
        return iv + encrypted_data
    
    def decrypt_file(self, encrypted_data: bytes) -> bytes:
        """Decrypt file data"""
        # Extract IV and encrypted data
        iv = encrypted_data[:16]
        encrypted_content = encrypted_data[16:]
        
        # Create cipher
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        
        # Decrypt
        padded_data = decryptor.update(encrypted_content) + decryptor.finalize()
        
        # Remove padding
        return self._unpad_data(padded_data)
    
    def _pad_data(self, data: bytes) -> bytes:
        """Add PKCS7 padding to data"""
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad_data(self, padded_data: bytes) -> bytes:
        """Remove PKCS7 padding from data"""
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]


class AsymmetricEncryption:
    """RSA public/private key encryption"""
    
    @staticmethod
    def generate_key_pair() -> Tuple[bytes, bytes]:
        """Generate RSA key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    @staticmethod
    def encrypt_with_public_key(data: bytes, public_key_pem: bytes) -> bytes:
        """Encrypt data with public key"""
        public_key = serialization.load_pem_public_key(public_key_pem)
        
        encrypted_data = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return encrypted_data
    
    @staticmethod
    def decrypt_with_private_key(encrypted_data: bytes, private_key_pem: bytes) -> bytes:
        """Decrypt data with private key"""
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
        )
        
        decrypted_data = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return decrypted_data


class TokenSecurity:
    """Secure token generation and validation"""
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key"""
        return f"aip_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def generate_verification_token() -> str:
        """Generate email verification token"""
        return secrets.token_urlsafe(48)
    
    @staticmethod
    def generate_reset_token() -> str:
        """Generate password reset token"""
        return secrets.token_urlsafe(48)
    
    @staticmethod
    def constant_time_compare(a: str, b: str) -> bool:
        """Compare strings in constant time to prevent timing attacks"""
        return secrets.compare_digest(a, b)


class DataSanitizer:
    """Sanitize and validate input data"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent directory traversal"""
        import re
        # Remove path separators and special characters
        sanitized = re.sub(r'[^\w\s\-_\.]', '', filename)
        # Remove leading dots and spaces
        sanitized = sanitized.lstrip('. ')
        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:251] + ext
        
        return sanitized or "unnamed_file"
    
    @staticmethod
    def sanitize_user_input(text: str) -> str:
        """Basic sanitization for user input"""
        import html
        # HTML escape
        sanitized = html.escape(text)
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        return sanitized
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """Validate password strength"""
        import re
        
        checks = {
            'length': len(password) >= 8,
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'lowercase': bool(re.search(r'[a-z]', password)),
            'digit': bool(re.search(r'\d', password)),
            'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
        }
        
        score = sum(checks.values())
        
        return {
            'checks': checks,
            'score': score,
            'is_strong': score >= 4,
            'message': DataSanitizer._get_password_message(score, checks)
        }
    
    @staticmethod
    def _get_password_message(score: int, checks: dict) -> str:
        """Get password strength message"""
        if score >= 5:
            return "Very strong password"
        elif score >= 4:
            return "Strong password"
        elif score >= 3:
            return "Moderate password"
        else:
            missing = [key for key, value in checks.items() if not value]
            return f"Weak password. Missing: {', '.join(missing)}"


class SecureHeaders:
    """Security headers for HTTP responses"""
    
    @staticmethod
    def get_security_headers() -> dict:
        """Get standard security headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://apis.google.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.openai.com https://www.googleapis.com; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': (
                "geolocation=(), "
                "microphone=(self), "
                "camera=(), "
                "fullscreen=(self), "
                "payment=()"
            )
        }


# Global instances
encryption_service = EncryptionService()
file_encryption = FileEncryption()
token_security = TokenSecurity()
data_sanitizer = DataSanitizer()
secure_headers = SecureHeaders()

__all__ = [
    "EncryptionService",
    "FileEncryption", 
    "AsymmetricEncryption",
    "TokenSecurity",
    "DataSanitizer",
    "SecureHeaders",
    "encryption_service",
    "file_encryption",
    "token_security",
    "data_sanitizer",
    "secure_headers"
]