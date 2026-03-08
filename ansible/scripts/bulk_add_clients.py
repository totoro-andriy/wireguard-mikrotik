#!/usr/bin/env python3
"""
Скрипт для масового додавання клієнтів з CSV файлу.
"""

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict


def read_clients_from_csv(csv_file: Path) -> List[Dict[str, str]]:
    """Читає список клієнтів з CSV файлу."""
    clients = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('client_name') or not row.get('client_ip'):
                print(f"⚠️  Пропущено рядок з неповними даними: {row}")
                continue
            clients.append({
                'client_name': row['client_name'].strip(),
                'client_ip': row['client_ip'].strip(),
            })
    
    return clients


def generate_keys(client_name: str, scripts_dir: Path) -> bool:
    """Генерує ключі для клієнта."""
    try:
        result = subprocess.run(
            ['python3', str(scripts_dir / 'generate_keys.py'), client_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ Ключі згенеровано для {client_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Помилка при генерації ключів для {client_name}: {e}")
        return False


def add_client_to_server(client_name: str, client_ip: str, project_dir: Path) -> bool:
    """Додає клієнта на сервер через Ansible."""
    try:
        result = subprocess.run(
            [
                'ansible-playbook',
                str(project_dir / 'playbooks' / 'add_client.yml'),
                '-e', f'client_name={client_name}',
                '-e', f'client_ip={client_ip}',
            ],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_dir
        )
        print(f"✓ Клієнт {client_name} додано на сервер")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Помилка при додаванні {client_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Масове додавання WireGuard клієнтів з CSV файлу',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Формат CSV файлу:
  client_name,client_ip
  peer4,10.66.66.5
  peer5,10.66.66.6
  peer6,10.66.66.7

Приклад використання:
  %(prog)s clients.csv
  %(prog)s clients.csv --dry-run
        """
    )
    
    parser.add_argument(
        'csv_file',
        type=Path,
        help='CSV файл зі списком клієнтів'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Тільки показати що буде зроблено, без реальних змін'
    )
    
    parser.add_argument(
        '--keys-only',
        action='store_true',
        help='Тільки згенерувати ключі, не додавати на сервер'
    )
    
    args = parser.parse_args()
    
    # Перевірка файлу
    if not args.csv_file.exists():
        print(f"❌ Файл не знайдено: {args.csv_file}")
        sys.exit(1)
    
    # Визначення директорій проекту
    project_dir = Path(__file__).parent.parent
    scripts_dir = project_dir / 'scripts'
    
    # Читання клієнтів
    print(f"📖 Читання клієнтів з {args.csv_file}...")
    clients = read_clients_from_csv(args.csv_file)
    
    if not clients:
        print("❌ Не знайдено клієнтів у файлі")
        sys.exit(1)
    
    print(f"✓ Знайдено {len(clients)} клієнтів")
    
    if args.dry_run:
        print("\n🔍 Режим dry-run - буде виконано:")
        for client in clients:
            print(f"  - {client['client_name']} ({client['client_ip']})")
        sys.exit(0)
    
    # Обробка кожного клієнта
    success_count = 0
    failed_count = 0
    
    for i, client in enumerate(clients, 1):
        print(f"\n[{i}/{len(clients)}] Обробка {client['client_name']}...")
        
        # Генерація ключів
        if not generate_keys(client['client_name'], scripts_dir):
            failed_count += 1
            continue
        
        # Додавання на сервер (якщо не keys-only)
        if not args.keys_only:
            if add_client_to_server(client['client_name'], client['client_ip'], project_dir):
                success_count += 1
            else:
                failed_count += 1
        else:
            success_count += 1
    
    # Підсумок
    print("\n" + "="*70)
    print(f"✅ Успішно оброблено: {success_count}")
    if failed_count > 0:
        print(f"❌ Помилок: {failed_count}")
    print("="*70)


if __name__ == '__main__':
    main()
