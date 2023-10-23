import sqlite3

connection = sqlite3.connect('users.db')
cursor = connection.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        chat_id INTEGER
    )
""")

connection.commit()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY,
        user_id INTEGER REFERENCES users (id) ON DELETE CASCADE,
        operation BOOLEAN NOT NULL,
        value DECIMAL NOT NULL,
        date DATETIME NOT NULL
                    DEFAULT (DATETIME('now'))
    )
""")
connection.commit()

class DatBase:
    def __init__(self):
        """Подключение к БД"""
        self.connection = sqlite3.connect('users.db')
        self.cursor = self.connection.cursor()

    def add_user(self, user_id, username, first_name, last_name, chat_id):
        """Добавление пользователя в БД"""
        with self.connection:
            self.cursor.execute("""
                    INSERT INTO users (user_id, username, first_name, last_name, chat_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, username, first_name, last_name, chat_id))
            self.connection.commit()

    def send_info(self, chat_id):
        """Отправляем пользователю информацию о нем"""
        with self.connection:
            self.cursor.execute("""
                    SELECT * FROM users WHERE chat_id=?
                """, (chat_id,))
            self.connection.commit()
            return self.cursor.fetchone()

    def remove_user(self, chat_id):
        """Удаляем пользователя из БД"""
        with self.connection:
            self.cursor.execute("""
                    DELETE FROM users WHERE chat_id=?
                """, (chat_id,))
            self.connection.commit()

    def get_user_id(self, user_id):
        """Достаем id пользователя в БД по его user_id"""
        result = self.cursor.execute("""
            SELECT `id` FROM `users` WHERE `user_id` = ?
            """, (user_id,))
        return result.fetchone()[0]

    def add_record(self, user_id, operation, value):
        """Создаем запись о доходах/расходах"""
        self.cursor.execute("""
            INSERT INTO `records` (`user_id`, `operation`, `value`) VALUES (?, ?, ?)
            """, (self.get_user_id(user_id), operation == "+", value))
        return self.connection.commit()

    def get_records(self, user_id, within="all"):
        """Получаем историю о доходах/расходах"""

        if within == "day":
            result = self.cursor.execute("""
                SELECT * FROM `records` WHERE `user_id` = ? AND `date` BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime') ORDER BY `date`
                """, (self.get_user_id(user_id),))
        elif within == "week":
            result = self.cursor.execute("""
                SELECT * FROM `records` WHERE `user_id` = ? AND `date` BETWEEN datetime('now', '-6 days') AND datetime('now', 'localtime') ORDER BY `date`
                """, (self.get_user_id(user_id),))
        elif within == "month":
            result = self.cursor.execute("""
                SELECT * FROM `records` WHERE `user_id` = ? AND `date` BETWEEN datetime('now', 'start of month') AND datetime('now', 'localtime') ORDER BY `date`
                """, (self.get_user_id(user_id),))
        else:
            result = self.cursor.execute("""
                SELECT * FROM `records` WHERE `user_id` = ? ORDER BY `date`
                """, (self.get_user_id(user_id),))

        return result.fetchall()

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()