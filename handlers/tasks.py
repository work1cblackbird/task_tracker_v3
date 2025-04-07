from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import Config
import database
import utils.keyboards
import utils.pagination
import utils.filters
import utils.calendar
import logging

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def create_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик создания новой задачи"""
    try:
        await update.message.reply_text(
            "Введите описание задачи:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data="cancel")]])
        )
        context.user_data["state"] = "awaiting_task_description"
    except Exception as e:
        logger.error(f"Ошибка в create_task: {e}")
        await update.message.reply_text("Произошла ошибка при создании задачи")

async def handle_task_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ввода описания задачи"""
    try:
        if "state" not in context.user_data or context.user_data["state"] != "awaiting_task_description":
            return

        description = update.message.text
        username = update.effective_user.username
        
        task_id = database.add_task(
            description=description,
            created_by=username,
            status=Config.TASK_STATUSES[0]  # new
        )
        
        await update.message.reply_text(
            f"✅ Задача #{task_id} создана!",
            reply_markup=utils.keyboards.get_main_menu(update.effective_user.username)
        )
        context.user_data.clear()
    except Exception as e:
        logger.error(f"Ошибка в handle_task_description: {e}")
        await update.message.reply_text("Ошибка при сохранении задачи")

async def show_task_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список задач с пагинацией"""
    try:
        user_role = database.get_user_role(update.effective_user.username)
        tasks = database.get_tasks_for_user(
            username=update.effective_user.username,
            role=user_role
        )
        
        await utils.pagination.send_task_page(
            update=update,
            tasks=tasks,
            page=1,
            total_pages=len(tasks) // Config.TASKS_PER_PAGE + 1
        )
    except Exception as e:
        logger.error(f"Ошибка в show_task_list: {e}")
        await update.message.reply_text("Ошибка при загрузке задач")

async def show_task_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, task_id: int):
    """Показывает детали задачи"""
    try:
        task = database.get_task(task_id)
        if not task:
            await update.callback_query.answer("Задача не найдена")
            return

        comments = database.get_comments(task_id)
        keyboard = utils.keyboards.get_task_detail_keyboard(
            task_id=task_id,
            status=task["status"],
            is_admin=(update.effective_user.username == Config.ADMIN_USERNAME)
        )
        
        message_text = (
            f"Задача #{task_id}\n"
            f"──────────\n"
            f"Описание: {task['description']}\n"
            f"Статус: {task['status']}\n"
            f"Автор: @{task['created_by']}\n"
            f"Дата: {task['created_at']}\n"
            f"──────────\n"
            f"Комментарии ({len(comments)}):\n" +
            "\n".join([f"{i+1}. @{c['username']}: {c['text']} ({c['created_at']})" for i, c in enumerate(comments)])
        )
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=message_text,
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text(
                text=message_text,
                reply_markup=keyboard
            )
    except Exception as e:
        logger.error(f"Ошибка в show_task_detail: {e}")
        await update.message.reply_text("Ошибка при загрузке задачи")

async def handle_task_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает действия с задачами (изменение статуса, удаление)"""
    try:
        query = update.callback_query
        data = query.data.split("_")
        
        if data[0] == "task":
            await show_task_detail(update, context, int(data[1]))
        elif data[0] == "status":
            database.update_task_status(int(data[1]), data[2])
            await show_task_detail(update, context, int(data[1]))
        elif data[0] == "delete":
            database.delete_task(int(data[1]))
            await query.answer("Задача удалена")
            await query.message.delete()
        elif data[0] == "comment":
            context.user_data["task_id"] = int(data[1])
            await query.message.reply_text("Введите ваш комментарий:")
            context.user_data["state"] = "awaiting_comment"
    except Exception as e:
        logger.error(f"Ошибка в handle_task_action: {e}")
        await update.callback_query.answer("Произошла ошибка")

async def handle_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает добавление комментария"""
    try:
        if "state" not in context.user_data or context.user_data["state"] != "awaiting_comment":
            return

        database.add_comment(
            task_id=context.user_data["task_id"],
            username=update.effective_user.username,
            text=update.message.text
        )
        
        await update.message.reply_text("Комментарий добавлен!")
        await show_task_detail(update, context, context.user_data["task_id"])
        context.user_data.clear()
    except Exception as e:
        logger.error(f"Ошибка в handle_comment: {e}")
        await update.message.reply_text("Ошибка при добавлении комментария")

async def show_task_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню фильтров"""
    try:
        await update.callback_query.message.edit_reply_markup(
            reply_markup=utils.keyboards.get_filters_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в show_task_filters: {e}")
        await update.callback_query.answer("Произошла ошибка")

async def handle_custom_date_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор произвольного периода через календарь"""
    try:
        await utils.calendar.send_date_selection(update, context)
    except Exception as e:
        logger.error(f"Ошибка в handle_custom_date_range: {e}")
        await update.message.reply_text("Ошибка при выборе даты")

def get_handlers():
    """Возвращает список обработчиков для регистрации в приложении"""
    return [
        CommandHandler("newtask", create_task),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_task_description),
        CallbackQueryHandler(show_task_list, pattern="^tasks_list"),
        CallbackQueryHandler(show_task_detail, pattern="^task_"),
        CallbackQueryHandler(handle_task_action, pattern="^(status|delete|comment)_"),
        CallbackQueryHandler(show_task_filters, pattern="^filters"),
        CallbackQueryHandler(handle_custom_date_range, pattern="^custom_date"),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_comment)
    ]