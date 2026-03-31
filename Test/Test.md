# Отчет о тестировании  31.03.2026

## 1. Чек-лист

| № | Проверка | Комментарий |
|---|----------|-------------|
| 1 | Пустое ФИО | Проверка пройдена, однако в backend.py, поле full_name получает пустую строку, а в БД NOT NULL пропускает пустую строку, записывая её. Рекомендация - добавить проверку на размер >0
| 2 | Пустой телефон | Проверка пройдена, однако в backend.py, поле аналогичным образом получает пустую строку
| 3 | Некорректный email | Проверка пройдена, валидация работает корректно
| 4 | Некорректная дата | Проверка пройдена, валидация реализована в GUI
| 5 | Дубликат телефона | Проверка пройдена, дубликат отклоняется, т.к. в БД поле phone_number имеет ограничение UNIQUE NOT NULL. Возвращает ошибку, которую обрабатывает backend.py
| 6 | SQL инъекция | Проверка пройдена, иньекция не прошла, т.к. используются запросы %s, которые передают данные отдельно от SQL- кода
| 7 | Очень длинная строка | Проверка пройдена, длинная строка отклоняется, т.к. в БД поля имеют ограничения, возвращая ошибку, которая перехватывается 
| 8 | Обновление с нечисловым ID | Не пройден, при передаче неправильного ID возникает ValueError. Однако это не влияет на пользователя. В GUI нет возможности самостоятельного добавления ID
| 9 | Удаление с нечисловым ID | Не пройден, аналогично, пользователю данная опция недоступна
| 10 | Несуществующий ID (update) | Пройден
| 11 | Несуществующий ID (delete) | Пройден

![img](https://github.com/Darkness1853/Pictures/blob/main/TEST/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-04-01%20043244.png?raw=true)

---

## Работа с CLI

Список команд

![img](https://github.com/Darkness1853/Pictures/blob/main/TEST/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-03-31%20105306.png?raw=true)
---
1. Создание контакта

![img1](https://github.com/Darkness1853/Pictures/blob/main/TEST/image%20(10).jpg?raw=true)

в CLI программа позволяет ввести неверную дату 

2. Сортировка по ФИО

![img3](https://github.com/Darkness1853/Pictures/blob/main/TEST/image.png?raw=true)

3. Бинарный поиск

![img4](https://github.com/Darkness1853/Pictures/blob/main/TEST/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-03-31%20153053.png?raw=true)

4. Поиск в ДОП

![img5](https://github.com/Darkness1853/Pictures/blob/main/TEST/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-03-31%20153215.png?raw=true)

5. ДОП порядок обхода

![img6](https://github.com/Darkness1853/Pictures/blob/main/TEST/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-03-31%20153414.png?raw=true)

6. Обновление контакта

![img7](https://github.com/Darkness1853/Pictures/blob/main/TEST/image%20(12).jpg?raw=true)

7. Удаление контакта

![img8](https://github.com/Darkness1853/Pictures/blob/main/TEST/image%20(13).jpg?raw=true)

8. Добавление фото к контакту

![img9](https://github.com/Darkness1853/Pictures/blob/main/TEST/image%20(14).jpg?raw=true)

9. Удаление фото

![img10](https://github.com/Darkness1853/Pictures/blob/main/TEST/image%20(15).jpg?raw=true)

--- 

## 2. Результаты тестирования программой

![img](https://github.com/Darkness1853/Pictures/blob/main/TEST/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-04-01%20042130.png?raw=true)

# Критические проблемы
Не обнаружены

# Не критичные проблемы

При тестировании поля ввода даты обнаружено, что бэкенд/логика приложения принимает даты, превышающие текущую дату

![img2](https://github.com/Darkness1853/Pictures/blob/main/TEST/image%20(11).jpg?raw=true)

Однако проблема не является критичным, так как:
Валидация корректно реализована на уровне графического интерфейса (GUI)