from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from environs import Env
from telegram import Update
from telegram.ext import CallbackContext

from dialogflow_utils import detect_intent_texts, PROJECT_ID

env = Env()
env.read_env()

bot_token = env.str('BOT_TOKEN')


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_html(
        f"Привет, {user.mention_html()}! Я теперь умный бот. Попробуй поздороваться!",
    )


def echo(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    telegram_user_id = str(update.message.from_user.id)

    query_result = detect_intent_texts(telegram_user_id, user_text, "ru")

    if query_result:
        dialogflow_response_text = query_result.fulfillment_text
        update.message.reply_text(dialogflow_response_text)
    else:
        update.message.reply_text("Извините, я не смог понять ваш запрос. Пожалуйста, попробуйте еще раз.")


def run_tg_bot():
    if not bot_token:
        return

    updater = Updater(bot_token, use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()

