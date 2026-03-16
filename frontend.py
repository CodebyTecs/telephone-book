from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QLineEdit, QLabel, QFormLayout, QDateEdit, 
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import QSize, Qt, QDate

# Универсальная функция загрузки стиля для конкретного виджета/окна
def apply_style(widget, path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            widget.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Предупреждение: Файл {path} не найден")

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в систему")
        self.setFixedSize(QSize(350, 200))
        
        # Применяем стиль только к этому окну
        apply_style(self, "assets/login_screen.qss")

        layout = QVBoxLayout()
        self.label = QLabel("Добро пожаловать в Телефонную книгу")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button = QPushButton("Войти")
        self.button.setFixedSize(150, 40)
        
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

class CreateEditWindow(QWidget):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.setWindowTitle("Создать/Редактировать")
        self.setFixedSize(QSize(400, 750))

        apply_style(self, "assets/create_edit_screen.qss")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(30, 20, 30, 20)

        self.btn_photo = QPushButton("+")
        self.btn_photo.setObjectName("photoButton")
        self.btn_photo.setFixedSize(120, 120)
        self.label = QLabel("ФИО")
        self.input_name = QLineEdit()
        self.label1 = QLabel("Номер")
        self.input_number= QLineEdit()
        self.label2 = QLabel("Email")
        self.input_email = QLineEdit()
        self.label3 = QLabel("Адрес")
        self.input_address = QLineEdit()
        self.label4 = QLabel("Дата рождения")
        self.input_date = QDateEdit()
        self.btn_save = QPushButton("Сохранить")
        self.btn_save.setObjectName("saveButton")

        self.btn_save.clicked.connect(self.save_contact)

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

    def save_contact(self):
        data = {
            "full_name": self.input_name.text(),
            "phone_number": self.input_number.text(),
            "email": self.input_email.text(),
            "address": self.input_address.text(),
            "birth_date": self.input_date.date().toPyDate().isoformat()
        }
        
        if hasattr(self, 'current_id') and self.current_id:
            result = self.backend.update_contact(self.current_id, data)
        else:
            result = self.backend.create_contact(data)    
        if result:
            QMessageBox.information(self, "Успех", "Данные сохранены!")
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить данные")
    
    def load_contact_data(self, data):
        self.current_id = data.get('id')
        self.input_name.setText(data.get('full_name', ''))
        self.input_number.setText(data.get('phone_number', ''))
        self.input_email.setText(data.get('email', ''))
        self.input_address.setText(data.get('address', ''))
        
        date_str = data.get('birth_date')
        if date_str:
            self.input_date.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))

class MainWindow(QMainWindow):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.setWindowTitle("Телефонная книга")
        self.resize(1250, 700)
        
        # Применяем стиль только к главному окну
        apply_style(self, "assets/main_screen.qss")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.setup_table()
        self.setup_controls()
        #self.refresh_data()

    def setup_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Фото", "ФИО", "Телефон", "Email", "Дата рождения", "Адрес"])
        header = self.table.horizontalHeader()
        self.table.setFrameStyle(0)
        
        # Задаем фиксированные размеры для узких столбцов
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed) # ID
        self.table.setColumnWidth(0, 40)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed) # Фото
        self.table.setColumnWidth(1, 100)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # ФИО будет растягиваться
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed) # Телефон
        self.table.setColumnWidth(3, 150)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch) # Email растягивается
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed) # Дата рождения
        self.table.setColumnWidth(5, 100)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch) # Адрес растягивается

        # 2. Дополнительные настройки
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False) # Скроем номера строк слева для чистоты
        
        self.main_layout.addWidget(self.table, stretch=2)

    def setup_controls(self):
        # 1. Создаем вертикальный макет для правой панели
        self.button_layout = QVBoxLayout()
        self.button_layout.setSpacing(20) # Расстояние между кнопками
        self.button_layout.setContentsMargins(20, 20, 20, 20) # Отступы от краев панели

        # 2. Создаем кнопки
        self.btn_create = QPushButton("Создать")
        self.btn_delete = QPushButton("Удалить")
        self.btn_get = QPushButton("Получить")
        self.btn_update = QPushButton("Обновить")

        self.btn_create.clicked.connect(self.open_create_window)
        self.btn_get.clicked.connect(self.refresh_data)
        self.btn_update.clicked.connect(self.open_edit_window)
        self.btn_delete.clicked.connect(self.delete_contact)

        # 3. Добавляем кнопки в макет
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.btn_create)
        self.button_layout.addWidget(self.btn_delete)
        self.button_layout.addWidget(self.btn_get)
        self.button_layout.addWidget(self.btn_update)
        self.button_layout.addStretch()

        # 4. Добавляем этот макет в основной горизонтальный макет окна
        self.main_layout.addLayout(self.button_layout, stretch=0)

    def open_create_window(self):
        self.edit_window = CreateEditWindow(self.backend)
        self.edit_window.destroyed.connect(self.refresh_data)
        self.edit_window.show()
    
    def refresh_data(self):
        try:
            contacts = self.backend.get_contacts() 
            self.table.setRowCount(0)
            for row_number, contact in enumerate(contacts):
                self.table.insertRow(row_number)
                row_data = [
                    str(contact.get('id', '')),
                    "", # Заглушка под фото
                    contact.get('full_name', ''),
                    contact.get('phone_number', ''),
                    contact.get('email', ''),
                    contact.get('birth_date', ''),
                    contact.get('address', '')
                ]
                for column_number, text in enumerate(row_data):
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row_number, column_number, item)            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось загрузить данные: {e}")
    
    def delete_contact(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return
        
        contact_id = self.table.item(selected_row, 0).text() 
        confirm = QMessageBox.question(self, "Подтверждение", f"Удалить запись ID {contact_id}?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            if self.backend.delete_contact(contact_id):
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить запись")
    
    def open_edit_window(self):
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
            "address": self.table.item(selected_row, 6).text()
        }
        
        self.edit_window = CreateEditWindow(self.backend)
        self.edit_window.load_contact_data(contact_data)
        self.edit_window.destroyed.connect(self.refresh_data)
        self.edit_window.show()

class Controller:
    def __init__(self, backend):
        self.backend = backend
        self.login_window = LoginWindow()
        self.main_window = None
        self.login_window.button.clicked.connect(self.show_main_and_close_login)

    def show_main_and_close_login(self):
        self.main_window = MainWindow(self.backend)
        self.main_window.show()
        self.login_window.close()