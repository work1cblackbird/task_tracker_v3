from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

import config
import database
import handlers.tasks
import handlers.users
import handlers.comments
import handlers.admin
import utils.keyboards
import utils.pagination
import utils.filters
import utils.calendar


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    role = database.get_user_role(user.username)

    if role == config.ROLES["ADMIN"]:
        reply_markup = utils.keyboards.admin_main_menu()
    elif role == config.ROLES["MANAGER"]:
        reply_markup = utils.keyboards.manager_main_menu()
    else:
        reply_markup = utils.keyboards.user_main_menu()

    await update.message.reply_text(
        "Главное меню:",
        reply_markup=reply_markup
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логирование ошибок."""
    print(f"Ошибка в обработчике: {context.error}")


def main() -> None:
    """Запуск бота."""
    # Создаем приложение
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Регистрируем обработчики из модулей
    application.add_handler(handlers.tasks.tasks_handlers())
    application.add_handler(handlers.users.users_handlers())
    application.add_handler(handlers.comments.comments_handlers())
    application.add_handler(handlers.admin.admin_handlers())

    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    # Инициализация БД при первом запуске
    database.init_db()
    main()