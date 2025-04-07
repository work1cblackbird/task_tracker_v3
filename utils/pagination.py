from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from config import Config

async def show_paginated_tasks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    tasks: list,
    page: int = 1,
    status_filter: str = None,
    items_per_page: int = 5
) -> None:
    """
    Отображает список задач с пагинацией и фильтрами.
    
    Args:
        update: Объект Update от Telegram.
        context: Контекст бота.
        tasks: Список задач из БД.
        page: Текущая страница (начинается с 1).
        status_filter: Фильтр по статусу ('new', 'in_progress', 'done').
        items_per_page: Количество задач на странице.
    """
    if not tasks:
        await update.message.reply_text("Задачи не найдены.")
        return

    # Применяем фильтр по статусу (если указан)
    if status_filter and status_filter.lower() in Config.TASK_STATUSES:
        tasks = [task for task in tasks if task["status"] == status_filter]

    # Разбиваем задачи на страницы
    total_pages = (len(tasks) // items_per_page) + (1 if len(tasks) % items_per_page != 0 else 0)
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    paginated_tasks = tasks[start_idx:end_idx]

    # Формируем текст сообщения
    message_text = f"Страница {page}/{total_pages}\n"
    if status_filter:
        message_text += f"Фильтр: {status_filter}\n"
    message_text += "───────────────────\n"

    for task in paginated_tasks:
        message_text += (
            f"#{task['id']} — {task['description']}\n"
            f"Статус: {task['status']} | Автор: @{task['created_by']}\n"
            f"Дата: {task['created_at']}\n"
            "───────────────────\n"
        )

    # Создаем клавиатуру пагинации
    keyboard = []
    
    # Кнопки переключения страниц
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"prev_{page}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"next_{page}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)

    # Кнопка фильтров (если нужно)
    keyboard.append([InlineKeyboardButton("🔄 Фильтры", callback_data="open_filters")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем/обновляем сообщение
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=message_text,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            text=message_text,
            reply_markup=reply_markup
        )

async def handle_pagination_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    tasks: list
) -> None:
    """
    Обрабатывает нажатия кнопок пагинации.
    """
    query = update.callback_query
    data = query.data

    if data.startswith("prev_"):
        new_page = int(data.split("_")[1]) - 1
    elif data.startswith("next_"):
        new_page = int(data.split("_")[1]) + 1
    else:
        return

    await show_paginated_tasks(
        update=update,
        context=context,
        tasks=tasks,
        page=new_page,
        status_filter=context.user_data.get("current_filter")
    )