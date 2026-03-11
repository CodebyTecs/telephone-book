CREATE TABLE IF NOT EXISTS contacts (
    id BIGSERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    birth_date DATE,
    phone_number VARCHAR(32) NOT NULL,
    email VARCHAR(255) UNIQUE,
    address TEXT,
    photo BYTEA,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_contacts_full_name ON contacts(full_name);

INSERT INTO contacts (full_name, birth_date, phone_number, email, address, photo) VALUES
('Иванов Иван Иванович', '1990-05-15', '+7 (999) 123-45-67', 'ivanov.ivan@example.com', 'г. Москва, ул. Ленина, д. 10, кв. 45', NULL),
('Петрова Анна Сергеевна', '1985-08-22', '+7 (999) 234-56-78', 'petrova.anna@example.com', 'г. Санкт-Петербург, Невский пр., д. 25, кв. 12', NULL),
('Сидоров Петр Петрович', '1978-03-10', '+7 (999) 345-67-89', 'sidorov.petr@example.com', 'г. Новосибирск, ул. Советская, д. 5', NULL),
('Козлова Елена Дмитриевна', '1995-12-03', '+7 (999) 456-78-90', 'kozlova.elena@example.com', 'г. Екатеринбург, ул. Малышева, д. 30, кв. 8', NULL),
('Морозов Алексей Викторович', '1982-07-19', '+7 (999) 567-89-01', 'morozov.alex@example.com', 'г. Казань, ул. Баумана, д. 15', NULL),
('Волкова Татьяна Андреевна', '1991-04-27', '+7 (999) 678-90-12', 'volkova.tatiana@example.com', 'г. Нижний Новгород, ул. Большая Покровская, д. 42', NULL),
('Соколов Дмитрий Сергеевич', '1988-09-14', '+7 (999) 789-01-23', 'sokolov.dmitry@example.com', 'г. Челябинск, ул. Кирова, д. 56', NULL),
('Михайлова Ольга Игоревна', '1993-11-30', '+7 (999) 890-12-34', 'mikhailova.olga@example.com', 'г. Омск, ул. Ленина, д. 100, кв. 23', NULL),
('Новиков Павел Александрович', '1980-06-05', '+7 (999) 901-23-45', 'novikov.pavel@example.com', 'г. Самара, ул. Куйбышева, д. 75', NULL),
('Федорова Наталья Владимировна', '1987-02-18', '+7 (999) 012-34-56', 'fedorova.natalia@example.com', 'г. Ростов-на-Дону, ул. Большая Садовая, д. 33', NULL);
