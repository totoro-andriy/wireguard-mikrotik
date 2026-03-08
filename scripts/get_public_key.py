#!/usr/bin/env python3
"""
Допоміжний скрипт для отримання публічного ключа з приватного ключа WireGuard.
"""

import argparse
import base64
import sys

try:
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("❌ Помилка: необхідна бібліотека cryptography")
    print("Встановіть: pip install cryptography")
    sys.exit(1)


def derive_public_key(private_key_b64: str) -> str:
    """Отримує публічний ключ з приватного."""
    try:
        private_bytes = base64.b64decode(private_key_b64)
        private_key = X25519PrivateKey.from_private_bytes(private_bytes)
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return base64.b64encode(public_bytes).decode('ascii')
    except Exception as e:
        print(f"❌ Помилка при обробці ключа: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Отримати публічний ключ з приватного ключа WireGuard'
    )
    
    parser.add_argument(
        'private_key',
        help='Приватний ключ WireGuard (Base64)'
    )
    
    args = parser.parse_args()
    
    public_key = derive_public_key(args.private_key)
    print(public_key)


if __name__ == '__main__':
    main()
