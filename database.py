import sqlite3
from datetime import datetime
from config import Config

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DATABASE_PATH)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        """Создает таблицы, если они не существуют."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL DEFAULT 'user'
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                created_by TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(username)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        self.conn.commit()

    def add_user(self, username: str, role: str = 'user'):
        """Добавляет пользователя в БД."""
        self.cursor.execute(
            "INSERT INTO users (username, role) VALUES (?, ?)",
            (username, role)
        )
        self.conn.commit()

    def get_user(self, username: str):
        """Возвращает данные пользователя."""
        self.cursor.execute(
            "SELECT * FROM users WHERE username = ?", 
            (username,)
        )
        return self.cursor.fetchone()

    def add_task(self, description: str, created_by: str):
        """Создает новую задачу."""
        self.cursor.execute(
            """
            INSERT INTO tasks (description, created_by) 
            VALUES (?, ?)
            """,
            (description, created_by)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_task(self, task_id: int):
        """Возвращает задачу по ID."""
        self.cursor.execute(
            "SELECT * FROM tasks WHERE id = ?", 
            (task_id,)
        )
        return self.cursor.fetchone()

    def get_user_tasks(self, username: str, status: str = None):
        """Возвращает задачи пользователя с фильтром по статусу."""
        query = "SELECT * FROM tasks WHERE created_by = ?"
        params = [username]
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_all_tasks(self, status: str = None):
        """Возвращает все задачи с фильтром по статусу."""
        query = "SELECT * FROM tasks"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def update_task_status(self, task_id: int, status: str):
        """Изменяет статус задачи."""
        self.cursor.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id)
        )
        self.conn.commit()

    def delete_task(self, task_id: int):
        """Удаляет задачу."""
        self.cursor.execute(
            "DELETE FROM tasks WHERE id = ?", 
            (task_id,)
        )
        self.conn.commit()

    def add_comment(self, task_id: int, username: str, text: str):
        """Добавляет комментарий к задаче."""
        self.cursor.execute(
            """
            INSERT INTO comments (task_id, username, text) 
            VALUES (?, ?, ?)
            """,
            (task_id, username, text)
        )
        self.conn.commit()

    def get_task_comments(self, task_id: int):
        """Возвращает комментарии задачи."""
        self.cursor.execute(
            "SELECT * FROM comments WHERE task_id = ? ORDER BY created_at DESC",
            (task_id,)
        )
        return self.cursor.fetchall()

    def close(self):
        """Закрывает соединение с БД."""
        self.conn.close()

# Инициализация БД при импорте
db = Database()