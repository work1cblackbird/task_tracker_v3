from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from config import Config
import database
import utils.keyboards

async def handle_comment_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Комментировать' в карточке задачи"""
    query = update.callback_query
    task_id = int(query.data.split('_')[1])
    
    context.user_data['current_task'] = task_id
    context.user_data['comment_state'] = 'awaiting_text'
    
    await query.message.reply_text("Введите ваш комментарий:")

async def save_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение комментария в БД"""
    if context.user_data.get('comment_state') != 'awaiting_text':
        return
    
    task_id = context.user_data['current_task']
    username = update.effective_user.username
    text = update.message.text
    
    database.add_comment(task_id, username, text)
    
    # Обновляем карточку задачи
    task = database.get_task(task_id)
    comments = database.get_comments(task_id)
    keyboard = utils.keyboards.generate_task_keyboard(task, update.effective_user.username)
    
    # Удаляем сообщение с запросом комментария
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=update.message.message_id
    )
    
    # Обновляем карточку задачи
    await update._effective_message.edit_text(
        text=format_task_card(task, comments),
        reply_markup=keyboard
    )
    
    # Очищаем состояние
    del context.user_data['comment_state']
    del context.user_data['current_task']

def format_task_card(task, comments):
    """Форматирование карточки задачи с комментариями"""
    text = f"""Задача #{task['id']}
──────────
Описание: {task['description']}
Статус: {task['status']}
Автор: @{task['created_by']}
Дата: {task['created_at']}
──────────
Комментарии ({len(comments)}):\n"""
    
    for i, comment in enumerate(comments, 1):
        text += f"{i}. @{comment['username']}: {comment['text']} ({comment['created_at']})\n"
    
    return text

def get_handlers():
    """Возвращает список обработчиков для comments.py"""
    return [
        CallbackQueryHandler(handle_comment_button, pattern=r"^comment_\d+$"),
        MessageHandler(filters.TEXT & ~filters.COMMAND, save_comment)
    ]