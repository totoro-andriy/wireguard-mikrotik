#!/bin/bash
# Скрипт для перевірки синтаксису всіх Ansible файлів

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔍 Перевірка синтаксису Ansible playbooks..."

cd "$PROJECT_DIR"

# Перевірка playbooks
for playbook in playbooks/*.yml; do
    echo "  Перевірка: $playbook"
    ansible-playbook --syntax-check "$playbook"
done

echo "✅ Всі playbooks мають правильний синтаксис"

# Перевірка inventory
echo "🔍 Перевірка inventory..."
ansible-inventory --list > /dev/null
echo "✅ Inventory валідний"

# Ansible lint (якщо встановлено)
if command -v ansible-lint &> /dev/null; then
    echo "🔍 Запуск ansible-lint..."
    ansible-lint playbooks/*.yml || echo "⚠️  Знайдено попередження від ansible-lint"
fi

# YAML lint (якщо встановлено)
if command -v yamllint &> /dev/null; then
    echo "🔍 Запуск yamllint..."
    yamllint inventory/ playbooks/ roles/ || echo "⚠️  Знайдено попередження від yamllint"
fi

echo ""
echo "✅ Перевірка завершена!"
