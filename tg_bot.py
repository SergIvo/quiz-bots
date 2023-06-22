import json
import logging
from random import choice

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
    CallbackContext, ConversationHandler)
from environs import Env
from redis import Redis
from telegram_logging import TgLogsHandler


logger = logging.getLogger('tg-quiz-bot')

NEW_QUESTION, ANSWER = range(2)


def start(update: Update, context: CallbackContext):
    user = update.effective_user.first_name
    keyboard = [['Новый вопрос']]
    keyboard_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    message_text = f'''
        Привет, {user}!
        Чтобы начать викторину, нажми «Новый вопрос»
    '''
    update.message.reply_text(
        message_text,
        reply_markup=keyboard_markup
    )
    return NEW_QUESTION


def send_new_question(update: Update, context: CallbackContext):
    keyboard = [['Сдаюсь']]
    keyboard_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    questions = context.bot_data.get('questions')
    db_connection = context.bot_data.get('db_connection')
    user_id = update.message.from_user.id

    new_question = choice(list(questions.keys()))
    db_connection.set(
        user_id,
        new_question
    )
    update.message.reply_text(
        new_question,
        reply_markup=keyboard_markup
    )
    return ANSWER


def handle_surrender(update: Update, context: CallbackContext):
    keyboard = [['Новый вопрос']]
    keyboard_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    questions = context.bot_data.get('questions')
    db_connection = context.bot_data.get('db_connection')
    user_id = update.message.from_user.id
    question = db_connection.get(user_id).decode()
    message_text = questions[question]

    update.message.reply_text(
        message_text,
        reply_markup=keyboard_markup
    )
    return NEW_QUESTION


def check_answer(update: Update, context: CallbackContext):
    questions = context.bot_data.get('questions')
    db_connection = context.bot_data.get('db_connection')
    user_id = update.message.from_user.id

    question = db_connection.get(user_id).decode()
    answer = questions[question]
    if update.message.text.lower() in answer.lower():
        message_text = '''
            Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»
        '''
        keyboard = [['Новый вопрос']]
        next_state = NEW_QUESTION
    else:
        message_text = '''
            Неправильно… Попробуешь ещё раз?
        '''
        keyboard = [['Сдаюсь']]
        next_state = ANSWER
    keyboard_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        message_text,
        reply_markup=keyboard_markup
    )
    return next_state


def handle_break(update: Update, context: CallbackContext):
    message_text = '''
        Ок, пока.
    '''
    update.message.reply_text(
        message_text,
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


if __name__ == '__main__':
    env = Env()
    env.read_env()
    tg_api_key = env('TG_API_KEY')
    redis_db_url = env('REDIS_DB_URL')
    tg_log_chat_id = env('TG_LOG_CHAT_ID')

    handler = TgLogsHandler(tg_api_key, tg_log_chat_id)
    handler.setFormatter(
        logging.Formatter('%(name)s %(levelname)s %(message)s')
    )
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    with open('questions.json', 'r') as file:
        questions = json.loads(file.read())

    redis_connection = Redis.from_url(redis_db_url)

    updater = Updater(tg_api_key)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['questions'] = questions
    dispatcher.bot_data['db_connection'] = redis_connection

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NEW_QUESTION: [
                MessageHandler(Filters.text('Новый вопрос'), send_new_question)
            ],
            ANSWER: [
                MessageHandler(Filters.text('Сдаюсь'), handle_surrender),
                MessageHandler(Filters.text & ~Filters.command, check_answer)
            ]
        },
        fallbacks=[CommandHandler('quite', handle_break)]
    )
    dispatcher.add_handler(conversation_handler)

    logger.info('Bot started')
    while True:
        try:
            updater.start_polling()
            updater.idle()
        except Exception as ex:
            logger.exception(ex)
