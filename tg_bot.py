from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from environs import Env


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    tg_api_key = env('TG_API_KEY')

    updater = Updater(tg_api_key)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()
