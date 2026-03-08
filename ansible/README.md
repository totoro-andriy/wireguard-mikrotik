# 🔒 Ansible MikroTik WireGuard Manager

Автоматизована система управління WireGuard клієнтами на MikroTik роутерах з підтримкою VXLAN для створення L2 мережі.

## 📋 Особливості

- ✅ **Повністю автоматизоване додавання клієнтів** - просто `make add-client`
- ✅ Автоматичне призначення IP адрес з доступного діапазону
- ✅ Автоматична генерація імен клієнтів та VNI з IP
- ✅ Автоматичне додавання/видалення WireGuard peers
- ✅ Генерація криптографічних ключів (приватні, публічні, preshared)
- ✅ Автоматичне створення конфігурацій для MikroTik клієнтів
- ✅ Підтримка VXLAN для L2 зв'язності (окремий VXLAN інтерфейс для кожного клієнта)
- ✅ Масове додавання клієнтів з CSV
- ✅ **Повна конфігурація безпеки для клієнтів:**
  - 🔐 SSH авторизація тільки по ключам
  - 🔥 Firewall правила (захист від зовнішнього втручання)
  - 🚫 WiFi інтерфейси вимкнені
  - 🛡️ Захист від брутфорсу та port scanning
  - 🔒 SSH/Winbox доступ тільки з VPN
  - 🌐 ether1=WAN, інші ether=bridge
  - ⛔ Клієнти bridge без доступу до інтернету
- ✅ Makefile для швидких команд
- ✅ Валідація та линтинг Ansible

## 🏗️ Структура проекту

```
ansible-mikrotik/
├── ansible.cfg                     # Конфігурація Ansible
├── Makefile                        # Швидкі команди
├── inventory/
│   ├── hosts.yml                   # Інвентар хостів
│   └── group_vars/
│       └── all.yml                 # Глобальні змінні
├── roles/
│   └── wireguard_mikrotik/         # Роль управління WireGuard
│       ├── tasks/
│       │   ├── main.yml
│       │   ├── add_peer.yml
│       │   └── remove_peer.yml
│       ├── templates/
│       │   ├── client_config.rsc.j2    # Конфіг для MikroTik
│       │   └── client_config.conf.j2   # Конфіг для Linux/Windows
│       └── defaults/
│           └── main.yml
├── playbooks/
│   ├── add_client.yml              # Додати клієнта
│   ├── remove_client.yml           # Видалити клієнта
│   ├── show_config.yml             # Показати конфіг
│   └── get_server_public_key.yml   # Отримати публічний ключ
├── scripts/
│   ├── generate_keys.py            # Генератор ключів
│   ├── get_public_key.py           # Отримати публічний ключ
│   ├── bulk_add_clients.py         # Масове додавання
│   └── setup.sh                    # Швидке налаштування
├── client_keys/                    # Ключі клієнтів (не в git)
├── generated_configs/              # Згенеровані конфігурації
└── clients.csv.example             # Приклад CSV для масового додавання
```

## 🚀 Швидкий старт

### 1. Налаштування проекту

```bash
# Автоматичне налаштування (рекомендовано)
./scripts/setup.sh

# Або вручну
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
```

### 2. Налаштування inventory

Відредагуйте [inventory/hosts.yml](inventory/hosts.yml) та вкажіть дані вашого сервера:

```yaml
wireguard_servers:
  hosts:
    srv-01.mood.pp.ua:
      ansible_host: "srv-01.mood.pp.ua"
      ansible_user: "admin"
      ansible_password: "ваш_пароль"  # або використайте ansible-vault
```

### 3. Перевірте з'єднання

```bash
make test
# або
ansible wireguard_servers -m ping
```

## 💻 Використання

### Використання Makefile (рекомендовано)

```bash
# Показати всі доступні команди
make help

# Додати нового клієнта (повністю автоматично!)
make add-client
# Система автоматично:
# - Знайде перший вільний IP у діапазоні 10.66.66.2-254
# - Згенерує ім'я R6{last_octet}
# - Обчислить VNI = 600 + last_octet
# - Згенерує криптографічні ключі
# - Додасть клієнта на сервер

# Або вказати конкретний IP
make add-client IP=10.66.66.12

# Видалити клієнта (потрібен IP)
make remove-client IP=10.66.66.12

# Показати конфігурацію сервера
make show-config
```

### Автоматичне призначення

Система повністю автоматизована:

✅ **IP адреса** - автоматично знаходить перший вільний у діапазоні 10.66.66.2-254  
✅ **Ім'я клієнта** - генерується з IP: `R6{last_octet}`  
✅ **VNI** - обчислюється: `6{last_octet}` (конкатенація)  
✅ **Криптографічні ключі** - генеруються автоматично

**Приклади:**
- IP `10.66.66.5` → Ім'я `R65`, VNI `65`
- IP `10.66.66.12` → Ім'я `R612`, VNI `612`
- IP `10.66.66.100` → Ім'я `R6100`, VNI `6100`
make help

# Додати клієнта (генерує ключі + додає на сервер)
make add-client NAME=peer4 IP=10.66.66.5

# Видалити клієнта
make remove-client NAME=peer4 IP=10.66.66.5

# Показати конфігурацію сервера
make show-config

# Тільки згенерувати ключі
make generate-keys NAME=peer5

# Масово додати клієнтів з CSV
make bulk-add FILE=clients.csv
```

### Використання Ansible playbooks

#### Додати нового клієнта

```bash
# 1. Згенеруйте ключі
python scripts/generate_keys.py peer4

# 2. Додайте клієнта на сервер
ansible-playbook playbooks/add_client.yml \
  -e "client_name=peer4" \
  -e "client_ip=10.66.66.5"
```

#### Видалити клієнта

```bash
ansible-playbook playbooks/remove_client.yml \
  -e "client_name=peer4" \
  -e "client_ip=10.66.66.5"
```

#### Показати поточну конфігурацію

```bash
ansible-playbook playbooks/show_config.yml
```

### Масове додавання клієнтів

1. Створіть CSV файл (див. [clients.csv.example](clients.csv.example)):

```csv
client_name,client_ip
peer4,10.66.66.5
peer5,10.66.66.6
peer6,10.66.66.7
```

2. Запустіть масове додавання:

```bash
python scripts/bulk_add_clients.py clients.csv

# Або через Makefile
make bulk-add FILE=clients.csv

# Тільки згенерувати ключі без додавання
python scripts/bulk_add_clients.py clients.csv --keys-only
```

## 🔑 Робота з ключами

### Генерація ключів для клієнта

```bash
python scripts/generate_keys.py peer4

# Вивід:
# 🔑 WireGuard ключі для клієнта: peer4
# 📝 Приватний ключ: ....
# 🔓 Публічний ключ: ....
# 🔐 Preshared ключ: ....
# ✅ Ключі збережено в: client_keys/peer4.json
```

### Отримання публічного ключа з приватного

```bash
python scripts/get_public_key.py "приватний_ключ"

# Публічний ключ сервера
python scripts/get_public_key.py "6EasMCGDrnk0GZrwIjJnO2GP9whr7dSll8k6TjwTfXA="
# Результат: QmOqGj4vAgWfmVxkc0xoqQZ4N7+P833VHs+xXJdhCxY=
```

## 📡 Конфігурація сервера

**Сервер:** srv-01.mood.pp.ua

### WireGuard
- **Інтерфейс:** fly
- **Listen Port:** 62356
- **IP адреса:** 10.66.66.1/24
- **Приватний ключ:** 6EasMCGDrnk0GZrwIjJnO2GP9whr7dSll8k6TjwTfXA=
- **Публічний ключ:** QmOqGj4vAgWfmVxkc0xoqQZ4N7+P833VHs+xXJdhCxY=

### VXLAN
- **Інтерфейс:** vxlan1
- **VNI:** 100
- **Local Address:** 10.66.66.1

### Bridge & DHCP
- **Bridge:** br_x
- **Мережа:** 172.16.0.0/16
- **Gateway:** 172.16.0.1
- **DHCP Pool:** 172.16.0.2 - 172.16.255.254

## 📝 Згенеровані конфігурації

Після додавання клієнта, конфігураційний файл буде створено в `generated_configs/`:

```bash
generated_configs/
└── peer4.rsc    # Конфігурація для MikroTik
```

### Імпорт конфігурації на MikroTik клієнта

**⚠️ ВАЖЛИВО: Перш ніж імпортувати конігурацію!**

1. **Підключіться до роутера** через MAC-Winbox або консоль

2. **Створіть backup:**
```
/system backup save name=before-vpn
```

3. **Скопіюйте файл** на клієнт через SFTP/Winbox

4. **Імпортуйте конфігурацію:**
```
/import file=peer4.rsc
```

5. **Після імпорту:**
   - SSH ключ (MainSSH) доданий автоматично
   - SSH та Winbox доступні ТІЛЬКИ через VPN (10.66.66.x)
   - Пароль SSH вимкнено, тільки ключі
   - Всі WiFi інтерфейси вимкнені
   - ether1 = WAN, інші ether = bridge
   - Firewall налаштований на максимальну безпеку

## 🛡️ Безпека

- Ключі зберігаються в `client_keys/` з правами доступу `0600`
- Директорія `client_keys/` додана в `.gitignore`
- Використовуйте `ansible-vault` для зберігання паролів:

```bash
# Створити vault для паролів
ansible-vault create inventory/vault.yml

# Редагувати vault
ansible-vault edit inventory/vault.yml

# Використати при запуску playbook
ansible-playbook playbooks/add_client.yml --ask-vault-pass
```

## 🔧 Розробка

### Лінтинг

```bash
# Перевірити Ansible файли
make lint

# Або окремо
ansible-lint playbooks/*.yml
yamllint inventory/
```

### Очищення

```bash
# Очистити тимчасові файли
make clean

# Повне очищення (включно з venv)
make clean-all
```

## 📚 Додаткові ресурси

- [EXAMPLES.md](EXAMPLES.md) - **Детальні приклади використання**
- [ARCHITECTURE.md](ARCHITECTURE.md) - **Детальний опис архітектури та мережі**
- [SECURITY.md](SECURITY.md) - **Детальний опис налаштувань безпеки**
- [MIGRATION.md](MIGRATION.md) - **Міграція на версію 1.1.0**
- [QUICKSTART.md](QUICKSTART.md) - Швидкий старт за 5 хвилин
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Огляд проекту
- [CHANGELOG.md](CHANGELOG.md) - Історія змін
- [MikroTik WireGuard Documentation](https://help.mikrotik.com/docs/display/ROS/WireGuard)
- [Ansible Collection: community.routeros](https://docs.ansible.com/ansible/latest/collections/community/routeros/)
- [WireGuard](https://www.wireguard.com/)

## 🤝 Підтримка

При виникненні проблем:

1. Перевірте з'єднання: `make test`
2. Перегляньте конфігурацію: `make show-config`
3. Перевірте логи Ansible
4. Перевірте firewall правила на сервері

## 📄 Ліцензія

MIT
