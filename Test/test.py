import sys
import os
sys.path.append('..')
from backend import Backend
import psycopg


def run_tests():
    conn = psycopg.connect(
        host="localhost",
        port="5433",
        dbname="phonebook",
        user="phonebook_user",
        password="phonebook"
    )
    
    backend = Backend(conn)
    
    print("Тест 1: Пустое ФИО")
    data = {
        "full_name": "",
        "phone_number": "+7 (999) 111-11-11",
        "email": "test1@example.com",
        "address": "Москва",
        "birth_date": "1990-01-01"
    }
    r = backend.create_contact(data)
    if r and r["full_name"] == "":
        print("  -")
        backend.delete_contact(r["id"])
    else:
        print("  +")
    
    print("Тест 2: Пустой телефон")
    data = {
        "full_name": "Иванов",
        "phone_number": "",
        "email": "test2@example.com",
        "address": "Москва",
        "birth_date": "1990-01-01"
    }
    r = backend.create_contact(data)
    if r and r["phone_number"] == "":
        print("  -")
        if r:
            backend.delete_contact(r["id"])
    else:
        print("  +")
    
    print("Тест 3: Некорректный email")
    data = {
        "full_name": "Иванов",
        "phone_number": "+7 (999) 222-22-22",
        "email": "lala-email",
        "address": "Москва",
        "birth_date": "1990-01-01"
    }
    r = backend.create_contact(data)
    if r is None:
        print("  +")
    else:
        print("  -")
        if r:
            backend.delete_contact(r["id"])
    
    print("Тест 4: Некорректная дата")
    data = {
        "full_name": "Иванов",
        "phone_number": "+7 (999) 333-33-33",
        "email": "test4@example.com",
        "address": "Москва",
        "birth_date": "2024-13-32"
    }
    r = backend.create_contact(data)
    if r is None:
        print("  +")
    else:
        print("  -")
        if r:
            backend.delete_contact(r["id"])
    
    print("Тест 5: Дубликат телефона")
    data1 = {
        "full_name": "Первый",
        "phone_number": "+7 (999) 444-44-44",
        "email": "first@example.com",
        "address": "Москва",
        "birth_date": "1990-01-01"
    }
    r1 = backend.create_contact(data1)
    data2 = {
        "full_name": "Второй",
        "phone_number": "+7 (999) 444-44-44",
        "email": "second@example.com",
        "address": "фвпыицуа",
        "birth_date": "1995-05-05"
    }
    r2 = backend.create_contact(data2)
    if r2 is None:
        print("  +")
    else:
        print("  -")
    if r1:
        backend.delete_contact(r1["id"])
    if r2:
        backend.delete_contact(r2["id"])
    
    print("Тест 6: SQL инъекция")
    data = {
        "full_name": "Иванов'; DROP TABLE contacts; --",
        "phone_number": "+7 (999) 555-55-55",
        "email": "test6@example.com",
        "address": "Москва",
        "birth_date": "1990-01-01"
    }
    r = backend.create_contact(data)
    if r and r["full_name"] == data["full_name"]:
        print("  +")
        backend.delete_contact(r["id"])
    else:
        print("  -")
    
    print("Тест 7: Ввод длинной строки")
    long_text = "A" * 10000
    data = {
        "full_name": long_text,
        "phone_number": long_text,
        "email": "test7@example.com",
        "address": long_text,
        "birth_date": "1990-01-01"
    }

    r = backend.create_contact(data)
    if r is None:
        print("  +")
    else:
        print("  -")
        if r:
            backend.delete_contact(r["id"])
    
    print("Тест 8: Обновление с неправильным форматом ID")
    data = {
        "full_name": "Обновление",
        "phone_number": "+7 (999) 000-00-00"
    }
    try:
        r = backend.update_contact("abc", data)
        if r is None:
            print("  +")
        else:
            print("  -")
    except Exception as e:
        print(f"{type(e).__name__}")
    
    print("Тест 9: Удаление с неправильным форматом ID")
    try:
        r = backend.delete_contact("abc")
        if r is False:
            print("  +")
        else:
            print("  -")
    except Exception as e:
        print(f"{type(e).__name__}")
    
    print("Тест 10: Несуществующий ID (update)")
    data = {
        "full_name": "Тест",
        "phone_number": "+7 (999) 000-00-00"
    }
    r = backend.update_contact(99999, data)
    if r is None:
        print("  +")
    else:
        print("  -")
    
    print("Тест 11: Несуществующий ID (delete)")
    r = backend.delete_contact(99999)
    if r is False:
        print("  +")
    else:
        print("  -")
    
    conn.close()


if __name__ == "__main__":
    run_tests()