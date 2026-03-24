import os

from PyQt6.QtCore import QByteArray, QDate, QSize, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFileDialog,
    QDateEdit,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QColor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


def apply_style(widget, filename):
    # Применяем qss-стили к окну из файла.
    try:
        full_path = os.path.join(ASSETS_DIR, filename)
        with open(full_path, "r", encoding="utf-8") as file:
            widget.setStyleSheet(file.read())
    except FileNotFoundError:
        print(f"Предупреждение: файл {filename} не найден")


class LoginWindow(QWidget):
    def __init__(self):
        # Создаем простое окно входа с кнопкой.
        super().__init__()
        self.setWindowTitle("Вход в систему")
        self.setFixedSize(QSize(350, 200))

        apply_style(self, "login_screen.qss")

        layout = QVBoxLayout()
        self.label = QLabel("Добро пожаловать в телефонную книгу")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button = QPushButton("Войти")
        self.button.setFixedSize(150, 40)

        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)


class CreateEditWindow(QWidget):
    def __init__(self, backend):
        # Создаем форму для добавления и редактирования контакта.
        super().__init__()
        self.backend = backend
        self.setWindowTitle("Создать/Редактировать")
        self.setFixedSize(QSize(400, 750))
        self.photo_bytes = None

        apply_style(self, "create_edit_screen.qss")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(30, 20, 30, 20)

        self.btn_photo = QPushButton("+")
        self.btn_photo.setObjectName("photoButton")
        self.btn_photo.setFixedSize(120, 120)
        self.label = QLabel("ФИО")
        self.input_name = QLineEdit()
        self.label1 = QLabel("Номер")
        self.input_number = QLineEdit()
        self.label2 = QLabel("Email")
        self.input_email = QLineEdit()
        self.label3 = QLabel("Адрес")
        self.input_address = QLineEdit()
        self.label4 = QLabel("Дата рождения")
        self.input_date = QDateEdit()
        self.btn_save = QPushButton("Сохранить")
        self.btn_save.setObjectName("saveButton")

        self.btn_save.clicked.connect(self.save_contact)
        self.btn_photo.clicked.connect(self.pick_photo)

        layout.addWidget(self.btn_photo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        layout.addWidget(self.input_name)
        layout.addWidget(self.label1)
        layout.addWidget(self.input_number)
        layout.addWidget(self.label2)
        layout.addWidget(self.input_email)
        layout.addWidget(self.label3)
        layout.addWidget(self.input_address)
        layout.addWidget(self.label4)
        layout.addWidget(self.input_date)
        layout.addSpacing(20)
        layout.addWidget(self.btn_save, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def pick_photo(self):
        # Выбираем фото с диска и подставляем в кнопку.
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите фото",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "rb") as file:
                self.photo_bytes = file.read()

            from PyQt6.QtGui import QIcon
            pixmap = QPixmap(file_path).scaled(
                120, 120,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.btn_photo.setText("")
            self.btn_photo.setIcon(QIcon(pixmap))
            self.btn_photo.setIconSize(QSize(120, 120))
        except OSError:
            QMessageBox.warning(self, "Ошибка", "Не удалось прочитать файл фото")

    def save_contact(self):
        # Сохраняем контакт: создаем новый или обновляем текущий.
        data = {
            "full_name": self.input_name.text(),
            "phone_number": self.input_number.text(),
            "email": self.input_email.text(),
            "address": self.input_address.text(),
            "birth_date": self.input_date.date().toPyDate().isoformat(),
        }

        if hasattr(self, "current_id") and self.current_id:
            result = self.backend.update_contact(self.current_id, data)
        else:
            result = self.backend.create_contact(data)

        if result and self.photo_bytes is not None:
            photo_result = self.backend.add_photo(result["id"], self.photo_bytes)
            if photo_result:
                result = photo_result

        if result:
            QMessageBox.information(self, "Успех", "Данные сохранены!")
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить данные")

    def load_contact_data(self, data):
        # Загружаем данные контакта в форму редактирования.
        self.current_id = data.get("id")
        self.input_name.setText(data.get("full_name", ""))
        self.input_number.setText(data.get("phone_number", ""))
        self.input_email.setText(data.get("email", ""))
        self.input_address.setText(data.get("address", ""))

        date_str = data.get("birth_date")
        if date_str:
            self.input_date.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))


class MainWindow(QMainWindow):
    def __init__(self, backend):
        # Создаем главное окно с таблицей и кнопками.
        super().__init__()
        self.backend = backend
        self.setWindowTitle("Телефонная книга")
        self.resize(1250, 700)

        apply_style(self, "main_screen.qss")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        outer_layout = QVBoxLayout(self.central_widget)
        outer_layout.setSpacing(10)
        outer_layout.setContentsMargins(10, 10, 10, 10)

        search_row = QHBoxLayout()
        search_row.addStretch()
        search_label = QLabel("Поиск по ФИО:")
        search_label.setObjectName("searchLabel")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите ФИО...")
        self.search_input.setFixedWidth(280)
        self.search_input.setObjectName("searchInput")
        self.btn_search = QPushButton("Найти")
        self.btn_search.setObjectName("searchButton")
        self.btn_search.setFixedWidth(100)
        self.btn_search.clicked.connect(self.search_contact)
        search_row.addWidget(search_label)
        search_row.addWidget(self.search_input)
        search_row.addWidget(self.btn_search)
        outer_layout.addLayout(search_row)

        self.main_layout = QHBoxLayout()
        outer_layout.addLayout(self.main_layout)

        self.setup_table()
        self.setup_controls()

    def setup_table(self):
        # Настраиваем таблицу для отображения контактов.
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Фото", "ФИО", "Телефон", "Email", "Дата рождения", "Адрес"]
        )
        header = self.table.horizontalHeader()
        self.table.setFrameStyle(0)

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 40)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 100)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 150)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 100)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.main_layout.addWidget(self.table, stretch=2)

    def setup_controls(self):
        # Создаем и подключаем кнопки управления.
        self.button_layout = QVBoxLayout()
        self.button_layout.setSpacing(20)
        self.button_layout.setContentsMargins(20, 20, 20, 20)

        self.btn_create = QPushButton("Создать")
        self.btn_delete = QPushButton("Удалить")
        self.btn_get = QPushButton("Получить")
        self.btn_update = QPushButton("Обновить")
        self.btn_sort = QPushButton("Сортировать")
        self.btn_tree = QPushButton("Порядок ДОП")

        self.btn_create.clicked.connect(self.open_create_window)
        self.btn_get.clicked.connect(self.refresh_data)
        self.btn_update.clicked.connect(self.open_edit_window)
        self.btn_delete.clicked.connect(self.delete_contact)
        self.btn_sort.clicked.connect(self.sort_contacts)
        self.btn_tree.clicked.connect(self.show_optimal_tree_order)

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.btn_create)
        self.button_layout.addWidget(self.btn_delete)
        self.button_layout.addWidget(self.btn_get)
        self.button_layout.addWidget(self.btn_update)
        self.button_layout.addWidget(self.btn_sort)
        self.button_layout.addWidget(self.btn_tree)
        self.button_layout.addStretch()

        self.main_layout.addLayout(self.button_layout, stretch=0)

    def open_create_window(self):
        # Открываем окно создания нового контакта.
        self.edit_window = CreateEditWindow(self.backend)
        self.edit_window.destroyed.connect(self.refresh_data)
        self.edit_window.show()

    def refresh_data(self):
        # Загружаем данные из БД и обновляем таблицу.
        try:
            contacts = self.backend.get_contacts()
            self._populate_table(contacts)
        except Exception as error:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось загрузить данные: {error}")

    def sort_contacts(self):
        # Сортируем контакты и показываем результат в таблице.
        try:
            contacts = self.backend.sort_contacts()
            self._populate_table(contacts)
        except Exception as error:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить сортировку: {error}")

    def show_optimal_tree_order(self):
        # Строим ДОП и выводим записи в порядке inorder.
        try:
            tree = self.backend.build_optimal_search_tree()
            if not tree:
                QMessageBox.information(self, "ДОП", "Нет данных для построения дерева")
                return
            contacts = []
            self._inorder_traverse(tree, contacts)
            self._populate_table(contacts)
        except Exception as error:
            QMessageBox.critical(self, "Ошибка", f"Не удалось построить ДОП: {error}")

    def _inorder_traverse(self, node, result):
        # Обходим дерево симметрично и собираем контакты.
        if node is None:
            return
        self._inorder_traverse(node.get("left"), result)
        result.append(node["contact"])
        self._inorder_traverse(node.get("right"), result)

    def search_contact(self):
        # Ищем контакт выбранным способом и подсвечиваем строку.
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Поиск", "Введите ФИО для поиска")
            return

        try:
            mode = self._ask_search_mode()
            if mode is None:
                return

            if mode == "binary":
                result = self.backend.binary_search_by_full_name(query)
            else:
                tree = self.backend.build_optimal_search_tree()
                if not tree:
                    QMessageBox.information(self, "Поиск", "Нет данных для поиска по дереву")
                    return
                result = self.backend.search_in_optimal_tree(tree, query)

            if result:
                contacts = self.backend.sort_contacts()
                self._populate_table(contacts)
                self._highlight_found_contact(result)
            else:
                QMessageBox.information(self, "Поиск", f"Контакт '{query}' не найден")
        except Exception as error:
            QMessageBox.critical(self, "Ошибка", f"Ошибка поиска: {error}")

    def _ask_search_mode(self):
        # Спрашиваем у пользователя метод поиска.
        box = QMessageBox(self)
        box.setWindowTitle("Поиск")
        box.setText("Выберите способ поиска")

        binary_button = box.addButton("Бинарный", QMessageBox.ButtonRole.AcceptRole)
        tree_button = box.addButton("По дереву", QMessageBox.ButtonRole.AcceptRole)
        box.addButton("Отмена", QMessageBox.ButtonRole.RejectRole)

        box.exec()
        clicked_button = box.clickedButton()

        if clicked_button == binary_button:
            return "binary"
        if clicked_button == tree_button:
            return "tree"
        return None

    def _highlight_found_contact(self, contact):
        # Подсвечиваем найденный контакт в таблице.
        target_id = str(contact.get("id", ""))

        for row in range(self.table.rowCount()):
            item_id = self.table.item(row, 0)
            if item_id is None:
                continue
            if item_id.text() != target_id:
                continue

            name_item = self.table.item(row, 2)
            self.table.selectRow(row)
            if name_item:
                self.table.scrollToItem(name_item)

            for col in range(self.table.columnCount()):
                cell = self.table.item(row, col)
                if cell:
                    cell.setBackground(QColor("#4a90d9"))
            break

    def _populate_table(self, contacts):
        # Заполняем таблицу списком контактов.
        self.table.setRowCount(0)
        self.table.setRowCount(len(contacts))
        self.table.setIconSize(QSize(80, 80))
        for row_number, contact in enumerate(contacts):
            self.table.setRowHeight(row_number, 90)

            item_id = QTableWidgetItem(str(contact.get("id", "")))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_number, 0, item_id)

            photo_bytes = contact.get("photo")
            if photo_bytes:
                pixmap = QPixmap()
                pixmap.loadFromData(QByteArray(bytes(photo_bytes)))
                scaled = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                label = QLabel()
                label.setPixmap(scaled)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setCellWidget(row_number, 1, label)
            else:
                item_photo = QTableWidgetItem("—")
                item_photo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_number, 1, item_photo)

            rest = [
                contact.get("full_name", ""),
                contact.get("phone_number", ""),
                contact.get("email", ""),
                contact.get("birth_date", ""),
                contact.get("address", ""),
            ]
            for col_offset, text in enumerate(rest):
                item = QTableWidgetItem(str(text) if text else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_number, col_offset + 2, item)

    def delete_contact(self):
        # Удаляем выбранную запись после подтверждения.
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return

        contact_id = self.table.item(selected_row, 0).text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить запись ID {contact_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            if self.backend.delete_contact(contact_id):
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить запись")

    def open_edit_window(self):
        # Открываем окно редактирования выбранного контакта.
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return

        contact_data = {
            "id": self.table.item(selected_row, 0).text(),
            "full_name": self.table.item(selected_row, 2).text(),
            "phone_number": self.table.item(selected_row, 3).text(),
            "email": self.table.item(selected_row, 4).text(),
            "birth_date": self.table.item(selected_row, 5).text(),
            "address": self.table.item(selected_row, 6).text(),
        }

        self.edit_window = CreateEditWindow(self.backend)
        self.edit_window.load_contact_data(contact_data)
        self.edit_window.destroyed.connect(self.refresh_data)
        self.edit_window.show()


class Controller:
    def __init__(self, backend):
        # Связываем окна и стартуем с окна входа.
        self.backend = backend
        self.login_window = LoginWindow()
        self.main_window = None
        self.login_window.button.clicked.connect(self.show_main_and_close_login)

    def show_main_and_close_login(self):
        # Показываем главное окно и закрываем окно входа.
        self.main_window = MainWindow(self.backend)
        self.main_window.show()
        self.login_window.close()
