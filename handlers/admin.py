# -*- coding: utf-8 -*-
"""
Модуль обработки административных команд
Только для пользователей с ролью ADMIN
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from config import BotConfig, Roles
from database import db
from utils.keyboards import get_back_button

# Настройка логгирования
logger = logging.getLogger(__name__)

class AdminHandlers:
    """Класс для обработки административных команд"""

    def __init__(self, application):
        self.application = application
        self._register_handlers()

    def _register_handlers(self):
        """Регистрация обработчиков административных команд"""
        handlers = [
            CallbackQueryHandler(self.promote_user_handler, pattern="^promote_"),
            CallbackQueryHandler(self.demote_user_handler, pattern="^demote_"),
            CallbackQueryHandler(self.delete_user_handler, pattern="^delete_user_"),
            CallbackQueryHandler(self.admin_tasks_handler, pattern="^admin_tasks$"),
        ]
        for handler in handlers:
            self.application.add_handler(handler)

    async def _check_admin(self, update: Update) -> bool:
        """Проверка прав администратора"""
        user = update.effective_user
        if user.username != BotConfig.ADMIN_USERNAME:
            await update.callback_query.answer("Эта команда только для администратора!", show_alert=True)
            return False
        return True

    async def promote_user_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Повышение пользователя до руководителя"""
        if not await self._check_admin(update):
            return

        username = update.callback_query.data.split("_")[1]
        db.update_user_role(username, Roles.MANAGER)
        
        await update.callback_query.answer(f"Пользователь @{username} теперь руководитель")
        await self._show_user_management(update)

    async def demote_user_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Понижение руководителя до пользователя"""
        if not await self._check_admin(update):
            return

        username = update.callback_query.data.split("_")[1]
        db.update_user_role(username, Roles.USER)
        
        await update.callback_query.answer(f"Пользователь @{username} теперь обычный пользователь")
        await self._show_user_management(update)

    async def delete_user_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Удаление пользователя"""
        if not await self._check_admin(update):
            return

        username = update.callback_query.data.split("_")[2]
        if username == BotConfig.ADMIN_USERNAME:
            await update.callback_query.answer("Нельзя удалить администратора!", show_alert=True)
            return

        # Здесь должна быть логика удаления пользователя и связанных задач
        await update.callback_query.answer(f"Пользователь @{username} удалён")
        await self._show_user_management(update)

    async def admin_tasks_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать административные задачи"""
        if not await self._check_admin(update):
            return

        keyboard = [
            [InlineKeyboardButton("Управление пользователями", callback_data="manage_users")],
            [InlineKeyboardButton("Просмотр всех задач", callback_data="view_all_tasks")],
            get_back_button()
        ]
        
        await update.callback_query.edit_message_text(
            "Административное меню:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def _show_user_management(self, update: Update):
        """Отображение списка пользователей для управления"""
        users = db.get_all_users()
        keyboard = []
        
        for user in users:
            if user[1] == BotConfig.ADMIN_USERNAME:
                continue
                
            role = "👤" if user[2] == Roles.USER else "👔"
            buttons = []
            
            if user[2] == Roles.USER:
                buttons.append(InlineKeyboardButton(
                    f"{role} Повысить до руководителя", 
                    callback_data=f"promote_{user[1]}"))
            else:
                buttons.append(InlineKeyboardButton(
                    f"{role} Понизить до пользователя", 
                    callback_data=f"demote_{user[1]}"))
                
            buttons.append(InlineKeyboardButton(
                "❌ Удалить", 
                callback_data=f"delete_user_{user[1]}"))
                
            keyboard.append(buttons)
        
        keyboard.append([get_back_button()])
        
        await update.callback_query.edit_message_text(
            "Управление пользователями:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def register_admin_handlers(application):
    """Функция для регистрации административных обработчиков"""
    AdminHandlers(application)