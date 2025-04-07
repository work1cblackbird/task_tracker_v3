from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config
import datetime
from database import get_tasks_from_db


class TaskFilters:
    @staticmethod
    async def apply_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Применяет фильтры и показывает задачи"""
        user_id = update.effective_user.id
        user_role = context.user_data.get('role', Config.ROLES['USER'])
        filters = context.user_data.get('filters', {})

        # Получаем задачи с учетом роли
        if user_role == Config.ROLES['USER']:
            tasks = get_tasks_from_db(created_by=user_id)
        else:
            tasks = get_tasks_from_db()

        # Применяем фильтры
        if 'status' in filters:
            tasks = [t for t in tasks if t['status'] == filters['status']]
        if 'date_range' in filters:
            start_date, end_date = filters['date_range']
            tasks = [
                t for t in tasks
                if start_date <= datetime.datetime.strptime(t['created_at'], '%Y-%m-%d %H:%M:%S') <= end_date
            ]

        # Показываем задачи
        await TaskFilters._show_filtered_tasks(update, tasks, user_role)

    @staticmethod
    async def _show_filtered_tasks(update: Update, tasks: list, user_role: str):
        """Отображает отфильтрованные задачи с пагинацией"""
        if not tasks:
            await update.callback_query.edit_message_text("Задачи не найдены.")
            return

        keyboard = []
        for task in tasks[:5]:  # Показываем первые 5 задач
            btn_text = f"#{task['id']} - {task['description'][:30]}..."
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"task_{task['id']}")])

        # Добавляем кнопки фильтров
        filter_btn = InlineKeyboardButton("🔄 Фильтры", callback_data="open_filters")
        keyboard.append([filter_btn])

        # Добавляем пагинацию, если задач больше 5
        if len(tasks) > 5:
            pagination_row = [
                InlineKeyboardButton("⬅️", callback_data="prev_page"),
                InlineKeyboardButton("1/2", callback_data="page_info"),
                InlineKeyboardButton("➡️", callback_data="next_page")
            ]
            keyboard.append(pagination_row)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            f"Найдено задач: {len(tasks)}",
            reply_markup=reply_markup
        )

    @staticmethod
    async def show_filter_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает меню фильтров"""
        keyboard = [
            [
                InlineKeyboardButton("🔘 Все", callback_data="filter_all"),
                InlineKeyboardButton("Новые", callback_data="filter_new")
            ],
            [
                InlineKeyboardButton("В работе", callback_data="filter_in_progress"),
                InlineKeyboardButton("Завершённые", callback_data="filter_done")
            ],
            [
                InlineKeyboardButton("📅 Сегодня", callback_data="filter_today"),
                InlineKeyboardButton("📅 Неделя", callback_data="filter_week")
            ],
            [
                InlineKeyboardButton("📅 Месяц", callback_data="filter_month"),
                InlineKeyboardButton("📅 Произвольный", callback_data="filter_custom")
            ],
            [
                InlineKeyboardButton("❌ Сбросить", callback_data="filter_reset"),
                InlineKeyboardButton("🔙 Назад", callback_data="cancel_filters")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            "Выберите фильтры:",
            reply_markup=reply_markup
        )

    @staticmethod
    async def handle_filter_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает выбор фильтра"""
        query = update.callback_query
        data = query.data

        if data == "filter_all":
            context.user_data['filters'] = {}
        elif data.startswith("filter_"):
            status_map = {
                "filter_new": "new",
                "filter_in_progress": "in_progress",
                "filter_done": "done"
            }
            if data in status_map:
                context.user_data['filters'] = {'status': status_map[data]}
            elif data == "filter_today":
                today = datetime.datetime.now()
                context.user_data['filters'] = {
                    'date_range': (
                        today.replace(hour=0, minute=0, second=0),
                        today.replace(hour=23, minute=59, second=59)
                    )
                }
            elif data == "filter_week":
                now = datetime.datetime.now()
                start = now - datetime.timedelta(days=now.weekday())
                end = start + datetime.timedelta(days=6)
                context.user_data['filters'] = {
                    'date_range': (
                        start.replace(hour=0, minute=0, second=0),
                        end.replace(hour=23, minute=59, second=59)
                    )
                }
            elif data == "filter_month":
                now = datetime.datetime.now()
                start = now.replace(day=1)
                end = (start + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
                context.user_data['filters'] = {
                    'date_range': (
                        start.replace(hour=0, minute=0, second=0),
                        end.replace(hour=23, minute=59, second=59)
                    )
                }

        await TaskFilters.apply_filters(update, context)