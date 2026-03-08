#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки функціональності генерації ключів.
Використовується для CI/CD або локального тестування.
"""

import sys
import tempfile
from pathlib import Path

# Додати scripts до шляху
sys.path.insert(0, str(Path(__file__).parent))

from generate_keys import generate_keys_set, derive_public_key


def test_key_generation():
    """Тест генерації ключів."""
    print("🧪 Тестування генерації ключів...")
    
    keys = generate_keys_set("test_client")
    
    # Перевірки
    assert keys['client_name'] == "test_client", "Неправильне ім'я клієнта"
    assert len(keys['private_key']) == 44, "Неправильна довжина приватного ключа"
    assert len(keys['public_key']) == 44, "Неправильна довжина публічного ключа"
    assert len(keys['preshared_key']) == 44, "Неправильна довжина preshared ключа"
    
    print("  ✅ Генерація ключів працює")
    return True


def test_public_key_derivation():
    """Тест отримання публічного ключа з приватного."""
    print("🧪 Тестування отримання публічного ключа...")
    
    # Відомий приватний ключ сервера
    private_key = "6EasMCGDrnk0GZrwIjJnO2GP9whr7dSll8k6TjwTfXA="
    expected_public_key = "QmOqGj4vAgWfmVxkc0xoqQZ4N7+P833VHs+xXJdhCxY="
    
    public_key = derive_public_key(private_key)
    
    assert public_key == expected_public_key, \
        f"Неправильний публічний ключ: {public_key} != {expected_public_key}"
    
    print("  ✅ Отримання публічного ключа працює")
    return True


def test_key_consistency():
    """Тест консистентності ключів."""
    print("🧪 Тестування консистентності...")
    
    keys = generate_keys_set("test_client")
    
    # Перевірити чи публічний ключ відповідає приватному
    derived_public = derive_public_key(keys['private_key'])
    
    assert derived_public == keys['public_key'], \
        "Публічний ключ не відповідає приватному"
    
    print("  ✅ Консистентність ключів підтверджена")
    return True


def main():
    """Запуск всіх тестів."""
    print("\n" + "="*60)
    print("🧪 Запуск тестів WireGuard ключів")
    print("="*60 + "\n")
    
    tests = [
        test_key_generation,
        test_public_key_derivation,
        test_key_consistency,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"  ❌ Тест провалився: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ Помилка при виконанні тесту: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 Результати: {passed} пройдено, {failed} провалено")
    print("="*60 + "\n")
    
    if failed > 0:
        print("❌ Деякі тести провалилися!")
        sys.exit(1)
    else:
        print("✅ Всі тести пройдено успішно!")
        sys.exit(0)


if __name__ == '__main__':
    main()
