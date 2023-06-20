import json
from random import choice

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from environs import Env


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(
        f'Привет, {user}!'
    )


def reply_with_keyboard(update: Update, context: CallbackContext) -> None:
    keyboard = [['Random button'], ['Назад', 'Новый вопрос']]
    keyboard_markup = ReplyKeyboardMarkup(keyboard)
    if update.message.text == 'Новый вопрос':
        questions = context.bot_data.get('questions')
        new_question = choice(questions)
        message_text = new_question['question']
    else:
        message_text = 'Random text'
    update.message.chat.send_message(
        message_text,
        reply_markup=keyboard_markup
    )


if __name__ == '__main__':
    env = Env()
    env.read_env()
    tg_api_key = env('TG_API_KEY')
    with open('questions.json', 'r') as file:
        questions = json.loads(file.read())

    updater = Updater(tg_api_key)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['questions'] = questions

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_with_keyboard))

    updater.start_polling()
    updater.idle()
