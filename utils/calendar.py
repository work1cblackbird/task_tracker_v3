# -*- coding: utf-8 -*-
"""
Модуль для работы с календарем выбора дат
Интеграция с python-telegram-calendar
"""

import logging
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes
from config import CalendarConfig

# Настройка логгирования
logger = logging.getLogger(__name__)

class CalendarHandler:
    """Класс для обработки календаря и выбора дат"""
    
    def __init__(self):
        self.date_format = CalendarConfig.DATE_FORMAT
        self.quick_periods = CalendarConfig.QUICK_PERIODS
    
    def generate_calendar(self, year=None, month=None):
        """Генерация клавиатуры календаря"""
        now = datetime.now()
        if not year:
            year = now.year
        if not month:
            month = now.month

        keyboard = []
        
        # Заголовок с месяцем и годом
        month_name = self._get_month_name(month)
        keyboard.append([
            InlineKeyboardButton("◀", callback_data=f"prev_month_{year}_{month}"),
            InlineKeyboardButton(f"{month_name} {year}", callback_data="ignore"),
            InlineKeyboardButton("▶", callback_data=f"next_month_{year}_{month}")
        ])
        
        # Дни недели
        keyboard.append([
            InlineKeyboardButton(day, callback_data="ignore") 
            for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        ])
        
        # Ячейки календаря
        month_days = self._get_month_days(year, month)
        for week in month_days:
            keyboard.append([
                InlineKeyboardButton(
                    str(day) if day != 0 else " ", 
                    callback_data=f"select_day_{year}_{month}_{day}" if day != 0 else "ignore"
                ) for day in week
            ])
        
        # Быстрый выбор периода
        keyboard.append([
            InlineKeyboardButton(period, callback_data=f"quick_period_{period_id}")
            for period_id, period in self.quick_periods.items()
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def _get_month_name(self, month):
        """Получение названия месяца"""
        months = [
            "Январь", "Февраль", "Март", "Апрель", 
            "Май", "Июнь", "Июль", "Август",
            "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        return months[month - 1]
    
    def _get_month_days(self, year, month):
        """Генерация дней месяца для календаря"""
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Находим день недели первого дня месяца (0-6, где 0 - понедельник)
        weekday = first_day.weekday()
        
        # Создаем матрицу 6x7
        weeks = []
        week = [0] * 7
        
        day = 1
        for i in range(1, last_day.day + weekday + 1):
            if i <= weekday:
                week[i-1] = 0
            else:
                week[(i-1)%7] = day
                if (i-1)%7 == 6:
                    weeks.append(week)
                    week = [0] * 7
                day += 1
        
        if week != [0] * 7:
            weeks.append(week)
        
        return weeks
    
    async def process_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора даты"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("select_day_"):
            _, _, year, month, day = data.split("_")
            selected_date = datetime(int(year), int(month), int(day))
            return selected_date.strftime(self.date_format)
        
        elif data.startswith(("prev_month_", "next_month_")):
            action, year, month = data.split("_")
            year = int(year)
            month = int(month)
            
            if action == "prev_month":
                if month == 1:
                    month = 12
                    year -= 1
                else:
                    month -= 1
            else:
                if month == 12:
                    month = 1
                    year += 1
                else:
                    month += 1
            
            new_calendar = self.generate_calendar(year, month)
            await query.edit_message_reply_markup(reply_markup=new_calendar)
            return None
        
        elif data.startswith("quick_period_"):
            period = data.split("_")[2]
            now = datetime.now()
            
            if period == "today":
                return now.strftime(self.date_format)
            elif period == "week":
                start = now - timedelta(days=now.weekday())
                end = start + timedelta(days=6)
                return f"{start.strftime(self.date_format)}-{end.strftime(self.date_format)}"
            elif period == "month":
                start = datetime(now.year, now.month, 1)
                end = datetime(now.year, now.month + 1, 1) - timedelta(days=1)
                return f"{start.strftime(self.date_format)}-{end.strftime(self.date_format)}"
            else:  # all
                return "all"
        
        return None

def register_calendar_handlers(application, calendar_handler):
    """Регистрация обработчиков календаря"""
    async def calendar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await calendar_handler.process_selection(update, context)
    
    application.add_handler(
        CallbackQueryHandler(
            calendar_callback,
            pattern="^(select_day|prev_month|next_month|quick_period)_"
        )
    )