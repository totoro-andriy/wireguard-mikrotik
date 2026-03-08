# 🔄 Міграція на версію 1.1.0

## Зміни в архітектурі VXLAN

Версія 1.1.0 вносить важливу зміну в архітектуру VXLAN мережі.

### Що змінилося?

**Раніше (v1.0.0):**
- Один VXLAN інтерфейс `vxlan1` на сервері
- Для кожного клієнта додавався VTEP до цього інтерфейсу
- Команда: `/interface vxlan vteps add interface=vxlan1 remote-ip=...`

**Тепер (v1.1.0+):**
- Окремий VXLAN інтерфейс для кожного клієнта
- Назва: `vxlan-<client_name>`
- Кожен інтерфейс додається до bridge
- Команди:
  ```routeros
  /interface vxlan add name=vxlan-peer1 vni=100 local-address=10.66.66.1 remote-address=10.66.66.2
  /interface bridge port add interface=vxlan-peer1 bridge=br_x
  ```

### Чому це було зроблено?

**Переваги нової архітектури:**
1. ✅ **Простіше управління**: Кожен клієнт = окремий інтерфейс
2. ✅ **Легше налагодження**: Можна швидко побачити стан кожного з'єднання
3. ✅ **Чистіше видалення**: При видаленні інтерфейсу bridge port видаляється автоматично
4. ✅ **Гнучкість налаштувань**: Можна налаштовувати параметри окремо для кожного клієнта
5. ✅ **Кращий контроль**: Простіше відстежувати трафік та проблеми

### Як мігрувати існуючі клієнти?

#### Якщо ви вже використовуєте версію 1.0.0:

**Варіант 1: Повна міграція (рекомендовано для production)**

1. **Створіть резервну копію конфігурації сервера:**
   ```routeros
   /export file=backup-before-migration
   ```

2. **Видаліть старі VTEP:**
   ```routeros
   /interface vxlan vteps print
   /interface vxlan vteps remove [find interface=vxlan1]
   ```

3. **Видаліть старий VXLAN інтерфейс:**
   ```routeros
   /interface bridge port remove [find interface=vxlan1]
   /interface vxlan remove [find name=vxlan1]
   ```

4. **Додайте клієнтів заново з новою версією:**
   ```bash
   make add-client NAME=peer1 IP=10.66.66.2
   make add-client NAME=peer2 IP=10.66.66.3
   # і т.д. для всіх клієнтів
   ```

5. **Оновіть конфігурації на клієнтах:**
   - Згенеровані файли `.rsc` будуть оновлені
   - Імпортуйте їх на клієнтські роутери

**Варіант 2: Поступова міграція**

Можна залишити існуючі клієнти на старій архітектурі і додавати нових на новій:

1. Існуючі клієнти продовжують працювати з VTEP
2. Нові клієнти автоматично створюються з окремими VXLAN інтерфейсами
3. Поступово мігруйте старих клієнтів за необхідності

**УВАГА**: Обидві архітектури можуть співіснувати, але рекомендується повна міграція для уніфікації.

#### Якщо ви тільки починаєте використовувати проект:

Нічого робити не потрібно! Просто використовуйте актуальну версію.

### Перевірка після міграції

```routeros
# Перевірте VXLAN інтерфейси (має бути декілька, по одному на клієнта)
/interface vxlan print

# Перевірте bridge порти (всі vxlan-* інтерфейси мають бути в bridge)
/interface bridge port print where bridge=br_x

# Перевірте WireGuard peers
/interface wireguard peers print

# Перевірте DHCP leases (клієнти мають отримати IP)
/ip dhcp-server lease print
```

### Приклад до/після

**До міграції:**
```routeros
/interface vxlan print
# Flags: R - RUNNING
# 0  R name="vxlan1" mtu=1450 local-address=10.66.66.1 vni=100

/interface vxlan vteps print
# 0 interface=vxlan1 remote-ip=10.66.66.2
# 1 interface=vxlan1 remote-ip=10.66.66.3
# 2 interface=vxlan1 remote-ip=10.66.66.4
```

**Після міграції:**
```routeros
/interface vxlan print
# Flags: R - RUNNING
# 0  R name="vxlan-peer1" mtu=1450 local-address=10.66.66.1 remote-address=10.66.66.2 vni=100
# 1  R name="vxlan-peer2" mtu=1450 local-address=10.66.66.1 remote-address=10.66.66.3 vni=100
# 2  R name="vxlan-peer3" mtu=1450 local-address=10.66.66.1 remote-address=10.66.66.4 vni=100

/interface vxlan vteps print
# (порожньо - vteps більше не використовуються)

/interface bridge port print where bridge=br_x
# 0 bridge=br_x interface=vxlan-peer1
# 1 bridge=br_x interface=vxlan-peer2
# 2 bridge=br_x interface=vxlan-peer3
```

### Потрібна допомога?

Якщо виникли проблеми з міграцією:

1. Перевірте логи Ansible
2. Перевірте конфігурацію на сервері
3. Переконайтеся, що WireGuard з'єднання активні
4. Відновіть з резервної копії в разі необхідності

## Інші зміни в 1.1.0

- Виправлено конфігурацію ansible-lint (видалено застарілий параметр `parseable`)
- Додано детальну документацію архітектури (ARCHITECTURE.md)
- Оновлено всі шаблони та документацію
