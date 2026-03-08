#!/bin/bash
# Скрипт для підготовки конфігурації клієнта з SSH ключем

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIGS_DIR="$PROJECT_DIR/generated_configs"

# Функція для виведення використання
usage() {
    cat << EOF
Використання: $0 <client_name> [ssh_public_key_file]

Приклади:
  $0 peer4                           # Буде запитано ключ інтерактивно
  $0 peer4 ~/.ssh/id_ed25519.pub     # Використати існуючий ключ

Цей скрипт:
1. Знаходить згенеровану конфігурацію клієнта
2. Додає ваш SSH публічний ключ
3. Створює готовий до імпорту файл

EOF
    exit 1
}

# Перевірка аргументів
if [ $# -lt 1 ]; then
    usage
fi

CLIENT_NAME="$1"
SSH_KEY_FILE="${2:-}"
CONFIG_FILE="$CONFIGS_DIR/${CLIENT_NAME}.rsc"

# Перевірка чи існує конфігураційний файл
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Помилка: Конфігурація для $CLIENT_NAME не знайдена: $CONFIG_FILE"
    echo "   Спочатку створіть клієнта:"
    echo "   make add-client NAME=$CLIENT_NAME IP=10.66.66.X"
    exit 1
fi

echo "🔍 Знайдено конфігурацію: $CONFIG_FILE"

# Отримання SSH ключа
SSH_KEY=""

if [ -n "$SSH_KEY_FILE" ]; then
    # Ключ вказано як аргумент
    if [ ! -f "$SSH_KEY_FILE" ]; then
        echo "❌ Помилка: SSH ключ не знайдено: $SSH_KEY_FILE"
        exit 1
    fi
    SSH_KEY=$(cat "$SSH_KEY_FILE")
    echo "✅ Використовується SSH ключ з: $SSH_KEY_FILE"
else
    # Спробувати знайти стандартні ключі
    POSSIBLE_KEYS=(
        "$HOME/.ssh/id_ed25519.pub"
        "$HOME/.ssh/id_rsa.pub"
        "$HOME/.ssh/id_ecdsa.pub"
    )
    
    FOUND_KEY=""
    for key_file in "${POSSIBLE_KEYS[@]}"; do
        if [ -f "$key_file" ]; then
            FOUND_KEY="$key_file"
            break
        fi
    done
    
    if [ -n "$FOUND_KEY" ]; then
        echo "🔑 Знайдено SSH ключ: $FOUND_KEY"
        read -p "Використати цей ключ? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            SSH_KEY=$(cat "$FOUND_KEY")
        fi
    fi
    
    # Якщо ключ не знайдено або користувач відмовився
    if [ -z "$SSH_KEY" ]; then
        echo ""
        echo "📝 Введіть ваш SSH публічний ключ (або шлях до файлу):"
        echo "   Приклад: ssh-ed25519 AAAAC3NzaC1... user@host"
        echo ""
        read -r SSH_KEY_INPUT
        
        # Перевірити чи це файл
        if [ -f "$SSH_KEY_INPUT" ]; then
            SSH_KEY=$(cat "$SSH_KEY_INPUT")
        else
            SSH_KEY="$SSH_KEY_INPUT"
        fi
    fi
fi

# Валідація SSH ключа
if [ -z "$SSH_KEY" ]; then
    echo "❌ Помилка: SSH ключ не може бути порожнім"
    exit 1
fi

# Перевірка формату ключа
if ! echo "$SSH_KEY" | grep -qE "^(ssh-rsa|ssh-ed25519|ecdsa-sha2-nistp256|ecdsa-sha2-nistp384|ecdsa-sha2-nistp521)"; then
    echo "❌ Помилка: Невірний формат SSH ключа"
    echo "   Ключ має починатися з: ssh-rsa, ssh-ed25519, або ecdsa-sha2-*"
    exit 1
fi

echo "✅ SSH ключ валідний"

# Створити резервну копію
BACKUP_FILE="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$CONFIG_FILE" "$BACKUP_FILE"
echo "📋 Створено резервну копію: $BACKUP_FILE"

# Підготувати SSH ключ для вставки (екранувати лапки якщо є)
SSH_KEY_ESCAPED=$(echo "$SSH_KEY" | sed 's/"/\\"/g')

# Додати SSH ключ до конфігурації
# Знайти рядок з коментарем для SSH ключа і замінити його
if grep -q "# add key=\"ssh-ed25519 AAAAC3" "$CONFIG_FILE"; then
    # Використовуємо sed для заміни закоментованого рядка
    sed -i "/^# add key=\"ssh-ed25519 AAAAC3/c\add key=\"$SSH_KEY_ESCAPED\" user=admin comment=\"${CLIENT_NAME}_ssh_key\"" "$CONFIG_FILE"
    echo "✅ SSH ключ додано до конфігурації"
else
    echo "⚠️  Не знайдено місце для SSH ключа в конфігурації"
    echo "   Додайте вручну в секцію /user ssh-keys:"
    echo "   add key=\"$SSH_KEY\" user=admin"
fi

# Перевірити чи ключ додано
if grep -q "add key=\"$SSH_KEY_ESCAPED\"" "$CONFIG_FILE"; then
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "✅ Конфігурація готова до імпорту!"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "📁 Файл: $CONFIG_FILE"
    echo "🔑 SSH ключ додано"
    echo ""
    echo "📋 Наступні кроки:"
    echo ""
    echo "1. Скопіюйте файл на MikroTik роутер:"
    echo "   scp $CONFIG_FILE admin@mikrotik-ip:${CLIENT_NAME}.rsc"
    echo ""
    echo "2. Підключіться до роутера через MAC-Winbox або консоль"
    echo ""
    echo "3. Імпортуйте конфігурацію:"
    echo "   /import file=${CLIENT_NAME}.rsc"
    echo ""
    echo "4. Після імпорту підключайтеся через VPN:"
    echo "   ssh admin@{{ wg_client_ip }}"
    echo ""
    echo "⚠️  ВАЖЛИВО:"
    echo "   - SSH та Winbox доступні ТІЛЬКИ через VPN"
    echo "   - Пароль SSH вимкнено (тільки ключі)"
    echo "   - ether1 = WAN, інші ether = bridge"
    echo "   - WiFi інтерфейси вимкнені"
    echo ""
else
    echo "❌ Помилка при додаванні SSH ключа"
    echo "   Відновіть з резервної копії: $BACKUP_FILE"
    exit 1
fi
