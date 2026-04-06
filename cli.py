import os


def print_contact(contact):
    has_photo = "yes" if contact.get("photo") else "no"
    print(
        f"[{contact['id']}] {contact['full_name']} | "
        f"{contact['phone_number']} | {contact['email']} | "
        f"{contact['birth_date']} | {contact['address']} | photo:{has_photo}"
    )


def print_help():
    print("\nКоманды:")
    print("  help                  - показать команды")
    print("  list                  - список контактов")
    print("  create                - создать контакт")
    print("  update <id>           - обновить контакт")
    print("  delete <id>           - удалить контакт")
    print("  find <ФИО>            - бинарный поиск по ФИО")
    print("  sort                  - показать отсортированный список")
    print("  treefind <телефон>    - поиск в оптимальном дереве по номеру")
    print("  dop                   - построить ДОП по телефону и показать записи")
    print("  addphoto <id> <path>  - добавить фото из файла")
    print("  delphoto <id>         - удалить фото")
    print("  exit                  - выход\n")


def ask_contact_data(old=None):
    if old is None:
        old = {
            "full_name": "",
            "phone_number": "",
            "email": "",
            "address": "",
            "birth_date": ""
        }

    full_name = input(f"ФИО [{old['full_name']}]: ").strip() or old["full_name"]
    phone_number = input(f"Телефон [{old['phone_number']}]: ").strip() or old["phone_number"]
    email = input(f"Email [{old['email']}]: ").strip() or old["email"]
    address = input(f"Адрес [{old['address']}]: ").strip() or old["address"]
    birth_date = input(f"Дата рождения YYYY-MM-DD [{old['birth_date']}]: ").strip() or old["birth_date"]

    return {
        "full_name": full_name,
        "phone_number": phone_number,
        "email": email,
        "address": address,
        "birth_date": birth_date
    }


def binary_search_sorted_contacts(sorted_contacts, full_name):
    target = full_name.strip().lower()
    left = 0
    right = len(sorted_contacts) - 1

    while left <= right:
        middle = (left + right) // 2
        current_name = sorted_contacts[middle]["full_name"].lower()

        if current_name == target:
            return sorted_contacts[middle]
        if current_name < target:
            left = middle + 1
        else:
            right = middle - 1

    return None


def dop_inorder_contacts(node, result):
    if node is None:
        return
    dop_inorder_contacts(node.get("left"), result)
    result.append(node["contact"])
    dop_inorder_contacts(node.get("right"), result)


def run_cli(backend):
    print("Телефонная книга (CLI)")
    print("Запуск в терминальном режиме. Введите 'help' для списка команд.")
    sorted_contacts = None
    tree = None

    while True:
        raw = input("> ").strip()
        if not raw:
            continue

        parts = raw.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if command == "help":
            print_help()

        elif command == "list":
            contacts = backend.get_contacts()
            if not contacts:
                print("Контактов нет.")
                continue
            for contact in contacts:
                print_contact(contact)

        elif command == "create":
            data = ask_contact_data()
            created = backend.create_contact(data)
            if created:
                sorted_contacts = None
                tree = None
                print("Контакт создан:")
                print_contact(created)
            else:
                print("Не удалось создать контакт. Проверьте данные.")

        elif command == "update":
            if not arg.isdigit():
                print("Укажите ID: update <id>")
                continue

            target = None
            for contact in backend.get_contacts():
                if str(contact["id"]) == arg:
                    target = contact
                    break

            if not target:
                print("Контакт не найден.")
                continue

            data = ask_contact_data(target)
            updated = backend.update_contact(arg, data)
            if updated:
                sorted_contacts = None
                tree = None
                print("Контакт обновлён:")
                print_contact(updated)
            else:
                print("Не удалось обновить контакт.")

        elif command == "delete":
            if not arg.isdigit():
                print("Укажите ID: delete <id>")
                continue
            if backend.delete_contact(arg):
                sorted_contacts = None
                tree = None
                print("Контакт удалён.")
            else:
                print("Не удалось удалить контакт.")

        elif command == "find":
            if not arg:
                print("Укажите ФИО: find <ФИО>")
                continue
            if sorted_contacts is None:
                print("Сначала выполните sort.")
                continue

            found = binary_search_sorted_contacts(sorted_contacts, arg)
            if found:
                print("Найдено:")
                print_contact(found)
            else:
                print("Контакт не найден.")

        elif command == "sort":
            sorted_contacts = backend.sort_contacts()
            tree = backend.build_optimal_search_tree()

            if not sorted_contacts:
                print("Контактов нет.")
                continue

            print("Отсортировано по ФИО:")
            for contact in sorted_contacts:
                print_contact(contact)

        elif command == "treefind":
            if not arg:
                print("Укажите номер телефона: treefind <телефон>")
                continue
            if tree is None:
                tree = backend.build_optimal_search_tree()

            if tree is None:
                print("Контактов нет.")
                continue

            found = backend.search_in_optimal_tree(tree, arg)
            if found:
                print("Найдено:")
                print_contact(found)
            else:
                print("Контакт не найден.")

        elif command == "dop":
            dop_data = backend.get_optimal_search_data()
            if not dop_data["contacts"]:
                print("Контактов нет.")
                continue

            sorted_contacts = dop_data["contacts"]
            tree = dop_data["tree"]
            contacts = []
            dop_inorder_contacts(tree, contacts)

            print("Порядок ДОП:")
            for contact in contacts:
                print_contact(contact)

        elif command == "addphoto":
            args = arg.split(maxsplit=1)
            if not args or not args[0].isdigit():
                print("Формат: addphoto <id> <path>")
                continue

            contact_id = args[0]
            file_path = args[1] if len(args) == 2 else input("Путь к фото: ").strip()
            file_path = file_path.strip().strip('"').strip("'")

            if not os.path.isfile(file_path):
                print("Файл не найден.")
                continue

            try:
                with open(file_path, "rb") as file:
                    photo_bytes = file.read()
            except OSError:
                print("Не удалось прочитать файл.")
                continue

            result = backend.add_photo(contact_id, photo_bytes)
            if result:
                sorted_contacts = None
                tree = None
                print("Фото добавлено.")
                print_contact(result)
            else:
                print("Не удалось добавить фото.")

        elif command == "delphoto":
            if not arg.isdigit():
                print("Укажите ID: delphoto <id>")
                continue

            result = backend.remove_photo(arg)
            if result:
                sorted_contacts = None
                tree = None
                print("Фото удалено.")
                print_contact(result)
            else:
                print("Не удалось удалить фото.")

        elif command == "exit":
            print("Выход из CLI.")
            break

        else:
            print("Неизвестная команда. Введите 'help'.")
