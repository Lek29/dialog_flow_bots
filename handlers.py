from telegram import Update
from telegram.ext import CallbackContext


def start(update: Update, context: CallbackContext) -> None:
    user_name = update.message.from_user.first_name
    update.message.reply_text(f'Здравствуйте! {user_name}')


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)
