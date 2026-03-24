import psycopg
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional


class ContactCreate(BaseModel):
    full_name: str
    birth_date: Optional[str] = None
    phone_number: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None


class ContactUpdate(BaseModel):
    full_name: str
    birth_date: Optional[str] = None
    phone_number: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None


class TreeNode:
    def __init__(self, key, contact):
        # Создаем узел дерева с контактом и ссылками на детей.
        self.key = key
        self.contact = contact
        self.left = None
        self.right = None

    def to_dict(self):
        # Переводим узел и его поддеревья в словарь.
        return {
            "key": self.key,
            "contact": self.contact,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }


class Backend:
    def __init__(self, connection):
        # Сохраняем подключение к БД и память для списка контактов.
        self.connection = connection
        self.memory_data = []

    def _row_to_dict(self, row):
        # Преобразуем строку из БД в словарь контакта.
        return {
            "id": row[0],
            "full_name": row[1] if row[1] else "",
            "birth_date": row[2].isoformat() if row[2] else "",
            "phone_number": row[3] if row[3] else "",
            "email": row[4] if row[4] else "",
            "address": row[5] if row[5] else "",
            "photo": row[6]
        }

    def _normalize_data(self, data):
        # Очищаем и нормализуем входные поля перед валидацией.
        return {
            "full_name": data.get("full_name", "").strip(),
            "birth_date": data.get("birth_date") or None,
            "phone_number": data.get("phone_number", "").strip(),
            "email": data.get("email") or None,
            "address": data.get("address") or None
        }

    def load_to_memory(self):
        # Загружаем контакты в память для сортировки и поиска.
        self.memory_data = self.get_contacts()
        return self.memory_data

    def get_contacts(self):
        # Читаем все контакты из базы по возрастанию id.
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, full_name, birth_date, phone_number, email, address, photo
                FROM contacts
                ORDER BY id
            """)
            rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append(self._row_to_dict(row))
        return result

    def create_contact(self, data):
        # Создаем новый контакт после проверки данных.
        try:
            data = self._normalize_data(data)
            contact = ContactCreate(**data)
        except ValidationError:
            return None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO contacts (full_name, birth_date, phone_number, email, address, photo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, full_name, birth_date, phone_number, email, address, photo
                """, (
                    contact.full_name,
                    contact.birth_date,
                    contact.phone_number,
                    contact.email,
                    contact.address,
                    None
                ))
                row = cursor.fetchone()

            self.connection.commit()
            return self._row_to_dict(row)

        except psycopg.Error:
            self.connection.rollback()
            return None

    def update_contact(self, contact_id, data):
        # Обновляем контакт по id после валидации.
        try:
            data = self._normalize_data(data)
            contact = ContactUpdate(**data)
        except ValidationError:
            return None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE contacts
                    SET full_name = %s,
                        birth_date = %s,
                        phone_number = %s,
                        email = %s,
                        address = %s,
                        updated_at = now()
                    WHERE id = %s
                    RETURNING id, full_name, birth_date, phone_number, email, address, photo
                """, (
                    contact.full_name,
                    contact.birth_date,
                    contact.phone_number,
                    contact.email,
                    contact.address,
                    int(contact_id)
                ))
                row = cursor.fetchone()

            self.connection.commit()

            if row is None:
                return None

            return self._row_to_dict(row)

        except psycopg.Error:
            self.connection.rollback()
            return None

    def delete_contact(self, contact_id):
        # Удаляем контакт по id.
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM contacts WHERE id = %s", (int(contact_id),))
                deleted_count = cursor.rowcount

            self.connection.commit()
            return deleted_count > 0

        except psycopg.Error:
            self.connection.rollback()
            return False

    def add_photo(self, contact_id, photo_bytes):
        # Добавляем фото контакту по id.
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE contacts
                    SET photo = %s,
                        updated_at = now()
                    WHERE id = %s
                    RETURNING id, full_name, birth_date, phone_number, email, address, photo
                """, (photo_bytes, int(contact_id)))
                row = cursor.fetchone()

            self.connection.commit()

            if row is None:
                return None

            return self._row_to_dict(row)

        except psycopg.Error:
            self.connection.rollback()
            return None

    def remove_photo(self, contact_id):
        # Удаляем фото у контакта по id.
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE contacts
                    SET photo = NULL,
                        updated_at = now()
                    WHERE id = %s
                    RETURNING id, full_name, birth_date, phone_number, email, address, photo
                """, (int(contact_id),))
                row = cursor.fetchone()

            self.connection.commit()

            if row is None:
                return None

            return self._row_to_dict(row)

        except psycopg.Error:
            self.connection.rollback()
            return None

    def sort_contacts(self):
        # Сортируем контакты по ФИО быстрым алгоритмом.
        self.load_to_memory()
        if len(self.memory_data) > 1:
            self._quick_sort(self.memory_data, 0, len(self.memory_data) - 1)
        return self.memory_data

    def _quick_sort(self, arr, low, high):
        # Рекурсивно сортируем часть массива quick sort.
        if low < high:
            pivot_index = self._partition(arr, low, high)
            self._quick_sort(arr, low, pivot_index - 1)
            self._quick_sort(arr, pivot_index + 1, high)

    def _partition(self, arr, low, high):
        # Делим массив относительно опорного элемента.
        pivot = arr[high]["full_name"].lower()
        i = low - 1

        for j in range(low, high):
            if arr[j]["full_name"].lower() <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]

        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    def binary_search_by_full_name(self, full_name):
        # Ищем контакт бинарным поиском в отсортированном списке.
        sorted_contacts = self.sort_contacts()
        target = full_name.strip().lower()

        left = 0
        right = len(sorted_contacts) - 1

        while left <= right:
            middle = (left + right) // 2
            current_name = sorted_contacts[middle]["full_name"].lower()

            if current_name == target:
                return sorted_contacts[middle]
            elif current_name < target:
                left = middle + 1
            else:
                right = middle - 1

        return None

    def build_optimal_search_tree(self):
        # Строим ДОП и возвращаем только дерево.
        result = self.get_optimal_search_data()
        return result["tree"]

    def get_optimal_search_data(self):
        # Строим ДОП и возвращаем дерево и таблицы алгоритма.
        contacts = self.sort_contacts()

        if not contacts:
            return {
                "contacts": [],
                "keys": [],
                "tree": None,
                "cost_table": [],
                "root_table": []
            }

        weights = self._get_weights(contacts)
        cost_table, root_table = self._algorithm_a1(weights)
        tree = self._build_tree(contacts, root_table, 0, len(contacts) - 1)

        normalized_cost = []
        normalized_root = []
        n = len(contacts)

        for i in range(n):
            cost_row = []
            root_row = []
            for j in range(n):
                if j < i:
                    cost_row.append(None)
                    root_row.append(None)
                    continue

                cost_row.append(cost_table[i][j])
                root_row.append(root_table[i][j] + 1)

            normalized_cost.append(cost_row)
            normalized_root.append(root_row)

        return {
            "contacts": contacts,
            "keys": [contact["full_name"] for contact in contacts],
            "tree": tree.to_dict() if tree else None,
            "cost_table": normalized_cost,
            "root_table": normalized_root
        }

    def _get_weights(self, contacts):
        # Задаем веса ключей для алгоритма A1.
        weights = []
        for _ in contacts:
            weights.append(1)
        return weights

    def _algorithm_a1(self, weights):
        # Считаем матрицы стоимости и корней для ДОП.
        n = len(weights)

        cost = []
        root = []

        for _ in range(n):
            cost.append([0] * n)
            root.append([0] * n)

        for i in range(n):
            cost[i][i] = weights[i]
            root[i][i] = i

        for length in range(2, n + 1):
            for left in range(0, n - length + 1):
                right = left + length - 1
                cost[left][right] = float("inf")

                total_weight = 0
                for k in range(left, right + 1):
                    total_weight += weights[k]

                for r in range(left, right + 1):
                    left_cost = cost[left][r - 1] if r > left else 0
                    right_cost = cost[r + 1][right] if r < right else 0
                    current_cost = left_cost + right_cost + total_weight

                    if current_cost < cost[left][right]:
                        cost[left][right] = current_cost
                        root[left][right] = r

        return cost, root

    def _build_tree(self, contacts, root_table, left, right):
        # Собираем дерево из таблицы корней.
        if left > right:
            return None

        root_index = root_table[left][right]
        node = TreeNode(contacts[root_index]["full_name"], contacts[root_index])

        node.left = self._build_tree(contacts, root_table, left, root_index - 1)
        node.right = self._build_tree(contacts, root_table, root_index + 1, right)

        return node

    def search_in_optimal_tree(self, tree, full_name):
        # Ищем контакт в уже построенном дереве ДОП.
        current = tree
        target = full_name.strip().lower()

        while current is not None:
            current_key = current["key"].lower()

            if current_key == target:
                return current["contact"]
            elif target < current_key:
                current = current["left"]
            else:
                current = current["right"]

        return None
