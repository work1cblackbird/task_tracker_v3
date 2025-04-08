# -*- coding: utf-8 -*-
"""
Конфигурационный файл бота Task Tracker
Все константы собраны в одном месте без использования .env
"""

class BotConfig:
    """Настройки бота и администратора"""
    # Токен бота (получить у @BotFather)
    BOT_TOKEN = "7631959629:AAFx_lCo0k5L6uyi1d0FykaJZBZOl9_SROI"
    
    # Username администратора (без @)
    ADMIN_USERNAME = "NN_Danila_Belov"
    
    # ID чата для логов (опционально)
    LOG_CHAT_ID = None

class Roles:
    """Система ролей пользователей"""
    USER = "Пользователь"
    MANAGER = "Руководитель"
    ADMIN = "Админ"
    
    # Доступные роли для назначения
    ALLOWED_ROLES = [USER, MANAGER, ADMIN]
    
    # Роли по умолчанию для новых пользователей
    DEFAULT_ROLE = USER

class TaskStatuses:
    """Статусы задач"""
    NEW = "Новая"
    IN_PROGRESS = "В работе"
    DONE = "Выполнена"
    
    # Доступные статусы
    ALL_STATUSES = [NEW, IN_PROGRESS, DONE]
    
    # Статус по умолчанию для новых задач
    DEFAULT_STATUS = NEW

class DatabaseConfig:
    """Настройки базы данных"""
    # Имя файла базы данных
    DB_FILENAME = "task_tracker.db"
    
    # Максимальное количество соединений
    POOL_SIZE = 5

class Pagination:
    """Настройки пагинации"""
    # Количество задач на одной странице
    TASKS_PER_PAGE = 5
    
    # Максимальное количество кнопок пагинации
    MAX_PAGE_BUTTONS = 5

class CalendarConfig:
    """Настройки календаря"""
    # Формат отображения даты
    DATE_FORMAT = "%d.%m.%Y"
    
    # Доступные периоды для быстрого выбора
    QUICK_PERIODS = {
        "today": "Сегодня",
        "week": "Неделя",
        "month": "Месяц",
        "all": "Все"
    }

class MessageTemplates:
    """Шаблоны сообщений"""
    TASK_CARD = """
Задача #{id}
——————————
Описание: {description}
Статус: {status}
Автор: @{author}
Дата: {date}
——————————
Комментарии ({comment_count}):
{comments}
——————————
{buttons}
"""
    USER_CARD = """
Пользователь: @{username}
Роль: {role}
——————————
{buttons}
"""

# Проверка обязательных конфигов
assert BotConfig.BOT_TOKEN != "ВАШ_ТОКЕН_БОТА", "Замените BOT_TOKEN на реальный токен бота"
assert BotConfig.ADMIN_USERNAME, "Укажите ADMIN_USERNAME"