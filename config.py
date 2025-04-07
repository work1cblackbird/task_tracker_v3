class Config:
    # Telegram Bot Token (получить у @BotFather)
    BOT_TOKEN = "7631959629:AAFx_lCo0k5L6uyi1d0FykaJZBZOl9_SROI"

    # Админ бота (ваш Telegram username без @)
    ADMIN_USERNAME = "NN_Danila_Belov"

    # Пути к файлам
    DATABASE_PATH = "database.db"
    LOG_FILE = "bot.log"

    # Роли пользователей
    class Roles:
        USER = "user"
        MANAGER = "manager"
        ADMIN = "admin"

    # Статусы задач
    class TaskStatus:
        NEW = "new"
        IN_PROGRESS = "in_progress"
        DONE = "done"

    # Настройки пагинации
    class Pagination:
        ITEMS_PER_PAGE = 5
        MAX_PAGES_TO_SHOW = 5

    # Настройки фильтров
    class Filters:
        DATE_FORMAT = "%d.%m.%Y"
        DEFAULT_PERIOD_DAYS = 30

    # Текстовые константы
    class Text:
        TASK_CREATED = "✅ Задача создана (ID: {task_id})"
        NO_TASKS = "Задачи не найдены"
        ACCESS_DENIED = "⛔ Доступ запрещен"


class Handlers:
    """Имена обработчиков для регистрации в приложении"""
    
    # Основные команды
    START = "start"
    HELP = "help"
    CANCEL = "cancel"

    # Задачи
    TASK_CREATE = "task_create"
    TASK_LIST = "task_list"
    TASK_DETAIL = "task_detail"
    TASK_UPDATE = "task_update"
    TASK_DELETE = "task_delete"

    # Комментарии
    COMMENT_ADD = "comment_add"
    COMMENT_LIST = "comment_list"

    # Администрирование
    USER_LIST = "user_list"
    USER_ROLE_UPDATE = "user_role_update"
    USER_DELETE = "user_delete"


class Keyboards:
    """Типы клавиатур для генерации"""
    
    MAIN_MENU = "main_menu"
    TASK_ACTIONS = "task_actions"
    FILTERS = "filters"
    DATE_PICKER = "date_picker"
    CONFIRM = "confirm"


class CallbackData:
    """Префиксы callback-данных"""
    
    TASK_PREFIX = "task_"
    COMMENT_PREFIX = "comment_"
    USER_PREFIX = "user_"
    PAGE_PREFIX = "page_"
    FILTER_PREFIX = "filter_"
    DATE_PREFIX = "date_"