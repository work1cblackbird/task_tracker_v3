# -*- coding: utf-8 -*-
"""
Модуль обработки комментариев к задачам
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from config import BotConfig
from database import db
from utils.keyboards import get_back_button

# Настройка логгирования
logger = logging.getLogger(__name__)

class CommentHandlers:
    """Класс для обработки операций с комментариями"""

    def __init__(self, application):
        self.application = application
        self._register_handlers()

    def _register_handlers(self):
        """Регистрация обработчиков комментариев"""
        handlers = [
            CallbackQueryHandler(self.add_comment_handler, pattern="^comment_"),
            CallbackQueryHandler(self.view_comments_handler, pattern="^view_comments_"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.save_comment_handler),
        ]
        for handler in handlers:
            self.application.add_handler(handler)

    async def add_comment_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик начала добавления комментария"""
        task_id = int(update.callback_query.data.split("_")[1])
        context.user_data["current_task"] = task_id
        context.user_data["awaiting_comment"] = True

        await update.callback_query.message.reply_text(
            "Введите ваш комментарий:",
            reply_markup=InlineKeyboardMarkup([[get_back_button()]])
        )

    async def save_comment_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сохранение комментария в БД"""
        if "awaiting_comment" not in context.user_data:
            return

        task_id = context.user_data["current_task"]
        username = update.effective_user.username
        comment_text = update.message.text

        db.add_comment(task_id, username, comment_text)

        # Очищаем состояние
        context.user_data.pop("awaiting_comment", None)
        context.user_data.pop("current_task", None)

        await update.message.reply_text(
            "Комментарий добавлен!",
            reply_markup=InlineKeyboardMarkup([[get_back_button()]])
        )

    async def view_comments_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просмотр всех комментариев к задаче"""
        task_id = int(update.callback_query.data.split("_")[2])
        comments = db.get_task_comments(task_id)

        if not comments:
            await update.callback_query.message.reply_text(
                "Комментарии отсутствуют",
                reply_markup=InlineKeyboardMarkup([[get_back_button()]])
            )
            return

        comments_text = "\n".join(
            [f"{i+1}. @{comment[0]}: {comment[1]} ({comment[2].split()[0]})" 
             for i, comment in enumerate(comments)]
        )

        keyboard = [
            [InlineKeyboardButton("✏️ Добавить комментарий", callback_data=f"comment_{task_id}")],
            [get_back_button()]
        ]

        await update.callback_query.message.edit_text(
            f"Комментарии к задаче #{task_id}:\n\n{comments_text}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def register_comment_handlers(application):
    """Функция для регистрации обработчиков комментариев"""
    CommentHandlers(application)