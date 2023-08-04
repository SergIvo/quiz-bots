FROM python:3.10-alpine

WORKDIR /quiz_bot

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "tg_bot.py"]
