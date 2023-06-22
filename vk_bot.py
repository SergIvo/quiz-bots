import json
from random import choice

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from environs import Env
from redis import Redis


def make_regular_keyboard(buttons_markup, one_time):
    keyboard = VkKeyboard(one_time=one_time)
    buttons_first_row = buttons_markup.pop(0)
    for button in buttons_first_row:
        keyboard.add_button(button, color=VkKeyboardColor.PRIMARY)
    for buttons_line in buttons_markup:
        keyboard.add_line()
        for button in buttons_line:
            keyboard.add_button(button, color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def handle_quiz_action(event, vk_api, questions, db_connection):
    user_id = event.user_id
    user = vk_api.users.get(user_ids=user_id)[0]
    user_name = user['first_name']

    if event.text == 'Новый вопрос':
        new_question = choice(list(questions.keys()))
        db_connection.set(
            user_id, 
            new_question
        )
        message_text = new_question
        keyboard_markup = [['Сдаюсь']]

    elif event.text == 'Сдаюсь':
        question = db_connection.get(user_id).decode()
        message_text = questions[question]
        keyboard_markup = [['Новый вопрос']]

    elif event.text.lower() == 'старт':
        message_text = message_text = f'''
            Привет, {user_name}!
            Чтобы начать викторину, нажми «Новый вопрос»
        '''
        keyboard_markup = [['Новый вопрос']]

    else:
        question = db_connection.get(user_id).decode()
        answer = questions[question]
        if event.text.lower() in answer.lower():
            message_text = '''
                Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»
            '''
            keyboard_markup = [['Новый вопрос']]
        else:
            message_text = '''
                Неправильно… Попробуешь ещё раз?
            '''
            keyboard_markup = [['Сдаюсь']]

    keyboard = make_regular_keyboard(keyboard_markup, True)

    vk_api.messages.send(
        user_id=user_id,
        message=message_text,
        random_id=get_random_id(),
        keyboard=keyboard
    )


if __name__ == "__main__":
    env = Env()
    env.read_env()
    redis_db_url = env('REDIS_DB_URL')
    
    with open('questions.json', 'r') as file:
        questions = json.loads(file.read())

    redis_connection = Redis.from_url(redis_db_url)
    
    vk_session = vk.VkApi(token=env('VK_API_TOKEN'))
    vk_api = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_quiz_action(
                event, 
                vk_api, 
                questions, 
                redis_connection
            )
