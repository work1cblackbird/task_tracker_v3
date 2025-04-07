from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from config import Config

class Keyboards:
    @staticmethod
    def get_main_menu(role):
        """
        Главное меню в зависимости от роли
        Возвращает ReplyKeyboardMarkup
        """
        if role == Config.ROLES["ADMIN"]:
            keyboard = [
                ["➕ Создать задачу", "📋 Все задачи"],
                ["👥 Управление пользователями"]
            ]
        elif role == Config.ROLES["MANAGER"]:
            keyboard = [
                ["➕ Создать задачу", "📋 Все задачи"]
            ]
        else:  # USER
            keyboard = [
                ["➕ Создать задачу", "📋 Мои задачи"]
            ]
        
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def get_task_actions(task_status, is_admin):
        """
        Кнопки действий с задачей
        Возвращает InlineKeyboardMarkup
        """
        buttons = []
        
        # Общие кнопки для всех ролей
        buttons.append([InlineKeyboardButton("✏️ Комментировать", callback_data="comment_task")])
        
        # Кнопки только для админа
        if is_admin:
            if task_status == "new":
                buttons.append([InlineKeyboardButton("🛠 Взять в работу", callback_data="take_task")])
            elif task_status == "in_progress":
                buttons.append([InlineKeyboardButton("✅ Завершить", callback_data="complete_task")])
            elif task_status == "done":
                buttons.append([InlineKeyboardButton("🔄 Вернуть в работу", callback_data="reopen_task")])
            
            buttons.append([InlineKeyboardButton("🗑 Удалить", callback_data="delete_task")])
        
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def get_filters_menu():
        """
        Меню фильтров для списка задач
        Возвращает InlineKeyboardMarkup
        """
        buttons = [
            [
                InlineKeyboardButton("🔘 Все", callback_data="filter_all"),
                InlineKeyboardButton("⚪️ Новые", callback_data="filter_new"),
                InlineKeyboardButton("⚪️ В работе", callback_data="filter_in_progress"),
                InlineKeyboardButton("⚪️ Завершённые", callback_data="filter_done")
            ],
            [
                InlineKeyboardButton("📅 Сегодня", callback_data="filter_today"),
                InlineKeyboardButton("📅 Неделя", callback_data="filter_week"),
                InlineKeyboardButton("📅 Месяц", callback_data="filter_month"),
                InlineKeyboardButton("📅 Произвольный", callback_data="filter_custom")
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def get_pagination(current_page, total_pages):
        """
        Кнопки пагинации
        Возвращает InlineKeyboardMarkup
        """
        buttons = []
        if total_pages > 1:
            buttons.append([
                InlineKeyboardButton("⬅️", callback_data=f"prev_{current_page}"),
                InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="ignore"),
                InlineKeyboardButton("➡️", callback_data=f"next_{current_page}")
            ])
        return InlineKeyboardMarkup(buttons) if buttons else None

    @staticmethod
    def get_user_management_buttons(user_role):
        """
        Кнопки управления пользователями (для админа)
        Возвращает InlineKeyboardMarkup
        """
        buttons = []
        if user_role == Config.ROLES["USER"]:
            buttons.append([InlineKeyboardButton("👔 Назначить руководителем", callback_data="promote_user")])
        elif user_role == Config.ROLES["MANAGER"]:
            buttons.append([InlineKeyboardButton("👤 Понизить до пользователя", callback_data="demote_user")])
        
        buttons.append([InlineKeyboardButton("🗑 Удалить", callback_data="delete_user")])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def get_confirmation_buttons():
        """
        Кнопки подтверждения действий
        Возвращает InlineKeyboardMarkup
        """
        buttons = [
            [
                InlineKeyboardButton("✅ Да", callback_data="confirm_yes"),
                InlineKeyboardButton("❌ Нет", callback_data="confirm_no")
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def get_back_button():
        """
        Кнопка "Назад"
        Возвращает InlineKeyboardMarkup
        """
        return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="go_back")]])