import json
from random import choice

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from environs import Env
from redis import Redis


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(
        f'Привет, {user}!'
    )


def reply_with_keyboard(update: Update, context: CallbackContext) -> None:
    keyboard = [['Сдаюсь', 'Новый вопрос']]
    keyboard_markup = ReplyKeyboardMarkup(keyboard)
    questions = context.bot_data.get('questions')
    db_connection = context.bot_data.get('db_connection')
    user_id = update.message.from_user.id

    if update.message.text == 'Новый вопрос':
        new_question = choice(list(questions.keys()))
        db_connection.set(
            user_id, 
            new_question
        )
        message_text = db_connection.get(user_id).decode()
    elif update.message.text == 'Сдаюсь':
        question = db_connection.get(user_id).decode()
        message_text = questions[question]
    else:
        question = db_connection.get(user_id).decode()
        answer = questions[question]
        if update.message.text.lower() in answer.lower():
            message_text = '''
                Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»
            '''
        else:
            message_text = '''
                Неправильно… Попробуешь ещё раз?
            '''
    update.message.reply_text(
        message_text,
        reply_markup=keyboard_markup
    )


if __name__ == '__main__':
    env = Env()
    env.read_env()
    tg_api_key = env('TG_API_KEY')
    redis_db_url = env('REDIS_DB_URL')
    
    with open('questions.json', 'r') as file:
        questions = json.loads(file.read())

    redis_connection = Redis.from_url(redis_db_url)

    updater = Updater(tg_api_key)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['questions'] = questions
    dispatcher.bot_data['db_connection'] = redis_connection

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_with_keyboard))

    updater.start_polling()
    updater.idle()
