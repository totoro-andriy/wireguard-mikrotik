# 🔐 Безпека MikroTik клієнтів

Цей документ описує всі налаштування безпеки, які автоматично застосовуються до клієнтів.

## 📋 Огляд безпеки

### ✅ Що налаштовано автоматично

1. **SSH авторизація тільки по ключам**
   - Паролі вимкнені
   - Тільки Ed25519/RSA ключі
   - Доступ тільки з VPN мережі

2. **Firewall захист**
   - Закритий INPUT chain
   - Обмежений FORWARD chain
   - RAW chain для захисту від атак

3. **Обмеження мережевого доступу**
   - SSH тільки з VPN (10.66.66.0/24)
   - Winbox тільки з VPN
   - Всі інші сервіси вимкнені

4. **Вимкнені небезпечні функції**
   - WiFi інтерфейси
   - Telnet, FTP, HTTP
   - API, API-SSL
   - UPnP, SOCKS, Proxy
   - MAC server, Bandwidth server
   - IP Cloud, DDNS

5. **Захист від атак**
   - Port scan detection
   - SSH brute force protection
   - Invalid packet drop
   - Connection tracking

## 🔥 Firewall правила

### INPUT Chain (захист роутера)

```
✅ Accept: Established/Related
✅ Accept: ICMP з VPN та bridge
✅ Accept: SSH з VPN (10.66.66.0/24)
✅ Accept: Winbox з VPN (10.66.66.0/24)
✅ Accept: З bridge (локальна мережа)
✅ Accept: WireGuard UDP 51820 на WAN
❌ DROP: Все інше з WAN
❌ DROP: Все інше
```

### FORWARD Chain (routing між інтерфейсами)

```
✅ Accept: Established/Related
✅ Accept: Bridge ↔ Bridge (без обмежень всередині)
✅ Accept: VXLAN ↔ Bridge
✅ Accept: З VPN
❌ DROP: Bridge → Internet (клієнтам інтернет не потрібний)
❌ DROP: Invalid packets
❌ DROP: Все з WAN
```

### RAW Chain (захист від атак)

```
❌ DROP: Blocked IPs
🚨 Detect: Port scanners (блокування на 1 день)
❌ DROP: Port scanners
```

### NAT

```
✅ Masquerade: Тільки на WAN (ether1)
```

## 🔑 SSH налаштування

### Генерація SSH ключа

```bash
# Рекомендовано: Ed25519 (швидкий та безпечний)
ssh-keygen -t ed25519 -C "peer4_mikrotik"

# Альтернатива: RSA 4096 біт
ssh-keygen -t rsa -b 4096 -C "peer4_mikrotik"
```

### Додавання ключа до конфігурації

```bash
# Автоматично (рекомендовано)
make prepare-config NAME=peer4

# Вручну - відредагуйте generated_configs/peer4.rsc:
/user ssh-keys
add key="ssh-ed25519 AAAAC3NzaC1lZDI1... user@host" user=admin
```

### Підключення через SSH

```bash
# З VPN мережі (після імпорту конфігурації)
ssh admin@10.66.66.5

# Якщо ключ не за замовчуванням
ssh -i ~/.ssh/mikrotik_key admin@10.66.66.5
```

## 🌐 Мережева топологія

### Інтерфейси

```
ether1      → WAN (DHCP client, NAT)
ether2-5    → Bridge (br_x)
wg0         → WireGuard VPN
vxlan1      → VXLAN (в bridge)
br_x        → Bridge (локальна мережа + VXLAN)
```

### IP адресація

```
WAN (ether1):    Отримує через DHCP
VPN (wg0):       10.66.66.X/24
Bridge (br_x):   Отримує через DHCP від сервера (172.16.0.0/16)
```

### Потоки трафіку

```
✅ Дозволено:
   - Bridge clients → VXLAN → Інші клієнти
   - VPN → Роутер (SSH, Winbox)
   - Роутер → Internet (WAN)
   - Роутер → VPN сервер

❌ Заблоковано:
   - Internet → Роутер (крім WireGuard UDP)
   - Bridge clients → Internet
   - Internet → Bridge clients
```

## 🛡️ Захист від атак

### Port Scan Detection

Автоматично виявляє та блокує port scanners:

```
21 з'єднань за 3 секунди на 3 різні порти
→ Додає IP до списку port_scanners на 1 день
→ Блокує весь трафік з цього IP
```

### SSH Brute Force Protection

Поетапний захист від брутфорсу SSH:

```
Stage 1: Нове SSH з'єднання → додає до ssh_stage1 (1 хв)
Stage 2: Повторне з'єднання → ssh_stage2 (1 хв)
Stage 3: Ще одне з'єднання → ssh_stage3 (1 хв)
Stage 4: Четверте з'єднання → ssh_blacklist (1 день)
         → Блокує весь трафік
```

### Invalid Packets

Всі пакети з невалідним connection state автоматично дропаються.

## 📊 Моніторинг безпеки

### Перевірка заблокованих IP

```
# Список port scanners
/ip firewall address-list print where list=port_scanners

# Список SSH brute force
/ip firewall address-list print where list=ssh_blacklist

# Видалити IP зі списку
/ip firewall address-list remove [find address=1.2.3.4]
```

### Логи firewall

```
# Перегляд логів
/log print where topics~"firewall"

# Фільтр критичних подій
/log print where topics~"critical"
```

### Статистика firewall

```
# Кількість дропнутих пакетів
/ip firewall filter print stats

# NAT статистика
/ip firewall nat print stats
```

## ⚙️ Додаткові налаштування

### Зміна SSH порту (опціонально)

```
/ip service
set ssh port=2222 address=10.66.66.0/24
```

Тоді в playbook додайте:
```yaml
ansible_port: 2222
```

### Додавання додаткових ether до bridge

Якщо у вас більше 5 портів:

```
/interface bridge port
add bridge=br_x interface=ether6 hw=yes
add bridge=br_x interface=ether7 hw=yes
# і т.д.
```

### Whitelist для SSH

Якщо потрібен доступ з певного WAN IP:

```
/ip firewall filter
add action=accept chain=input protocol=tcp dst-port=22 \
    src-address=YOUR_TRUSTED_IP comment="SSH from trusted IP" \
    place-before=[find comment="Drop all from WAN"]
```

## 🔄 Backup та відновлення

### Створення backup

```
# Full backup (включає паролі)
/system backup save name=backup-before-import

# Export конфігурації
/export file=config-backup
```

### Відновлення

```
# З backup
/system backup load name=backup-before-import

# З export
/import file=config-backup.rsc
```

## ⚠️ Важливі попередження

### ❗ Перед імпортом конфігурації

1. **ОБОВ'ЯЗКОВО створіть backup**
   ```
   /system backup save name=backup-before-automation
   ```

2. **ОБОВ'ЯЗКОВО додайте SSH ключ**
   - Інакше ви втратите доступ!
   - Використайте `make prepare-config NAME=peer4`

3. **Майте альтернативний доступ**
   - MAC-Winbox (доступ через MAC адресу)
   - Serial console
   - Фізичний доступ до роутера

### ❗ Після імпорту

1. **SSH та Winbox доступні ТІЛЬКИ з VPN**
   - Спочатку підключіться до VPN сервера
   - Потім SSH до клієнта: `ssh admin@10.66.66.X`

2. **Паролі SSH не працюють**
   - Тільки SSH ключі
   - Перевірте що ключ додано до роутера

3. **WiFi вимкнені**
   - Якщо потрібні WiFi - ввімкніть вручну
   - Додайте WiFi інтерфейси до bridge за потреби

## 🔍 Troubleshooting

### Не можу підключитися через SSH

1. Перевірте що ви в VPN мережі:
   ```bash
   ping 10.66.66.X
   ```

2. Перевірте що SSH ключ додано:
   ```
   /user ssh-keys print
   ```

3. Спробуйте з явним вказанням ключа:
   ```bash
   ssh -i ~/.ssh/your_key admin@10.66.66.X
   ```

### Втратив доступ після імпорту

1. Підключіться через MAC-Winbox:
   - Neighbor Discovery → Знайти роутер по MAC
   - Подвійний клік по MAC адресі

2. Або через serial console (якщо є фізичний доступ)

3. Відновіть з backup:
   ```
   /system backup load name=backup-before-automation
   ```

### Клієнти bridge не отримують IP

1. Перевірте DHCP клієнт на bridge:
   ```
   /ip dhcp-client print
   ```

2. Перевірте VXLAN з'єднання:
   ```
   /interface vxlan print
   ```

3. Перевірте WireGuard статус:
   ```
   /interface wireguard print
   /interface wireguard peers print
   ```

## 📚 Додаткові ресурси

- [MikroTik Security](https://wiki.mikrotik.com/wiki/Manual:Securing_Your_Router)
- [MikroTik Firewall](https://help.mikrotik.com/docs/display/ROS/Filter)
- [SSH Key Authentication](https://help.mikrotik.com/docs/display/ROS/SSH+login+without+password)
- [WireGuard on MikroTik](https://help.mikrotik.com/docs/display/ROS/WireGuard)

---

**Створено для максимальної безпеки MikroTik клієнтів**
