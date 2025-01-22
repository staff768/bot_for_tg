from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "7578514497:AAEQLow8BzQXto524xlu7FDqRYViK0KBdEs"
ADMIN_ID = [-4643547958]  # ID группы модерации
CHANNEL_ID = "-1002164491208"  # ID канала

user_suggestions = {}  # Словарь для временного хранения сообщений

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправьте своё предложение для канала.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text
        user_id = update.message.from_user.id
        username = update.message.from_user.username or "Без имени"

        suggestion_id = str(user_id) + "_" + str(update.message.message_id)
        user_suggestions[suggestion_id] = user_message

        keyboard = [
            [
                InlineKeyboardButton("✅ Одобрить", callback_data=f"approve|{suggestion_id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject|{suggestion_id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Ваше предложение отправлено на рассмотрение!")

        for admin in ADMIN_ID:
            await context.bot.send_message(
                chat_id=admin,
                text=f"Новое предложение от @{username} (ID: {user_id}):\n\n{user_message}",
                reply_markup=reply_markup
            )
    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("Произошла ошибка, попробуйте позже.")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        action, suggestion_id = query.data.split('|')
        user_message = user_suggestions.get(suggestion_id, "Сообщение недоступно")

        if action == "approve":
            # Отправляем сообщение в кавычках
            formatted_message = f'"{user_message}"'

            # Отправляем в канал
            await context.bot.send_message(chat_id=CHANNEL_ID, text=formatted_message)
            await query.edit_message_text(text="Сообщение опубликовано!")

            # Убираем предложение из словаря
            user_suggestions.pop(suggestion_id, None)

        elif action == "reject":
            await query.edit_message_text(text="Сообщение отклонено.")
            user_suggestions.pop(suggestion_id, None)

    except Exception as e:
        print(f"Ошибка: {e}")
        await query.edit_message_text(text="Произошла ошибка при обработке.")


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.run_polling()

if __name__ == "__main__":
    main()
