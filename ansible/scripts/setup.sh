#!/bin/bash
# Швидкий старт для проекту Ansible MikroTik WireGuard

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Налаштування проекту Ansible MikroTik WireGuard"
echo "=================================================="

# Перевірка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не знайдено. Встановіть Python 3."
    exit 1
fi

echo "✓ Python 3 знайдено"

# Перевірка/активація venv
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "✓ Virtual environment існує"
    source "$PROJECT_DIR/venv/bin/activate"
else
    echo "📦 Створення virtual environment..."
    python3 -m venv "$PROJECT_DIR/venv"
    source "$PROJECT_DIR/venv/bin/activate"
fi

echo "✓ Virtual environment активовано"

# Встановлення залежностей Python
echo "📦 Встановлення Python залежностей..."
pip install -q --upgrade pip
pip install -q -r "$PROJECT_DIR/requirements.txt"
echo "✓ Python залежності встановлено"

# Встановлення Ansible collections
echo "📦 Встановлення Ansible collections..."
ansible-galaxy collection install -r "$PROJECT_DIR/requirements.yml" --force
echo "✓ Ansible collections встановлено"

# Створення необхідних директорій
mkdir -p "$PROJECT_DIR/client_keys"
mkdir -p "$PROJECT_DIR/generated_configs"
mkdir -p "$PROJECT_DIR/logs"

echo "✓ Директорії створено"

# Перевірка inventory
if [ ! -f "$PROJECT_DIR/inventory/hosts.yml" ]; then
    echo "⚠️  Увага: inventory/hosts.yml не знайдено"
    echo "   Відредагуйте inventory/hosts.yml та вкажіть дані вашого сервера"
else
    echo "✓ Inventory файл знайдено"
fi

echo ""
echo "✅ Налаштування завершено!"
echo ""
echo "📋 Наступні кроки:"
echo ""
echo "1. Відредагуйте inventory/hosts.yml:"
echo "   - Вкажіть правильний ansible_host для вашого сервера"
echo "   - Встановіть ansible_user та ansible_password"
echo ""
echo "2. Згенеруйте ключі для нового клієнта:"
echo "   python scripts/generate_keys.py peer4"
echo ""
echo "3. Додайте клієнта на сервер:"
echo "   ansible-playbook playbooks/add_client.yml -e 'client_name=peer4' -e 'client_ip=10.66.66.5'"
echo ""
echo "4. Перегляньте поточну конфігурацію:"
echo "   ansible-playbook playbooks/show_config.yml"
echo ""
