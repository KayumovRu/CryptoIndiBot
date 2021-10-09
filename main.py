import tg.bot as bot
import yobit.yobit as yobit

# активация бота (поддержка команды start)
updater, dispatcher = bot.InitBot()
bot.ActivateBot(dispatcher, updater)

#см. tg/bot.py, yobit/yobit.py