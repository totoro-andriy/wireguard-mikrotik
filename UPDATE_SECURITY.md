# 🎉 Оновлення: Повна конфігурація безпеки клієнтів

## 📅 Дата: 2026-01-25

## 🚀 Що додано

### 1. ✨ Повна конфігурація безпеки в шаблоні клієнта

Файл: `roles/wireguard_mikrotik/templates/client_config.rsc.j2`

**Додано розділи:**

#### 🔥 Firewall правила
- **INPUT chain**: Захист роутера від зовнішнього доступу
  - Доступ SSH та Winbox ТІЛЬКИ з VPN (10.66.66.0/24)
  - WireGuard UDP 51820 на WAN
  - ICMP тільки з VPN та bridge
  - DROP всього іншого з WAN

- **FORWARD chain**: Контроль routing між інтерфейсами
  - Дозвіл bridge ↔ bridge (без обмежень всередині)
  - Дозвіл VXLAN ↔ bridge
  - **БЛОКУВАННЯ bridge → Internet** (клієнтам інтернет не потрібний)
  - DROP невалідних пакетів

- **RAW chain**: Захист від атак
  - Port scan detection та блокування
  - SSH brute force protection (4-етапний)

#### 🔐 SSH налаштування
- Авторизація ТІЛЬКИ по ключам (паролі вимкнені)
- Strong crypto = yes
- Host key size = 4096
- Секція для додавання SSH публічних ключів

#### 🌐 Налаштування інтерфейсів
- **ether1**: Завжди WAN (DHCP client, NAT)
- **ether2-5**: Автоматично в bridge
- **WiFi**: Всі інтерфейси вимкнені
- **Bridge**: br_x з VXLAN та всіма LAN портами

#### 🛡️ IP Services обмеження
- Telnet, FTP, WWW, API - вимкнені
- SSH - тільки з VPN мережі
- Winbox - тільки з VPN мережі

#### 🔒 Додаткова безпека
- MAC server вимкнено
- Bandwidth server вимкнено
- UPnP вимкнено
- IP Cloud вимкнено
- SOCKS вимкнено
- HTTP Proxy вимкнено
- Neighbor Discovery тільки на визначених інтерфейсах

#### ⚙️ System налаштування
- NTP клієнт (time.google.com, time.cloudflare.com)
- Logging (critical, error, warning, firewall)
- Timezone: Europe/Kiev

### 2. 🔧 Новий скрипт: prepare_config.sh

Файл: `scripts/prepare_config.sh`

**Функціональність:**
- Автоматичне додавання SSH ключа до конфігурації
- Інтерактивний вибір ключа або введення
- Автоматичний пошук стандартних ключів (~/.ssh/id_*.pub)
- Валідація формату SSH ключа
- Створення backup перед змінами
- Детальні інструкції після підготовки

**Використання:**
```bash
./scripts/prepare_config.sh peer4
./scripts/prepare_config.sh peer4 ~/.ssh/id_ed25519.pub
make prepare-config NAME=peer4
make prepare-config NAME=peer4 KEY=~/.ssh/id_ed25519.pub
```

### 3. 📚 Нова документація

#### SECURITY.md
Повний посібник з безпеки, включає:
- Огляд всіх налаштувань безпеки
- Детальний опис firewall правил
- Інструкції по SSH ключам
- Мережева топологія
- Захист від атак
- Моніторинг безпеки
- Troubleshooting
- Backup та відновлення

#### CHECKLIST.md
Швидкий чеклист для додавання клієнта:
- Покрокова інструкція
- Всі необхідні команди
- Перевірки після кожного кроку
- Швидка допомога
- Корисні команди

### 4. 🔄 Оновлення існуючої документації

#### README.md
- Додано інформацію про безпеку в розділ "Особливості"
- Оновлено інструкції по імпорту конфігурації
- Додано важливі попередження про SSH ключі
- Посилання на SECURITY.md

#### QUICKSTART.md
- Додано крок підготовки SSH ключа
- Додано крок prepare_config
- Оновлено команди
- Детальніше описано що налаштовується автоматично

#### Makefile
- Додано команду `prepare-config`

---

## 🔐 Налаштування безпеки

### Що захищено автоматично:

✅ **SSH авторизація**
   - Тільки по ключам (Ed25519/RSA)
   - Паролі вимкнені
   - Доступ тільки з VPN мережі

✅ **Firewall**
   - Закритий INPUT chain
   - Обмежений FORWARD chain
   - RAW chain для захисту від атак
   - Блокування bridge → Internet

✅ **Захист від атак**
   - Port scan detection → блокування на 1 день
   - SSH brute force → 4-етапний захист
   - Drop invalid packets

✅ **Мережева ізоляція**
   - ether1 = WAN (окремо)
   - ether2+ = bridge (разом з VXLAN)
   - WiFi вимкнені
   - Клієнти bridge БЕЗ доступу до інтернету

✅ **Обмеження сервісів**
   - SSH/Winbox тільки з VPN
   - Всі інші сервіси вимкнені
   - MAC server вимкнено
   - Cloud, UPnP, SOCKS вимкнені

---

## 📋 Робочий процес (оновлений)

### Раніше:
1. `make add-client NAME=peer4 IP=10.66.66.5`
2. Імпорт `peer4.rsc` на роутер
3. ❌ Доступ через пароль з будь-якого місця

### Тепер:
1. `make add-client NAME=peer4 IP=10.66.66.5`
2. **`make prepare-config NAME=peer4`** ← НОВИЙ КРОК
3. Імпорт `peer4.rsc` на роутер
4. ✅ Доступ ТІЛЬКИ через SSH ключ з VPN

---

## ⚠️ ВАЖЛИВІ ЗМІНИ ДЛЯ КОРИСТУВАЧІВ

### 🚨 Обов'язкові дії перед імпортом:

1. **Створіть SSH ключ** (якщо немає):
   ```bash
   ssh-keygen -t ed25519 -C "mikrotik_key"
   ```

2. **Додайте SSH ключ до конфігурації**:
   ```bash
   make prepare-config NAME=peer4
   ```

3. **Створіть backup на роутері**:
   ```
   /system backup save name=before-vpn
   ```

4. **Майте альтернативний доступ**:
   - MAC-Winbox (через MAC адресу)
   - Serial console
   - Фізичний доступ

### 🔒 Після імпорту:

- ✅ SSH: `ssh admin@10.66.66.5` (тільки з VPN)
- ✅ Winbox: `10.66.66.5:8291` (тільки з VPN)
- ❌ Пароль SSH НЕ працює (тільки ключі)
- ❌ Доступ з WAN заблокований
- ❌ WiFi вимкнені

---

## 🎯 Приклад повного циклу

```bash
# 1. Активувати venv
source venv/bin/activate

# 2. Додати клієнта на сервер
make add-client NAME=peer4 IP=10.66.66.5

# 3. Згенерувати SSH ключ (якщо немає)
ssh-keygen -t ed25519 -C "peer4_key"

# 4. Підготувати конфігурацію з SSH ключем
make prepare-config NAME=peer4

# 5. Скопіювати на роутер та імпортувати
# (через MAC-Winbox або консоль)
# /import file=peer4.rsc

# 6. Підключитися через VPN
ssh admin@10.66.66.5
```

---

## 📊 Статистика проекту

### Файли створено/оновлено:
- ✅ 1 шаблон оновлено (client_config.rsc.j2)
- ✅ 1 новий скрипт (prepare_config.sh)
- ✅ 2 нові документи (SECURITY.md, CHECKLIST.md)
- ✅ 3 документи оновлено (README.md, QUICKSTART.md, Makefile)

### Рядків коду додано:
- Шаблон: ~300 рядків (з 100 до 400+)
- Скрипт: ~150 рядків
- Документація: ~700 рядків
- **Всього: ~1150 рядків**

---

## 🔍 Технічні деталі

### Firewall INPUT chain:
```
Accept: established/related
Accept: ICMP (VPN + bridge)
Accept: SSH port 22 (VPN only)
Accept: Winbox port 8291 (VPN only)
Accept: від bridge
Accept: WireGuard UDP 51820 (WAN)
DROP: все з WAN
DROP: все інше
```

### Firewall FORWARD chain:
```
Accept: established/related
Accept: bridge ↔ bridge
Accept: VXLAN ↔ bridge
Accept: від VPN
DROP: bridge → Internet  ← КЛЮЧОВА ОСОБЛИВІСТЬ
DROP: invalid
DROP: від WAN
```

### Port Scan Detection:
```
21 з'єднань за 3 сек на 3 різні порти
→ address-list: port_scanners (1 день)
→ DROP all traffic
```

### SSH Brute Force Protection:
```
Спроба 1: ssh_stage1 (1 хв)
Спроба 2: ssh_stage2 (1 хв)
Спроба 3: ssh_stage3 (1 хв)
Спроба 4: ssh_blacklist (1 день) → DROP
```

---

## ✅ Готово до використання!

Проект тепер включає:
- ✅ Повну автоматизацію WireGuard на MikroTik
- ✅ Максимальну безпеку для клієнтів
- ✅ SSH авторизацію по ключам
- ✅ Детальну документацію
- ✅ Зручні інструменти (scripts + Makefile)
- ✅ Захист від атак
- ✅ Ізоляцію мереж

**Всі клієнти будуть налаштовані однаково безпечно!** 🎉🔐
