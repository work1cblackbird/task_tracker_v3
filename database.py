# -*- coding: utf-8 -*-
"""
Модуль для работы с базой данных SQLite
Соответствует концепции Task Tracker Bot
"""

import sqlite3
from datetime import datetime
from config import DatabaseConfig, Roles, TaskStatuses, BotConfig

class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self):
        """Инициализация соединения с БД"""
        self.connection = sqlite3.connect(DatabaseConfig.DB_FILENAME)
        self.cursor = self.connection.cursor()
        self._create_tables()
    
    def _create_tables(self):
        # Создаем таблицу users без параметра для DEFAULT
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица tasks
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(username)
            )
        """)
        
        # Таблица comments
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        self.connection.commit()
    
    # ========== Users ==========
    def add_user(self, username: str, role: str = Roles.DEFAULT_ROLE):
        """Добавление нового пользователя"""
        try:
            self.cursor.execute(
                "INSERT INTO users (username, role) VALUES (?, ?)",
                (username, role)
            )
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, username: str):
        """Получение данных пользователя"""
        self.cursor.execute(
            "SELECT username, role FROM users WHERE username = ?",
            (username,)
        )
        return self.cursor.fetchone()
    
    def update_user_role(self, username: str, new_role: str):
        """Изменение роли пользователя"""
        self.cursor.execute(
            "UPDATE users SET role = ? WHERE username = ?",
            (new_role, username)
        )
        return self.connection.commit()
    
    # ========== Tasks ==========
    def add_task(self, description: str, created_by: str):
        """Добавление новой задачи"""
        self.cursor.execute(
            "INSERT INTO tasks (description, created_by) VALUES (?, ?)",
            (description, created_by)
        )
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_task(self, task_id: int):
        """Получение данных задачи"""
        self.cursor.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        )
        return self.cursor.fetchone()
    
    def update_task_status(self, task_id: int, new_status: str):
        """Обновление статуса задачи"""
        self.cursor.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (new_status, task_id)
        )
        return self.connection.commit()
    
    def delete_task(self, task_id: int):
        """Удаление задачи"""
        self.cursor.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )
        return self.connection.commit()
    
    # ========== Comments ==========
    def add_comment(self, task_id: int, username: str, text: str):
        """Добавление комментария к задаче"""
        self.cursor.execute(
            """INSERT INTO comments (task_id, username, text) 
            VALUES (?, ?, ?)""",
            (task_id, username, text)
        )
        return self.connection.commit()
    
    def get_task_comments(self, task_id: int):
        """Получение комментариев задачи"""
        self.cursor.execute(
            """SELECT username, text, created_at 
            FROM comments WHERE task_id = ? 
            ORDER BY created_at""",
            (task_id,)
        )
        return self.cursor.fetchall()
    
    # ========== Utility Methods ==========
    def close(self):
        """Закрытие соединения с БД"""
        self.connection.close()
    
    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие соединения"""
        self.close()

# Инициализация глобального подключения
db = Database()

def init_database():
    """Инициализация базы данных при старте"""
    # Добавляем администратора, если его нет
    admin_username = BotConfig.ADMIN_USERNAME
    if not db.get_user(admin_username):
        db.add_user(admin_username, Roles.ADMIN)