# -*- coding: utf-8 -*-
"""
Главный модуль бота Task Tracker
Точка входа и обработка основных команд
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from config import BotConfig, Roles
from database import db
from utils.keyboards import get_main_menu_keyboard

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TaskTrackerBot:
    def __init__(self):
        self.application = Application.builder().token(BotConfig.BOT_TOKEN).build()
        self._register_handlers()

    def _register_handlers(self):
        """Регистрация всех обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_handler))
        self.application.add_handler(CommandHandler("help", self.help_handler))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler)
        )

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        if not db.get_user(user.username):
            db.add_user(user.username)

        keyboard = get_main_menu_keyboard(user.username)
        await update.message.reply_text(
            f"Привет, {user.first_name}! Выберите действие:",
            reply_markup=keyboard
        )

    async def help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
        📌 Доступные команды:
        /start - Главное меню
        /help - Справка
        
        Основные функции доступны через кнопки меню
        """
        await update.message.reply_text(help_text)

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на inline-кнопки"""
        query = update.callback_query
        await query.answer()

        if query.data == "create_task":
            context.user_data["awaiting_task"] = True
            await query.message.reply_text("Введите описание задачи:")

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        if context.user_data.get("awaiting_task"):
            description = update.message.text
            task_id = db.add_task(description, update.effective_user.username)
            context.user_data.pop("awaiting_task")
            await update.message.reply_text(f"Задача #{task_id} создана!")
        else:
            await update.message.reply_text("Используйте кнопки меню")

    def run(self):
        """Запуск бота"""
        self.application.run_polling()

if __name__ == "__main__":
    # Инициализация базы данных
    if not db.get_user(BotConfig.ADMIN_USERNAME):
        db.add_user(BotConfig.ADMIN_USERNAME, Roles.ADMIN)
    
    # Создание и запуск бота
    bot = TaskTrackerBot()
    bot.run()