from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from config import Config
import database


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start. Регистрирует пользователя или обновляет роль."""
    user = update.effective_user
    username = user.username
    user_id = user.id

    # Проверяем, является ли пользователь админом
    if username == Config.ADMIN_USERNAME:
        role = Config.ROLES["ADMIN"]
    else:
        role = Config.ROLES["USER"]

    # Добавляем/обновляем пользователя в БД
    database.add_or_update_user(user_id, username, role)

    # Формируем клавиатуру в зависимости от роли
    if role == Config.ROLES["ADMIN"]:
        keyboard = [
            [InlineKeyboardButton("➕ Создать задачу", callback_data="create_task")],
            [InlineKeyboardButton("📋 Все задачи", callback_data="all_tasks")],
            [InlineKeyboardButton("👥 Управление пользователями", callback_data="manage_users")]
        ]
    elif role == Config.ROLES["MANAGER"]:
        keyboard = [
            [InlineKeyboardButton("➕ Создать задачу", callback_data="create_task")],
            [InlineKeyboardButton("📋 Все задачи", callback_data="all_tasks")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("➕ Создать задачу", callback_data="create_task")],
            [InlineKeyboardButton("📋 Мои задачи", callback_data="my_tasks")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Привет, {user.full_name}!\nВаша роль: {role}",
        reply_markup=reply_markup
    )


async def promote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Повышение пользователя до руководителя (только для админа)."""
    query = update.callback_query
    user_id_to_promote = int(query.data.split("_")[1])

    # Проверяем права текущего пользователя
    current_user = query.from_user.username
    if current_user != Config.ADMIN_USERNAME:
        await query.answer("❌ Недостаточно прав!")
        return

    # Обновляем роль в БД
    database.update_user_role(user_id_to_promote, Config.ROLES["MANAGER"])
    await query.answer(f"Пользователь повышен до {Config.ROLES['MANAGER']}")
    await query.edit_message_text(
        text=f"Роль пользователя обновлена: {Config.ROLES['MANAGER']}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Назад к списку", callback_data="user_list")]
        ])
    )


async def demote_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Понижение пользователя до обычного (только для админа)."""
    query = update.callback_query
    user_id_to_demote = int(query.data.split("_")[1])

    # Проверяем права текущего пользователя
    current_user = query.from_user.username
    if current_user != Config.ADMIN_USERNAME:
        await query.answer("❌ Недостаточно прав!")
        return

    # Обновляем роль в БД
    database.update_user_role(user_id_to_demote, Config.ROLES["USER"])
    await query.answer(f"Пользователь понижен до {Config.ROLES['USER']}")
    await query.edit_message_text(
        text=f"Роль пользователя обновлена: {Config.ROLES['USER']}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Назад к списку", callback_data="user_list")]
        ])
    )


async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление пользователя (только для админа)."""
    query = update.callback_query
    user_id_to_delete = int(query.data.split("_")[1])

    # Проверяем права текущего пользователя
    current_user = query.from_user.username
    if current_user != Config.ADMIN_USERNAME:
        await query.answer("❌ Недостаточно прав!")
        return

    # Удаляем пользователя из БД
    database.delete_user(user_id_to_delete)
    await query.answer("Пользователь удалён")
    await query.edit_message_text(
        text="Пользователь успешно удалён",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Назад к списку", callback_data="user_list")]
        ])
    )


async def show_user_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображение списка пользователей (только для админа)."""
    query = update.callback_query
    current_user = query.from_user.username

    if current_user != Config.ADMIN_USERNAME:
        await query.answer("❌ Недостаточно прав!")
        return

    users = database.get_all_users()
    keyboard = []

    for user in users:
        user_id = user[0]
        username = user[1]
        role = user[2]

        if role == Config.ROLES["USER"]:
            keyboard.append([
                InlineKeyboardButton(f"@{username} (Пользователь)", callback_data=f"user_{user_id}"),
                InlineKeyboardButton("👔 Повысить", callback_data=f"promote_{user_id}")
            ])
        elif role == Config.ROLES["MANAGER"]:
            keyboard.append([
                InlineKeyboardButton(f"@{username} (Руководитель)", callback_data=f"user_{user_id}"),
                InlineKeyboardButton("👤 Понизить", callback_data=f"demote_{user_id}")
            ])
        keyboard.append([
            InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_{user_id}")
        ])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_menu")])

    await query.edit_message_text(
        text="Список пользователей:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def setup_handlers(application):
    """Регистрация обработчиков."""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(promote_user, pattern="^promote_"))
    application.add_handler(CallbackQueryHandler(demote_user, pattern="^demote_"))
    application.add_handler(CallbackQueryHandler(delete_user, pattern="^delete_"))
    application.add_handler(CallbackQueryHandler(show_user_list, pattern="^user_list"))