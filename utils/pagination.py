# -*- coding: utf-8 -*-
"""
Модуль пагинации списка задач
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import Pagination as PaginationConfig

class Paginator:
    """Класс для управления пагинацией списка задач"""

    def __init__(self):
        self.items_per_page = PaginationConfig.TASKS_PER_PAGE
        self.max_buttons = PaginationConfig.MAX_PAGE_BUTTONS

    async def show_page(self, message, tasks, page=1, filters=None):
        """
        Отображение страницы с задачами
        :param message: Объект сообщения Telegram
        :param tasks: Полный список задач
        :param page: Номер текущей страницы
        :param filters: Примененные фильтры (для callback_data)
        :return: None
        """
        total_pages = (len(tasks) + self.items_per_page - 1) // self.items_per_page
        page = max(1, min(page, total_pages))

        start_idx = (page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_tasks = tasks[start_idx:end_idx]

        # Формируем текст сообщения
        text = self._generate_page_text(page, total_pages, filters)
        
        # Формируем клавиатуру с задачами и пагинацией
        keyboard = self._generate_page_keyboard(page_tasks, page, total_pages, filters)

        if hasattr(message, 'edit_text'):
            await message.edit_text(text, reply_markup=keyboard)
        else:
            await message.reply_text(text, reply_markup=keyboard)

    def _generate_page_text(self, page, total_pages, filters):
        """Генерация текста для страницы"""
        text = f"Страница {page}/{total_pages}\n"
        
        if filters:
            filter_text = []
            if filters.get('status'):
                filter_text.append(f"статус: {filters['status']}")
            if filters.get('period'):
                filter_text.append(f"период: {filters['period']}")
            if filter_text:
                text += "Фильтры: " + ", ".join(filter_text) + "\n"
        
        text += "───────────────────"
        return text

    def _generate_page_keyboard(self, tasks, current_page, total_pages, filters):
        """Генерация клавиатуры для страницы"""
        keyboard = []
        
        # Кнопки задач
        for task in tasks:
            keyboard.append([
                InlineKeyboardButton(
                    f"#{task[0]} {task[1][:30]}... ({task[2]})",
                    callback_data=f"task_{task[0]}")
            ])
        
        # Кнопки пагинации
        pagination_buttons = []
        filter_prefix = self._get_filter_prefix(filters)
        
        # Кнопка "Назад"
        if current_page > 1:
            pagination_buttons.append(
                InlineKeyboardButton(
                    "⬅️", 
                    callback_data=f"{filter_prefix}page_{current_page - 1}")
            )
        
        # Номер текущей страницы
        pagination_buttons.append(
            InlineKeyboardButton(
                f"{current_page}/{total_pages}", 
                callback_data="ignore")
        )
        
        # Кнопка "Вперед"
        if current_page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton(
                    "➡️", 
                    callback_data=f"{filter_prefix}page_{current_page + 1}")
            )
        
        keyboard.append(pagination_buttons)
        
        # Дополнительные кнопки
        additional_buttons = []
        additional_buttons.append(
            InlineKeyboardButton("➕ Создать задачу", callback_data="create_task")
        )
        additional_buttons.append(
            InlineKeyboardButton("🔍 Фильтры", callback_data="filter_status")
        )
        keyboard.append(additional_buttons)
        
        return InlineKeyboardMarkup(keyboard)

    def _get_filter_prefix(self, filters):
        """Генерация префикса для callback_data с учетом фильтров"""
        if not filters:
            return ""
        
        prefix = []
        if filters.get('status'):
            prefix.append(f"status_{filters['status']}")
        if filters.get('period'):
            prefix.append(f"period_{filters['period']}")
        
        return "_".join(prefix) + "_" if prefix else ""