# 📝 Приклади використання

## Швидкий старт

### Додавання клієнтів

```bash
# Активувати віртуальне середовище
source venv/bin/activate

# Найпростіший спосіб - повністю автоматично!
make add-client
# Система сама:
# 1. Знайде перший вільний IP (наприклад 10.66.66.5)
# 2. Створить ім'я: R65
# 3. Обчислить VNI: 65
# 4. Згенерує криптографічні ключі
# 5. Додасть клієнта на сервер
# 6. Створить конфігурацію: generated_configs/R65.rsc

# Або вказати конкретний IP
make add-client IP=10.66.66.12
# Автоматично створить:
# - Ім'я: R612
# - VNI: 612
# - Конфігурація: generated_configs/R612.rsc

# Додати ще одного клієнта
make add-client IP=10.66.66.13
# Автоматично створить:
# - Ім'я: R613
# - VNI: 613
# - Конфігурація: generated_configs/R613.rsc
```

### Видалення клієнтів

```bash
# Видалити клієнта з IP 10.66.66.12
make remove-client IP=10.66.66.12
# Автоматично визначить ім'я: R612

# Видалити клієнта з IP 10.66.66.5
make remove-client IP=10.66.66.5
# Автоматично визначить ім'я: R65
```

### Перегляд конфігурації

```bash
# Показати всю конфігурацію на сервері
make show-config

# Отримати публічний ключ сервера
ansible-playbook playbooks/get_server_public_key.yml
```

## Таблиця відповідності IP → Ім'я → VNI

| IP адреса      | Ім'я клієнта | VNI  | VXLAN інтерфейс |
|----------------|--------------|------|-----------------|
| 10.66.66.2     | R62          | 62   | vxlan-R62       |
| 10.66.66.3     | R63          | 63   | vxlan-R63       |
| 10.66.66.4     | R64          | 64   | vxlan-R64       |
| 10.66.66.5     | R65          | 65   | vxlan-R65       |
| 10.66.66.10    | R610         | 610  | vxlan-R610      |
| 10.66.66.12    | R612         | 612  | vxlan-R612      |
| 10.66.66.100   | R6100        | 6100 | vxlan-R6100     |
| 10.66.66.254   | R6254        | 6254 | vxlan-R6254     |

## Повний процес додавання клієнта

### 1. Додати клієнта через Ansible

```bash
make add-client IP=10.66.66.12
```

Вивід:
```
⏳ Генерація ключів для R612 (10.66.66.12)...
✅ Ключі успішно згенеровано: client_keys/R612.json

⏳ Додавання R612 на сервер...
PLAY [Додати WireGuard клієнта] *******************

TASK [Перевірка обов'язкових параметрів] **********
ok: [srv-01.mood.pp.ua]

TASK [Згенерувати ім'я клієнта з IP адреси] *******
ok: [srv-01.mood.pp.ua]

TASK [Показати згенероване ім'я] ******************
ok: [srv-01.mood.pp.ua] => {
    "msg": "Ім'я клієнта: R612, VNI: 612"
}

...

TASK [Вивести підсумок] ***************************
ok: [srv-01.mood.pp.ua] => {
    "msg": [
        "╔════════════════════════════════════════════════════════╗",
        "║  WireGuard клієнт успішно додано!                      ║",
        "╠════════════════════════════════════════════════════════╣",
        "║  Клієнт: R612",
        "║  IP адреса: 10.66.66.12",
        "║  Користувач: maestro",
        "║  Пароль: xK9#pL2@mN5!qW8&",
        "║  Конфігурація: generated_configs/R612.rsc",
        "╠════════════════════════════════════════════════════════╣",
        "║  ВАЖЛИВО: Збережіть пароль в безпечному місці!         ║",
        "║  SSH доступ також працює по ключу MainSSH              ║",
        "╚════════════════════════════════════════════════════════╝"
    ]
}
```

### 2. Імпортувати конфігурацію на клієнта

**Через Winbox:**
1. Files → Upload → виберіть `generated_configs/R612.rsc`
2. New Terminal
3. `/import file=R612.rsc`

**Через SCP:**
```bash
scp generated_configs/R612.rsc admin@client-ip:/
ssh admin@client-ip "/import file=R612.rsc"
```

### 3. Перевірка

**На сервері:**
```bash
# Перевірити через Ansible
make show-config

# Або напряму на сервері
ssh admin@srv-01.mood.pp.ua
/interface wireguard peers print
/interface vxlan print where name~"R612"
/interface bridge port print where interface~"vxlan-R612"
```

**На клієнті:**
```bash
ssh maestro@10.66.66.12  # через VPN після підключення
# Або через Winbox

/interface wireguard peers print
# Має показати active з'єднання

/ip dhcp-client print
# Має показати отриманий IP з bridge мережі (172.16.x.x)

/ping 172.16.0.1
# Має працювати
```

## Масове додавання клієнтів

### Створіть файл clients.csv

```csv
name,ip
10.66.66.10
10.66.66.11
10.66.66.12
10.66.66.13
10.66.66.14
```

### Запустіть масове додавання

```bash
python scripts/bulk_add_clients.py clients.csv
```

Скрипт автоматично:
1. Згенерує ім'я для кожного IP (R610, R611, R612...)
2. Створить ключі
3. Додасть клієнтів на сервер
4. Згенерує конфігурації

## Troubleshooting

### Клієнт не підключається

```bash
# Перевірити на сервері
/interface wireguard peers print
# Має бути "current-endpoint-address" та "last-handshake"

# Перевірити firewall
/ip firewall filter print where chain=input

# Перевірити VXLAN
/interface vxlan print where name~"R612"
/interface bridge port print where interface~"vxlan-R612"
```

### Клієнт не отримує IP через DHCP

```bash
# На сервері перевірити DHCP
/ip dhcp-server lease print

# Перевірити bridge
/interface bridge port print where bridge=br_x

# На клієнті
/ip dhcp-client print
/log print where topics~"dhcp"
```

### Перегенерувати конфігурацію

Якщо потрібно перегенерувати конфігурацію без видалення:

```bash
ansible-playbook playbooks/add_client.yml -e "client_ip=10.66.66.12" --tags generate_config
```

## Корисні команди

```bash
# Показати всі доступні команди
make help

# Перевірити з'єднання з сервером
make test

# Запустити lint
make lint

# Очистити тимчасові файли
make clean

# Згенерувати ключі вручну
python scripts/generate_keys.py R612

# Конвертувати приватний ключ в публічний
python scripts/get_public_key.py "private_key_here"
```
