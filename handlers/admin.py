# admin.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from config import Config
import database
import utils.keyboards
import utils.calendar
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=Config.LOGS_PATH
)
logger = logging.getLogger(__name__)

async def promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.data.split('_')[1]
    
    try:
        database.update_user_role(user_id, Config.ROLES["MANAGER"])
        await query.edit_message_text(
            f"Пользователь повышен до руководителя",
            reply_markup=utils.keyboards.back_to_users_list()
        )
    except Exception as e:
        logger.error(f"Ошибка повышения пользователя: {e}")
        await query.answer("Произошла ошибка")

async def demote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.data.split('_')[1]
    
    try:
        database.update_user_role(user_id, Config.ROLES["USER"])
        await query.edit_message_text(
            f"Пользователь понижен до обычного",
            reply_markup=utils.keyboards.back_to_users_list()
        )
    except Exception as e:
        logger.error(f"Ошибка понижения пользователя: {e}")
        await query.answer("Произошла ошибка")

async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.data.split('_')[1]
    
    try:
        database.delete_user(user_id)
        await query.edit_message_text(
            "Пользователь удалён",
            reply_markup=utils.keyboards.back_to_users_list()
        )
    except Exception as e:
        logger.error(f"Ошибка удаления пользователя: {e}")
        await query.answer("Произошла ошибка")

async def show_user_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        users = database.get_all_users()
        await update.message.reply_text(
            "Управление пользователями:",
            reply_markup=utils.keyboards.users_management_keyboard(users)
        )
    except Exception as e:
        logger.error(f"Ошибка отображения пользователей: {e}")
        await update.message.reply_text("Ошибка загрузки списка")

async def handle_admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action, user_id = query.data.split('_')[:2]
    
    if action == "promote":
        await promote_user(update, context)
    elif action == "demote":
        await demote_user(update, context)
    elif action == "delete":
        await delete_user(update, context)

def get_admin_handlers():
    return [
        CommandHandler("admin", show_user_management),
        CallbackQueryHandler(handle_admin_actions, pattern=r"^(promote|demote|delete)_\d+$")
    ]