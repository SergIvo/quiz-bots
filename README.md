# Quiz Bots

## About

This project consists of two bots for Telegram and VKontakte respectively. Each bot starts a quiz with user, using questions and answers readed from JSON-file. Telegram bot also provides a QR-code with user score after win. Both bots stores last asked question for each user in Redis database. Project also contains a script for automated creation of JSON-file with questions from text files with corresponding marks for each question and answer. Note that this script expects input text file to be encoded in KOI8. Each script can be used standalone.

## Preparing project to run

1. Download files from GitHub with `git clone` command:
```
git clone https://github.com/SergIvo/quiz-bots
```
2. To run the project scripts, you should first set some environment variables. To make environment variable management easier, you can create [.env](https://pypi.org/project/python-dotenv/#getting-started) file and store all variables in it.
```
VK_GROUP_TOKEN="API key of VKontakte group in which bot supposed to respond in the group chat"
TG_API_KEY="your Telegram API key, needed by logger"
TG_LOG_CHAT_ID="ID of the chat to there bot will log service information (warnings, error messages, etc.)"
```
3. Run bots in Docker with `docker compose` tool:
```
docker compose up -d
```

## Running scripts separately

1. Create virtual environment using python [venv](https://docs.python.org/3/library/venv.html):
```
python -m venv venv
```
2. Then install dependencies from "requirements.txt" in created virtual environment using `pip` package manager:
```
pip install -r requirements.txt
```
3. Since both bots in the project requires database URL to connect to Redis database, add Redis database url to your `.env` file:
```
REDIS_DB_URL=redis://[[username]:[password]]@host:port/database
```
You can read through [this part](https://redis.readthedocs.io/en/latest/connections.html#redis.Redis) of Redis documentation to know more about types of database URLs Redis can connect to.

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