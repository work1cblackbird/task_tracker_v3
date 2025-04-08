# -*- coding: utf-8 -*-
"""
Модуль обработки пользовательских операций
Регистрация, управление ролями, профиль
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from config import BotConfig, Roles
from database import db
from utils.keyboards import get_back_button, get_main_menu_keyboard

# Настройка логгирования
logger = logging.getLogger(__name__)

class UserHandlers:
    """Класс для обработки пользовательских операций"""

    def __init__(self, application):
        self.application = application
        self._register_handlers()

    def _register_handlers(self):
        """Регистрация обработчиков пользователей"""
        handlers = [
            CommandHandler("profile", self.profile_handler),
            CallbackQueryHandler(self.manage_users_handler, pattern="^manage_users$"),
            CallbackQueryHandler(self.change_role_handler, pattern="^change_role_"),
        ]
        for handler in handlers:
            self.application.add_handler(handler)

    async def profile_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать профиль пользователя"""
        user = update.effective_user
        user_data = db.get_user(user.username)

        if not user_data:
            db.add_user(user.username)
            user_data = (user.username, Roles.DEFAULT_ROLE)

        role_name = "👤 Пользователь" if user_data[1] == Roles.USER else \
                   "👔 Руководитель" if user_data[1] == Roles.MANAGER else \
                   "👑 Администратор"

        text = (
            f"📌 Ваш профиль:\n"
            f"Имя: {user.full_name}\n"
            f"Username: @{user.username}\n"
            f"Роль: {role_name}"
        )

        keyboard = []
        if user.username == BotConfig.ADMIN_USERNAME:
            keyboard.append([InlineKeyboardButton(
                "Управление пользователями", 
                callback_data="manage_users"
            )])

        keyboard.append([get_back_button()])

        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def manage_users_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список пользователей для управления"""
        if update.effective_user.username != BotConfig.ADMIN_USERNAME:
            await update.callback_query.answer("Эта команда только для администратора!", show_alert=True)
            return

        users = db.get_all_users()
        keyboard = []

        for user in users:
            if user[1] == BotConfig.ADMIN_USERNAME:
                continue

            role_icon = "👤" if user[2] == Roles.USER else "👔"
            keyboard.append([
                InlineKeyboardButton(
                    f"{role_icon} @{user[1]} ({user[2]})",
                    callback_data=f"user_detail_{user[1]}"
                )
            ])

        keyboard.append([get_back_button()])

        await update.callback_query.message.edit_text(
            "Список пользователей:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def change_role_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Изменение роли пользователя"""
        if update.effective_user.username != BotConfig.ADMIN_USERNAME:
            await update.callback_query.answer("Эта команда только для администратора!", show_alert=True)
            return

        data = update.callback_query.data.split("_")
        username = data[2]
        new_role = data[3]

        if username == BotConfig.ADMIN_USERNAME:
            await update.callback_query.answer("Нельзя изменить роль администратора!", show_alert=True)
            return

        db.update_user_role(username, new_role)
        await update.callback_query.answer(f"Роль пользователя @{username} изменена")
        await self.manage_users_handler(update, context)

def register_user_handlers(application):
    """Функция для регистрации обработчиков пользователей"""
    UserHandlers(application)