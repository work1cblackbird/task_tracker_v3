from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from config import Config

class Calendar:
    def __init__(self):
        self.current_date = datetime.now()
        self.selected_dates = []

    def generate_month_keyboard(self, year=None, month=None):
        if year is None:
            year = self.current_date.year
        if month is None:
            month = self.current_date.month

        # Определяем первый день месяца и количество дней
        first_day = datetime(year, month, 1)
        days_in_month = (datetime(year, month + 1, 1) - timedelta(days=1)).day if month < 12 else 31
        weekday = first_day.weekday()

        # Заголовок (месяц и год)
        month_name = first_day.strftime("%B %Y")
        keyboard = [
            [InlineKeyboardButton(month_name, callback_data="ignore")],
            [InlineKeyboardButton(day, callback_data="ignore") for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]]
        ]

        # Генерация дней
        row = []
        for day in range(1, days_in_month + 1):
            date = datetime(year, month, day)
            if date in self.selected_dates:
                button_text = f"✅{day}"
            else:
                button_text = str(day)
            row.append(InlineKeyboardButton(button_text, callback_data=f"day_{year}_{month}_{day}"))
            if len(row) == 7:
                keyboard.append(row)
                row = []

        if row:
            keyboard.append(row)

        # Кнопки навигации
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        navigation_buttons = [
            InlineKeyboardButton("◀", callback_data=f"month_{prev_year}_{prev_month}"),
            InlineKeyboardButton("▶", callback_data=f"month_{next_year}_{next_month}"),
        ]
        keyboard.append(navigation_buttons)

        # Кнопки подтверждения/сброса
        action_buttons = [
            InlineKeyboardButton("🔄 Сбросить", callback_data="reset_dates"),
            InlineKeyboardButton("✅ Готово", callback_data="confirm_dates"),
        ]
        keyboard.append(action_buttons)

        return InlineKeyboardMarkup(keyboard)

    async def handle_calendar_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        data = query.data

        if data.startswith("day_"):
            _, year, month, day = data.split("_")
            date = datetime(int(year), int(month), int(day))
            if date in self.selected_dates:
                self.selected_dates.remove(date)
            else:
                self.selected_dates.append(date)
            await query.edit_message_reply_markup(reply_markup=self.generate_month_keyboard(int(year), int(month)))

        elif data.startswith("month_"):
            _, year, month = data.split("_")
            await query.edit_message_reply_markup(reply_markup=self.generate_month_keyboard(int(year), int(month)))

        elif data == "reset_dates":
            self.selected_dates = []
            await query.edit_message_reply_markup(reply_markup=self.generate_month_keyboard())

        elif data == "confirm_dates":
            if len(self.selected_dates) == 2:
                start_date = min(self.selected_dates)
                end_date = max(self.selected_dates)
                await query.edit_message_text(f"Выбран период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
                return {"start_date": start_date, "end_date": end_date}
            else:
                await query.answer("Нужно выбрать две даты (начало и конец периода)")

        await query.answer()

    async def send_calendar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Выберите период:",
            reply_markup=self.generate_month_keyboard()
        )