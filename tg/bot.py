import sys
import os
import telegram.ext as tgext

def InitBot():
    curdir = os.path.dirname(os.path.abspath(__file__))

    try:
        f = open(curdir + '/token.txt', 'r')
        TOKEN = f.read().splitlines()[0]
    except:
        sys.exit("Telegram token reading error. Check the file tg/token.txt")

    updater = tgext.Updater(token = TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    return updater, dispatcher

def Start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! I'm Crypto Indi Bot! I can show cryptocurrency rates and display information on your portfolio from the Yobbit exchange.")


def ActivateBot(dispatcher, updater):
    start_handler = tgext.CommandHandler('start', Start)
    dispatcher.add_handler(start_handler)

    updater.start_polling()
    updater.idle()