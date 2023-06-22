# Quiz Bots

## About

This project consists of two bots for Telegram and VKontakte respectively. Each bot starts a quiz with user, using questions and answers readed from JSON-file. Both bots stores last asked queastion for each user in Redis database. Project also contains a script for automated creation of JSON-file with questions from text files with corresponding marks for each question and answer. Note that this script expects input text file to be encoded in KOI8. Each script might be used standalone.

Links to the bots:
- [Telegram bot](http://t.me/DvmnQuizBot)
- [Vkontakte bot](https://vk.com/im?sel=-216230564)

This project created for educational purposes as part of an online course for web developers at [dvmn.org](https://dvmn.org/)

## Preparing project to run

1. Download files from GitHub with `git clone` command:
```
git clone https://github.com/SergIvo/dvmn-quiz-bot
```
2. Create virtual environment using python [venv](https://docs.python.org/3/library/venv.html) to avoid conflicts with different versions of the same packages:
```
python -m venv venv
```
3. Then install dependencies from "requirements.txt" in created virtual environment using `pip` package manager:
```
pip install -r requirements.txt
```
4. To run the project scripts, you should first set some environment variables. To make environment variable management easier, you can create [.env](https://pypi.org/project/python-dotenv/#getting-started) file and store all variables in it. Both bots in the project requires database URL to connect to Redis database:
```
REDIS_DB_URL=redis://[[username]:[password]]@host:port/database
```
You can read through [this part](https://redis.readthedocs.io/en/latest/connections.html#redis.Redis) of Redis documentation to know more about types of database URLs Redis can connect to.

## Running scripts

### Telegram bot
To run Telegram bot, you should additionally set following environment variables:
```
export TG_API_KEY="your Telegram API key"
export TG_LOG_CHAT_ID="ID of the chat to there bot will log service information (warnings, error messages, etc.)"
```
Then run bot with the following command:
```
python tg_bot.py
```

### VKontakte bot
To run VKontakte bot, you should additionally set following environment variables:
```
export VK_GROUP_TOKEN="API key of VKontakte group in which bot supposed to respond in the group chat"
export TG_API_KEY="your Telegram API key, needed by logger"
export TG_LOG_CHAT_ID="ID of the chat to there bot will log service information (warnings, error messages, etc.)"
```
Then run bot with the following command:
```
python vk_bot.py
```

### Script for parsing questions from .txt files
This script parses text files with questions and save it to JSON file. Script accepts relative path or full path to directory, containing .txt files with questions. Questions and answers should be marked as following:
```
Вопрос:
Текст вопроса

Ответ:
Текст ответа
```

To run script, execute the following command:
```
python load_questions.py "path to directory with questions"
```

