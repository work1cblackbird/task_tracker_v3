# -*- coding: utf-8 -*-
"""
Модуль обработки операций с задачами
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from config import BotConfig, TaskStatuses
from database import db
from utils.keyboards import (
    get_main_menu_keyboard,
    get_task_keyboard,
    get_back_button,
    get_filters_keyboard,
)

# Настройка логгирования
logger = logging.getLogger(__name__)

class TaskHandlers:
    """Класс для обработки операций с задачами"""

    def __init__(self, application):
        self.application = application
        self._register_handlers()

    def _register_handlers(self):
        """Регистрация обработчиков задач"""
        handlers = [
            CommandHandler("tasks", self.list_tasks_handler),
            CallbackQueryHandler(self.create_task_handler, pattern="^create_task$"),
            CallbackQueryHandler(self.task_detail_handler, pattern="^task_"),
            CallbackQueryHandler(self.change_status_handler, pattern="^(take|complete|reopen)_"),
            CallbackQueryHandler(self.delete_task_handler, pattern="^delete_"),
            CallbackQueryHandler(self.filter_tasks_handler, pattern="^filter_"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.save_task_handler),
        ]
        for handler in handlers:
            self.application.add_handler(handler)

    async def list_tasks_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список задач"""
        user = update.effective_user
        is_admin = user.username == BotConfig.ADMIN_USERNAME
        
        if is_admin:
            tasks = db.get_all_tasks()
        else:
            tasks = db.get_user_tasks(user.username)

        if not tasks:
            await update.message.reply_text("Задачи не найдены")
            return

        keyboard = []
        for task in tasks:
            keyboard.append([
                InlineKeyboardButton(
                    f"#{task[0]} {task[1][:30]}... ({TaskStatuses.get_status_name(task[2])})",
                    callback_data=f"task_{task[0]}"
                )
            ])

        keyboard.append([
            InlineKeyboardButton("➕ Создать задачу", callback_data="create_task"),
            InlineKeyboardButton("🔍 Фильтры", callback_data="filter_status")
        ])

        await update.message.reply_text(
            "Список задач:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def create_task_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало создания задачи"""
        context.user_data["awaiting_task"] = True
        await update.callback_query.message.reply_text(
            "Введите описание задачи:",
            reply_markup=InlineKeyboardMarkup([[get_back_button()]])
        )

    async def save_task_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сохранение новой задачи"""
        if "awaiting_task" not in context.user_data:
            return

        description = update.message.text
        user = update.effective_user
        task_id = db.add_task(description, user.username)

        context.user_data.pop("awaiting_task", None)
        await update.message.reply_text(
            f"Задача #{task_id} создана!",
            reply_markup=get_main_menu_keyboard(user.username)
        )

    async def task_detail_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр деталей задачи"""
        task_id = int(update.callback_query.data.split("_")[1])
        task = db.get_task(task_id)

        if not task:
            await update.callback_query.answer("Задача не найдена")
            return

        comments = db.get_task_comments(task_id)
        comments_text = "\n".join(
            [f"{i+1}. @{c[1]}: {c[2]}" for i, c in enumerate(comments)]
        ) if comments else "Комментарии отсутствуют"

        text = (
            f"Задача #{task[0]}\n"
            f"Описание: {task[1]}\n"
            f"Статус: {TaskStatuses.get_status_name(task[2])}\n"
            f"Автор: @{task[3]}\n"
            f"Дата: {task[4]}\n\n"
            f"Комментарии:\n{comments_text}"
        )

        keyboard = get_task_keyboard(task[2], update.effective_user.username, task_id)
        await update.callback_query.message.edit_text(
            text,
            reply_markup=keyboard
        )

    async def change_status_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Изменение статуса задачи"""
        action, task_id = update.callback_query.data.split("_")
        task_id = int(task_id)
        user = update.effective_user

        if action == "take":
            new_status = TaskStatuses.IN_PROGRESS
        elif action == "complete":
            new_status = TaskStatuses.DONE
        else:  # reopen
            new_status = TaskStatuses.IN_PROGRESS

        db.update_task_status(task_id, new_status)
        await update.callback_query.answer(f"Статус обновлен: {TaskStatuses.get_status_name(new_status)}")
        await self.task_detail_handler(update, context)

    async def delete_task_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Удаление задачи"""
        task_id = int(update.callback_query.data.split("_")[1])
        db.delete_task(task_id)
        await update.callback_query.answer("Задача удалена", show_alert=True)
        await update.callback_query.message.delete()

    async def filter_tasks_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Фильтрация задач"""
        filter_type = update.callback_query.data.split("_")[1]
        keyboard = get_filters_keyboard(filter_type)
        await update.callback_query.message.edit_reply_markup(reply_markup=keyboard)

def register_task_handlers(application):
    """Функция для регистрации обработчиков задач"""
    TaskHandlers(application)