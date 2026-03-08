# ✅ Чеклист додавання WireGuard клієнта

## 🚀 Швидкий процес (5 хвилин)

### ☑️ Крок 1: Підготовка (1 хв)
```bash
cd /home/maestro/devel/ansible-mikrotik
source venv/bin/activate
```

### ☑️ Крок 2: Визначити IP адресу
- [ ] Перевірити зайняті IP: `make show-config`
- [ ] Вибрати вільний IP: `10.66.66.X` (де X = 5, 6, 7, ...)
- [ ] Придумати ім'я: `peer4`, `peer5`, `office-kyiv`, тощо

### ☑️ Крок 3: Додати клієнта на сервер (1 хв)
```bash
make add-client NAME=peer4 IP=10.66.66.5
```

**Що відбувається:**
- ✅ Генеруються WireGuard ключі
- ✅ Peer додається на сервер
- ✅ Окремий VXLAN інтерфейс створюється
- ✅ Конфігурація створюється в `generated_configs/peer4.rsc`
- ✅ SSH ключ MainSSH додається автоматично

### ☑️ Крок 4: Підготувати MikroTik роутер (1 хв)
- [ ] Підключитися через MAC-Winbox або консоль
- [ ] Створити backup: `/system backup save name=before-vpn`
- [ ] Скопіювати `generated_configs/peer4.rsc` на роутер

### ☑️ Крок 5: Імпортувати конфігурацію (30 сек)
```
/import file=peer4.rsc
```

**Що налаштується автоматично:**
- ✅ WireGuard VPN підключення
- ✅ VXLAN для L2 мережі
- ✅ Bridge з ether2-5 + VXLAN
- ✅ DHCP клієнт на bridge
- ✅ SSH ключ MainSSH (автоматично)
- ✅ Firewall правила
- ✅ SSH тільки з VPN по ключам
- ✅ Winbox тільки з VPN
- ✅ WiFi інтерфейси вимкнені
- ✅ Захист від атак

### ☑️ Крок 6: Перевірка (1 хв)

**З VPN мережі (з сервера або іншого клієнта):**
```bash
# Ping
ping 10.66.66.5

# SSH
ssh admin@10.66.66.5

# Winbox
# Підключитися до 10.66.66.5:8291
```

**На клієнті перевірити:**
```
# WireGuard статус
/interface wireguard peers print

# VXLAN статус
/interface vxlan vteps print

# Отриманий IP з bridge
/ip dhcp-client print

# Firewall працює
/ip firewall filter print stats
```

---

## 🔄 Масове додавання

### ☑️ Створити CSV файл
```csv
client_name,client_ip
peer4,10.66.66.5
peer5,10.66.66.6
peer6,10.66.66.7
```

### ☑️ Запустити масове додавання
```bash
make bulk-add FILE=clients.csv
```

### ☑️ Готово! 
Всі конфігурації з SSH ключем створені автоматично

---

## ⚠️ Важливі нагадування

- [ ] **ЗАВЖДИ створюйте backup** перед імпортом: `/system backup save`
- [ ] **SSH ключ MainSSH додається автоматично** до всіх конфігурацій
- [ ] **Майте альтернативний доступ** (MAC-Winbox, консоль)
- [ ] **Після імпорту SSH/Winbox тільки з VPN** (не з WAN!)
- [ ] **Паролі SSH не працюють** - тільки ключі
- [ ] **WiFi вимкнені** - ввімкніть вручну якщо потрібно

---

## 🆘 Швидка допомога

### Не можу підключитися після імпорту
1. Використайте MAC-Winbox (через MAC адресу)
2. Перевірте чи ви в VPN мережі
3. Відновіть backup якщо потрібно

### Забув додати SSH ключ
**Не потрібно!** SSH ключ MainSSH додається автоматично до всіх конфігурацій.

### Клієнт не отримує IP через DHCP
1. Перевірте WireGuard: `/interface wireguard peers print`
2. Перевірте VXLAN: `/interface vxlan print`
3. Перевірте DHCP client: `/ip dhcp-client print`

---

## 📊 Корисні команди

```bash
# Показати всіх клієнтів на сервері
make show-config

# Перевірити з'єднання з сервером
make test

# Видалити клієнта
make remove-client NAME=peer4 IP=10.66.66.5

# Згенерувати тільки ключі
make generate-keys NAME=peer10

# Всі доступні команди
make help
```

---

## 📁 Структура файлів

```
client_keys/peer4.json           # Ключі клієнта (тільки тут!)
generated_configs/peer4.rsc      # Конфігурація для імпорту
generated_configs/peer4.rsc.backup.* # Резервні копії
```

---

## ✅ Готово!

Після виконання всіх кроків:
- ✅ Клієнт підключений до VPN сервера
- ✅ Клієнт в L2 мережі через VXLAN
- ✅ Клієнт отримує IP через DHCP (172.16.x.x)
- ✅ Максимальна безпека налаштована
- ✅ Доступ тільки через VPN

**Наступний клієнт?** Просто повторіть з новим іменем та IP! 🎉
