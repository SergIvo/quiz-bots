import json
import logging
from random import choice
from io import BytesIO

import qrcode
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
    CallbackContext, ConversationHandler)
from environs import Env
from redis import Redis
from telegram_logging import TgLogsHandler


logger = logging.getLogger('tg-quiz-bot')

NEW_QUESTION, ANSWER, QR_CODE = range(3)


def give_hint(answer):
    words = answer.split()
    word_length = len(words[0])
    if word_length % 10 == 1 and word_length != 11:
        letter_word_form = 'буква'
    elif word_length % 10 in range(2, 5) and word_length not in range(11, 20):
        letter_word_form = 'буквы'
    else:
        letter_word_form = 'букв'
    if len(words) > 1:
        return f'В первом слове ответа {word_length} {letter_word_form}.'
    return f'В ответе {word_length} {letter_word_form}.'


def save_to_redis(db_connection, key, value):
    encoded_value = json.dumps(value)
    db_connection.set(key, encoded_value)


def read_from_redis(db_connection, key):
    encoded_value = db_connection.get(key)
    if encoded_value:
        return json.loads(encoded_value.decode())
    else:
        return None


def make_qr(user_id, user_score):
    qr_image = qrcode.make(
        {
            'user_id': user_id,
            'user_score': user_score
        }
    )
    image_bytes = BytesIO()
    image_bytes.name = f'{user_id}.png'
    qr_image.save(image_bytes, 'PNG')
    image_bytes.seek(0)
    return image_bytes


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
    keyboard = [['Подсказка', 'Сдаюсь']]
    keyboard_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    questions = context.bot_data.get('questions')
    db_connection = context.bot_data.get('db_connection')
    user_id = update.message.from_user.id

    new_question = choice(list(questions.keys()))

    if read_from_redis(db_connection, user_id):
        user_state = read_from_redis(db_connection, user_id)
        user_score = user_state['score']
    else:
        user_score = 0

    save_to_redis(
        db_connection,
        user_id,
        {
            'question': new_question,
            'hint': True,
            'score': user_score
        }
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
    user_state = read_from_redis(db_connection, user_id)
    question = user_state['question']
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

    user_state = read_from_redis(db_connection, user_id)
    question = user_state['question']
    answer = questions[question]
    if update.message.text.lower() in answer.lower():
        user_state['score'] += 1
        if user_state['score'] >= 5:
            message_text = '''
                Поздравляю! Вы выиграли <НИЧЕГО>. 
            '''
            keyboard = [['Получить приз']]
            next_state = QR_CODE
        else:
            message_text = '''
                Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»
            '''
            keyboard = [['Новый вопрос']]
            next_state = NEW_QUESTION

        save_to_redis(db_connection, user_id, user_state)
    elif update.message.text == 'Подсказка':
        message_text = give_hint(answer)
        keyboard = [['Сдаюсь']]
        next_state = ANSWER
    else:
        message_text = '''
            Неправильно… Попробуешь ещё раз?
        '''
        if user_state['hint']:
            keyboard = [['Подсказка', 'Сдаюсь']]
        else:
            keyboard = [['Сдаюсь']]
        next_state = ANSWER
    keyboard_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        message_text,
        reply_markup=keyboard_markup
    )
    return next_state


def handle_qr(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    db_connection = context.bot_data.get('db_connection')
    user_state = read_from_redis(db_connection, user_id)

    qr_code = make_qr(user_id, user_state['score'])
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=qr_code,
        caption='Покажи организаторам этот QR-код, чтобы получить свою награду.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


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
            ],
            QR_CODE: [
                MessageHandler(Filters.text('Получить приз'), handle_qr)
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
