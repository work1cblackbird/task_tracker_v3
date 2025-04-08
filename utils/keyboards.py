# -*- coding: utf-8 -*-
"""
Модуль для генерации клавиатур и кнопок
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from config import BotConfig, Roles, TaskStatuses

class Keyboards:
    """Класс для генерации всех клавиатур бота"""

    @staticmethod
    def get_main_menu_keyboard(username):
        """
        Главное меню (ReplyKeyboardMarkup)
        :param username: Telegram username пользователя
        :return: ReplyKeyboardMarkup
        """
        is_admin = username == BotConfig.ADMIN_USERNAME

        if is_admin:
            keyboard = [
                ["➕ Создать задачу", "📋 Все задачи"],
                ["👥 Управление пользователями"]
            ]
        else:
            keyboard = [
                ["➕ Создать задачу", "📋 Мои задачи"]
            ]

        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    @staticmethod
    def get_task_keyboard(task_status, current_user, task_id=None):
        """
        Клавиатура для управления задачей (InlineKeyboardMarkup)
        :param task_status: Текущий статус задачи
        :param current_user: Username текущего пользователя
        :param task_id: ID задачи (для callback_data)
        :return: InlineKeyboardMarkup
        """
        buttons = []
        callback_prefix = f"task_{task_id}_" if task_id else ""

        # Кнопки для всех пользователей
        buttons.append([
            InlineKeyboardButton(
                "✏️ Комментировать",
                callback_data=f"{callback_prefix}comment")
        ])

        # Кнопки только для админа
        if current_user == BotConfig.ADMIN_USERNAME:
            if task_status == TaskStatuses.NEW:
                buttons.append([
                    InlineKeyboardButton(
                        "🛠 Взять в работу",
                        callback_data=f"{callback_prefix}take")
                ])
            elif task_status == TaskStatuses.IN_PROGRESS:
                buttons.append([
                    InlineKeyboardButton(
                        "✅ Завершить",
                        callback_data=f"{callback_prefix}complete")
                ])
            elif task_status == TaskStatuses.DONE:
                buttons.append([
                    InlineKeyboardButton(
                        "🔄 Вернуть в работу",
                        callback_data=f"{callback_prefix}reopen")
                ])

            buttons.append([
                InlineKeyboardButton(
                    "🗑 Удалить",
                    callback_data=f"{callback_prefix}delete")
            ])

        buttons.append([Keyboards.get_back_button()])

        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def get_filters_keyboard(filter_type="status"):
        """
        Клавиатура фильтров (InlineKeyboardMarkup)
        :param filter_type: Тип фильтра (status/period)
        :return: InlineKeyboardMarkup
        """
        if filter_type == "status":
            buttons = [
                [
                    InlineKeyboardButton("🔘 Все", callback_data="filter_status_all"),
                    InlineKeyboardButton("⚪️ Новые", callback_data="filter_status_new"),
                    InlineKeyboardButton("⚪️ В работе", callback_data="filter_status_in_progress"),
                    InlineKeyboardButton("⚪️ Завершённые", callback_data="filter_status_done")
                ]
            ]
        else:  # period
            buttons = [
                [
                    InlineKeyboardButton("📅 Сегодня", callback_data="filter_period_today"),
                    InlineKeyboardButton("📅 Неделя", callback_data="filter_period_week"),
                    InlineKeyboardButton("📅 Месяц", callback_data="filter_period_month"),
                    InlineKeyboardButton("📅 Все", callback_data="filter_period_all")
                ],
                [
                    InlineKeyboardButton(
                        "📅 Произвольный период", 
                        callback_data="filter_custom_period")
                ]
            ]

        buttons.append([Keyboards.get_back_button()])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def get_user_management_keyboard(users):
        """
        Клавиатура для управления пользователями (InlineKeyboardMarkup)
        :param users: Список пользователей из БД
        :return: InlineKeyboardMarkup
        """
        buttons = []
        for user in users:
            if user[1] == BotConfig.ADMIN_USERNAME:
                continue

            role_icon = "👤" if user[2] == Roles.USER else "👔"
            buttons.append([
                InlineKeyboardButton(
                    f"{role_icon} @{user[1]}",
                    callback_data=f"user_detail_{user[1]}")
            ])

        buttons.append([Keyboards.get_back_button()])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def get_user_actions_keyboard(username, current_role):
        """
        Клавиатура действий с пользователем (InlineKeyboardMarkup)
        :param username: Username пользователя
        :param current_role: Текущая роль пользователя
        :return: InlineKeyboardMarkup
        """
        buttons = []
        
        if current_role == Roles.USER:
            buttons.append([
                InlineKeyboardButton(
                    "👔 Назначить руководителем",
                    callback_data=f"promote_{username}")
            ])
        else:
            buttons.append([
                InlineKeyboardButton(
                    "👤 Понизить до пользователя",
                    callback_data=f"demote_{username}")
            ])

        buttons.append([
            InlineKeyboardButton(
                "🗑 Удалить пользователя",
                callback_data=f"delete_user_{username}")
        ])

        buttons.append([Keyboards.get_back_button()])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def get_back_button():
        """Кнопка 'Назад' для всех клавиатур"""
        return InlineKeyboardButton("🔙 Назад", callback_data="back")

    @staticmethod
    def get_confirmation_keyboard(action):
        """
        Клавиатура подтверждения действия
        :param action: Действие для подтверждения
        :return: InlineKeyboardMarkup
        """
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_{action}"),
                InlineKeyboardButton("❌ Отменить", callback_data="cancel_action")
            ]
        ])