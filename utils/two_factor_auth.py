#!/usr/bin/env python3
"""
Two-Factor Authentication module for Open WebUI

This module implements TOTP (Time-based One-Time Password) authentication
compatible with standard authenticator apps like Google Authenticator,
Microsoft Authenticator, Authy, etc.

Dependencies:
- pyotp: For TOTP generation and verification
- qrcode: For generating QR codes for app setup
- pillow: For image processing (required by qrcode)

Install with: pip install pyotp qrcode[pil]
"""

import base64
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

try:
    from io import BytesIO

    import pyotp
    import qrcode
    from qrcode.image.pil import PilImage
    IMPORTS_SUCCESSFUL = True
except ImportError:
    IMPORTS_SUCCESSFUL = False
    logging.warning("2FA dependencies not installed. Run: pip install pyotp qrcode[pil]")

# Configure logging
logger = logging.getLogger(__name__)

class TwoFactorAuth:
    """
    Implements TOTP (Time-based One-Time Password) for two-factor authentication.
    """
    
    def __init__(self, issuer_name: str = "Open WebUI"):
        """
        Initialize the 2FA module.
        
        Args:
            issuer_name: The name that appears in authenticator apps
        """
        self.issuer_name = issuer_name
        if not IMPORTS_SUCCESSFUL:
            logger.error("2FA dependencies not installed. Install with: pip install pyotp qrcode[pil]")
    
    def generate_secret(self) -> str:
        """
        Generate a new random secret key for TOTP.
        
        Returns:
            str: Base32 encoded secret key
        """
        if not IMPORTS_SUCCESSFUL:
            return ""
        return pyotp.random_base32()
    
    def get_totp_uri(self, username: str, secret: str) -> str:
        """
        Generate the TOTP URI for QR code generation.
        
        Args:
            username: The username to associate with this TOTP
            secret: The secret key for this user
            
        Returns:
            str: TOTP URI for QR code generation
        """
        if not IMPORTS_SUCCESSFUL:
            return ""
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name=self.issuer_name
        )
    
    def generate_qr_code(self, username: str, secret: str) -> Tuple[str, str]:
        """
        Generate a QR code image for setting up authenticator apps.
        
        Args:
            username: The username for the TOTP
            secret: The secret key for this user
            
        Returns:
            Tuple[str, str]: (base64_encoded_qr_image, totp_uri)
        """
        if not IMPORTS_SUCCESSFUL:
            return "", ""
        
        totp_uri = self.get_totp_uri(username, secret)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert image to base64 string
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}", totp_uri
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """
        Verify a TOTP token.
        
        Args:
            secret: The user's secret key
            token: The token to verify
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        if not IMPORTS_SUCCESSFUL:
            logger.error("Cannot verify TOTP: dependencies not installed")
            return False
        
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
    
    def verify_totp_with_window(self, secret: str, token: str, window: int = 1) -> bool:
        """
        Verify a TOTP token with a time window for validity.
        
        Args:
            secret: The user's secret key
            token: The token to verify
            window: Number of 30-second windows to check before and after current time
            
        Returns:
            bool: True if token is valid within the window, False otherwise
        """
        if not IMPORTS_SUCCESSFUL:
            logger.error("Cannot verify TOTP: dependencies not installed")
            return False
        
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=window)


class BackupCodes:
    """
    Manages backup codes for 2FA recovery.
    """
    
    CODE_COUNT = 10
    CODE_LENGTH = 8
    
    @staticmethod
    def generate_backup_codes() -> list[str]:
        """
        Generate a set of backup recovery codes.
        
        Returns:
            list[str]: List of backup codes
        """
        codes = []
        for _ in range(BackupCodes.CODE_COUNT):
            # Generate 8-character backup code using letters and numbers
            code = ''.join(os.urandom(1)[0] % 36 for _ in range(BackupCodes.CODE_LENGTH))
            code = ''.join(chr(c + ord('a')) if c < 26 else chr(c - 26 + ord('0')) for c in code)
            # Add hyphen in middle for readability
            code = f"{code[:4]}-{code[4:]}"
            codes.append(code)
        return codes
    
    @staticmethod
    def hash_backup_codes(codes: list[str]) -> list[str]:
        """
        Hash backup codes for secure storage.
        In a production environment, use a proper password hashing function.
        
        Args:
            codes: List of plaintext backup codes
            
        Returns:
            list[str]: List of hashed backup codes
        """
        import hashlib
        return [hashlib.sha256(code.encode()).hexdigest() for code in codes]
    
    @staticmethod
    def verify_backup_code(code: str, hashed_codes: list[str]) -> bool:
        """
        Verify a backup code against a list of hashed codes.
        
        Args:
            code: The backup code to verify
            hashed_codes: List of hashed backup codes
            
        Returns:
            bool: True if code matches any in the list
        """
        import hashlib
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        return code_hash in hashed_codes


# Example usage
def example():
    """Example usage of the 2FA functionality."""
    if not IMPORTS_SUCCESSFUL:
        print("Cannot run example: Required packages not installed.")
        print("Install with: pip install pyotp qrcode[pil]")
        return
    
    # Initialize 2FA
    tfa = TwoFactorAuth("Open WebUI Demo")
    
    # Generate secret for a new user
    secret = tfa.generate_secret()
    print(f"Generated secret: {secret}")
    
    # Generate QR code
    qr_code, uri = tfa.generate_qr_code("test_user", secret)
    print(f"TOTP URI: {uri}")
    print("QR Code generated (base64 string):", qr_code[:50] + "...")
    
    # Verify a token (you would get this from user input)
    # For testing, we can generate a valid token
    if IMPORTS_SUCCESSFUL:
        totp = pyotp.TOTP(secret)
        token = totp.now()
        print(f"Current token: {token}")
        
        is_valid = tfa.verify_totp(secret, token)
        print(f"Token verification: {is_valid}")
    
    # Generate backup codes
    backup_codes = BackupCodes.generate_backup_codes()
    print("Generated backup codes:", backup_codes)
    
    # Hash backup codes for storage
    hashed_codes = BackupCodes.hash_backup_codes(backup_codes)
    print("Hashed backup codes (first one):", hashed_codes[0])
    
    # Verify a backup code
    is_valid_backup = BackupCodes.verify_backup_code(backup_codes[0], hashed_codes)
    print(f"Backup code verification: {is_valid_backup}")


if __name__ == "__main__":
    example()
