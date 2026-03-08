#!/usr/bin/env python3
"""
Скрипт для генерації WireGuard ключів для MikroTik клієнтів.
Генерує приватний ключ, публічний ключ та preshared ключ.
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Dict

try:
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("❌ Помилка: необхідна бібліотека cryptography")
    print("Встановіть: pip install cryptography")
    sys.exit(1)


def generate_private_key() -> str:
    """Генерує приватний ключ WireGuard."""
    private_key = X25519PrivateKey.generate()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    return base64.b64encode(private_bytes).decode('ascii')


def derive_public_key(private_key_b64: str) -> str:
    """Отримує публічний ключ з приватного."""
    private_bytes = base64.b64decode(private_key_b64)
    private_key = X25519PrivateKey.from_private_bytes(private_bytes)
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return base64.b64encode(public_bytes).decode('ascii')


def generate_preshared_key() -> str:
    """Генерує preshared ключ (32 випадкових байти)."""
    return base64.b64encode(os.urandom(32)).decode('ascii')


def generate_keys_set(client_name: str) -> Dict[str, str]:
    """Генерує повний набір ключів для клієнта."""
    private_key = generate_private_key()
    public_key = derive_public_key(private_key)
    preshared_key = generate_preshared_key()
    
    return {
        'client_name': client_name,
        'private_key': private_key,
        'public_key': public_key,
        'preshared_key': preshared_key,
    }


def save_keys(keys: Dict[str, str], output_dir: Path) -> Path:
    """Зберігає ключі в JSON файл."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{keys['client_name']}.json"
    
    with open(output_file, 'w') as f:
        json.dump(keys, f, indent=2)
    
    # Встановлюємо обмежені права доступу
    os.chmod(output_file, 0o600)
    
    return output_file


def print_keys(keys: Dict[str, str]):
    """Виводить ключі на екран."""
    print("\n" + "="*70)
    print(f"🔑 WireGuard ключі для клієнта: {keys['client_name']}")
    print("="*70)
    print(f"\n📝 Приватний ключ (Private Key):")
    print(f"   {keys['private_key']}")
    print(f"\n🔓 Публічний ключ (Public Key):")
    print(f"   {keys['public_key']}")
    print(f"\n🔐 Preshared ключ (Preshared Key):")
    print(f"   {keys['preshared_key']}")
    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(
        description='Генератор WireGuard ключів для MikroTik клієнтів',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Приклади використання:
  %(prog)s peer4
  %(prog)s peer5 --output-dir ./my_keys
  %(prog)s peer6 --no-save
        """
    )
    
    parser.add_argument(
        'client_name',
        help='Ім\'я клієнта (наприклад, peer4, client1)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'client_keys',
        help='Директорія для збереження ключів (за замовчуванням: ../client_keys)'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Не зберігати ключі, тільки вивести на екран'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Перезаписати існуючі ключі'
    )
    
    args = parser.parse_args()
    
    # Перевірка чи існують ключі
    output_file = args.output_dir / f"{args.client_name}.json"
    if output_file.exists() and not args.force and not args.no_save:
        print(f"❌ Помилка: ключі для {args.client_name} вже існують: {output_file}")
        print(f"Використайте --force для перезапису або --no-save для генерації без збереження")
        sys.exit(1)
    
    # Генерація ключів
    print(f"⚙️  Генерація ключів для клієнта: {args.client_name}...")
    keys = generate_keys_set(args.client_name)
    
    # Виведення ключів
    print_keys(keys)
    
    # Збереження ключів
    if not args.no_save:
        saved_file = save_keys(keys, args.output_dir)
        print(f"\n✅ Ключі збережено в: {saved_file}")
        print(f"\n💡 Наступний крок:")
        print(f"   ansible-playbook playbooks/add_client.yml \\")
        print(f"     -e 'client_name={args.client_name}' \\")
        print(f"     -e 'client_ip=10.66.66.X'")
    else:
        print("\n⚠️  Ключі НЕ збережено (використано --no-save)")


if __name__ == '__main__':
    main()
