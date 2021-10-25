import configparser
import sys
from datetime import datetime as dt
import sqlite3
import telebot
from telebot import types
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from yobit import GetInfo, GetTrades
from local import loc

matplotlib.use('Agg')

config = configparser.ConfigParser()
try:
    config.read("settings.ini")
    PATH_DB = config["Path"]["db"]
    PATH_PIC = config["Path"]["pic"]
    TOKEN = config["Telegram"]["token"]
    KEY = config["Yobit"]["key"]
    SECRET = config["Yobit"]["secret"]
    API_URL = config["Yobit"]["api_url"]
    TAPI_URL = config["Yobit"]["tapi_url"]
except:
    sys.exit("Settings reading error. Check the file settings.ini")

bot = telebot.TeleBot(TOKEN)


# ============================================================
# KEYBOARD - клавиатуры по уровням вложенности

# LEVEL 1 Keyboard: START
@bot.message_handler(commands=['start'])
def send_keyboard_start(message, text=loc['welcome']):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton(loc['btn1_market'])
    btn2 = types.KeyboardButton(loc['btn2_portf'])
    btn3 = types.KeyboardButton(loc['btn3_demo'])
    btn4 = types.KeyboardButton(loc['btn4_help'])
    keyboard.add(btn1, btn2)
    keyboard.add(btn3, btn4)

    msg = bot.send_message(message.from_user.id,
                    text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_worker_start)

# LEVEL 2 Keyboard: START -> MARKET
@bot.message_handler(commands=['market'])
def send_keyboard_market(message, text=loc['select_command']):
    keyboard = types.ReplyKeyboardMarkup(row_width=3)
    btn1 = types.KeyboardButton(loc['btn11_coininfo'])
    btn2 = types.KeyboardButton(loc['btn12_cointrades'])
    btn_back = types.KeyboardButton(loc['btn_back'])
    keyboard.add(btn1, btn2)
    keyboard.add(btn_back)

    msg = bot.send_message(message.from_user.id,
                     text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_worker_market)

# LEVEL 2 Keyboard: START -> PORTFOLIO
@bot.message_handler(commands=['portfolio'])
def send_keyboard_portf(message, text=loc['select_command']):
    keyboard = types.ReplyKeyboardMarkup(row_width=3)
    btn1 = types.KeyboardButton(loc['btn21_showportf'])
    btn2 = types.KeyboardButton(loc['btn22_showtrades'])
    btn3 = types.KeyboardButton(loc['btn23_addtrade'])
    btn4 = types.KeyboardButton(loc['btn24_deletetrade'])
    btn5 = types.KeyboardButton(loc['btn25_clearportf'])
    btn_back = types.KeyboardButton(loc['btn_back'])
    keyboard.add(btn1, btn2, btn3)
    keyboard.add(btn4, btn5, btn_back)

    msg = bot.send_message(message.from_user.id,
                     text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_worker_portf)

# LEVEL 2 Keyboard: START -> DEMO
@bot.message_handler(commands=['demo'])
def send_keyboard_demo(message, text=loc['select_command']):
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    btn1 = types.KeyboardButton(loc['btn31_copyportf'])
    btn_back = types.KeyboardButton(loc['btn_back'])
    keyboard.add(btn1)
    keyboard.add(btn_back)

    msg = bot.send_message(message.from_user.id,
                     text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, callback_worker_demo)

# ============================================================
# CALBACK - обработка нажатий

# CALBACK LEVEL 1 START
def callback_worker_start(call):
    if call.text == loc['btn1_market']:
        msg = bot.send_message(call.chat.id, loc['btn1_market_reply'])
        send_keyboard_market(call, loc['select_command'])
    elif call.text == loc['btn2_portf']:
        msg = bot.send_message(call.chat.id, loc['btn2_portf_reply'])
        send_keyboard_portf(call, loc['select_command'])
    elif call.text == loc['btn3_demo']:
        msg = bot.send_message(call.chat.id, loc['btn3_demo_reply'])
        send_keyboard_demo(call, loc['select_command'])
    elif call.text == loc['btn4_help']:
        ShowHelp(call)
    else:
        send_keyboard_start(call, loc['unknown'])

# CALBACK LEVEL 2 START -> MARKET
def callback_worker_market(call):
    if call.text == loc['btn11_coininfo']:
        msg = bot.send_message(call.chat.id, loc['btn11_coininfo_reply'])
        bot.register_next_step_handler(msg, ShowInfo)
    elif call.text == loc['btn12_cointrades']:
        msg = bot.send_message(call.chat.id, loc['btn12_cointrades_reply'])
        bot.register_next_step_handler(msg, ShowTrades)
    elif call.text == loc['btn_back']:
        send_keyboard_start(call)
    else:
        send_keyboard_market(call, loc['unknown'])

# CALBACK LEVEL 2 START -> PORTFOLIO
def callback_worker_portf(call):
    if call.text == loc['btn23_addtrade']: # добавить сделку
        msg = bot.send_message(call.chat.id, loc['btn23_addtrade_reply'])
        bot.register_next_step_handler(msg, AddTradePortf)
    elif call.text == loc['btn22_showtrades']: # показать все сделки из портфеля
        ShowTradesPortf(call)
    elif call.text == loc['btn21_showportf']:
        try:
            ShowPortf(call)
        except:
            bot.send_message(call.chat.id, loc['portfolio_empty'])
            send_keyboard_portf(call, loc['what_next'])
    elif call.text == loc['btn24_deletetrade']:
        try:
            SelectTradeDelete(call)
        except:
            bot.send_message(call.chat.id, loc['portfolio_empty'])
            send_keyboard_portf(call, loc['what_next'])
    elif call.text == loc['btn25_clearportf']:
        try:
            ClearPortf(call)
        except:
            bot.send_message(call.chat.id, loc['portfolio_empty'])
            send_keyboard_portf(call, loc['what_next'])
    elif call.text == loc['btn_back']:
        send_keyboard_start(call)
    else:
        send_keyboard_portf(call, loc['unknown'])

# CALBACK LEVEL 2 START -> DEMO
def callback_worker_demo(call):
    if call.text == loc['btn31_copyportf']:
        CopyPortf(call)
    elif call.text == loc['btn_back']:
        send_keyboard_start(call)
    else:
        send_keyboard_demo(call, loc['unknown'])


# ============================================================
# ФУНКЦИИ вспомогательные

# превращаем coin из любого регистра в пару к usd
def ConstructPair(coin):
    pair = coin.lower() + '_' + 'usd'
    return pair

# выгрузить сделки юзера в DF
def GetDF_FromDB(user_id):
    with sqlite3.connect(PATH_DB) as con:
        sql = 'SELECT * FROM coins WHERE user_id=={}'.format(user_id)
        df = pd.read_sql(sql, con)
        df = df.loc[:, df.columns != 'user_id']
    return df

# формирование красивого списка сделок
def TradeListExterior(df):
    df['timestamp'] = [dt.fromtimestamp(x) for x in df['timestamp']]
    df['coin'] = df['coin'].str.upper()
    df = df.astype(str)
    text = '<code>'
    for i in range(df.shape[0]):
        row = df.iloc[i].tolist()
        text += '#' + ', '.join(row) + '\n'
    text += '</code>'
    return text

# добавление курсов криптомонет
def AddCoinsRate(df):
    coins_lst = df['coin'].to_list()
    pairs_str = '_usd-'.join(coins_lst)+'_usd'
    ticker_json = GetInfo(pairs_str, API_URL)
    df['rate'] = df['coin'].map(lambda x: ticker_json[x+'_usd']['sell'])
    df['cost'] = df['rate'] * df['ammount']
    return df

# создание графика состава портфеля
def CreatePie(df):
    df['res'] = df.ammount * np.where(df.type == 'sell', -1, 1)
    portf = df.groupby(['coin']).sum()['res']
    portf = pd.DataFrame({'coin':portf.index, 'ammount':portf.values})
    portf = AddCoinsRate(portf)
    total = portf.cost.sum()
    portf.plot(kind='pie', y='cost',
            figsize=(6,6),
            labels=portf.coin.str.upper(),
            label='', legend = False,
            autopct=lambda p: '${abs:.1f} ({p:.1f}%)' \
                .format(abs = p * total / 100, p = p))
    plt.savefig(PATH_PIC)
    return total

# ФУНКЦИИ обработки
# ============================================================
# FUNC LEVEL 2 START -> MARKET

def ShowInfo(msg):
    coin = msg.text
    pair = ConstructPair(coin)
    try:
        ticker_json = GetInfo(pair, API_URL)
        text = '''
        <b>{title}</b><code>
        Курс покупки        : ${buy:.4f}
        Курс продажи        : ${sell:.4f}
        Максимум за 24 ч    : ${high:.4f}
        Минимум за 24 ч     : ${low:.4f}
        Объем торгов за 24 ч: ${vol:.4f}
        </code>
        '''.format(title = coin.upper() + '-USD',
                buy = ticker_json[pair]['buy'],
                sell = ticker_json[pair]['sell'],
                high = ticker_json[pair]['high'],
                low = ticker_json[pair]['low'],
                vol = ticker_json[pair]['vol'])
        bot.send_message(msg.chat.id, text, parse_mode = 'HTML')
        send_keyboard_market(msg, loc['what_next'])
    except:
        send_keyboard_market(msg, loc['unknown_coin'])

def ShowTrades(msg):
    coin = msg.text
    pair = ConstructPair(coin)
    try:
        ticker_json = GetTrades(pair, API_URL)
        text = '<b>{title}</b>\n<code>'.format(title = coin.upper() + '-USD')
        for i in range(min(10, len(ticker_json))): # показываем 10 последних сделок
            text += ' - {type} {amount} {coin} по курсу ${price:.4f}, {date} \n'.format(
                coin = coin.upper(),
                type = (ticker_json[i]['type']).upper(),
                amount = ticker_json[i]['amount'],
                price = ticker_json[i]['price'],
                date = dt.fromtimestamp(ticker_json[i]['timestamp']))
        text += '</code>'
        bot.send_message(msg.chat.id, text, parse_mode = 'HTML')
        send_keyboard_market(msg, loc['what_next'])
    except:
        send_keyboard_market(msg, loc['unknown_coin'])


# FUNC LEVEL 2 START -> PORTFOLIO

# добавить сделку
def AddTradePortf(msg):
    try:
        trade = (msg.text).lower().replace(', ', ',').split(sep=',')

        # если дата не указана, то подставить текущую
        if len(trade) == 5:
            trade_date = dt.strptime(trade[4], '%Y-%m-%d %H:%M:%S')
        else:
            trade_date = dt.now()
        stamp = int(round(trade_date.timestamp()))

        with sqlite3.connect(PATH_DB) as con:
            cursor = con.cursor()
            sql = '''
            INSERT INTO coins (user_id, coin, type, ammount, usd, timestamp) VALUES (?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(sql,
                           (msg.from_user.id, trade[0], trade[1],
                           float(trade[2]), float(trade[3]), stamp))
            con.commit()
        bot.send_message(msg.chat.id, loc['complete'])
        send_keyboard_portf(msg, loc['what_next'])
    except:
        send_keyboard_portf(msg, loc['failed_command'])

# показать все сделки из портфеля
def ShowTradesPortf(msg):
    try:
        df = GetDF_FromDB(msg.from_user.id)
        text = TradeListExterior(df)
        bot.send_message(msg.chat.id, text, parse_mode = 'HTML')
        send_keyboard_portf(msg, loc['what_next'])
    except:
        send_keyboard_portf(msg, loc['portfolio_empty'])

# показать портфель
def ShowPortf(msg):
    try:
        df = GetDF_FromDB(msg.from_user.id)
        total = CreatePie(df)
        photo = open(PATH_PIC, 'rb')
        bot.send_photo(msg.chat.id, photo, 'Оценка портфеля: ${:.1f}'.format(total))
        send_keyboard_portf(msg, loc['what_next'])
    except:
        send_keyboard_portf(msg, loc['portfolio_empty'])

# выделяет сделку для удаления
def SelectTradeDelete(msg):
    df = GetDF_FromDB(msg.from_user.id)
    text = TradeListExterior(df)
    bot.send_message(msg.chat.id, text, parse_mode = 'HTML')
    msg = bot.send_message(msg.from_user.id, text = loc['btn24_deletetrade_reply'])
    bot.register_next_step_handler(msg, DeleteTrade)


# удаляет эту сделку
def DeleteTrade(msg):
    with sqlite3.connect(PATH_DB) as con:
        cursor = con.cursor()
        cursor.execute('DELETE FROM coins WHERE user_id==? AND id==?', \
                       (msg.from_user.id, msg.text))
        bot.send_message(msg.chat.id, loc['complete'])
        send_keyboard_portf(msg, loc['what_next'])

# очищает весь портфель
def ClearPortf(msg):
    try:
        with sqlite3.connect(PATH_DB) as con:
            cursor = con.cursor()
            cursor.execute('DELETE FROM coins WHERE user_id=={}'.format(msg.from_user.id))
            con.commit()
        bot.send_message(msg.chat.id, loc['complete'])
        send_keyboard_portf(msg, loc['what_next'])
    except:
        send_keyboard_portf(msg, loc['portfolio_empty'])

# FUNC LEVEL 2 START -> DEMO

# копирует демо-портфель
def CopyPortf(msg):
    try:
        with sqlite3.connect(PATH_DB) as con:
            sql = '''
            CREATE TEMPORARY TABLE tmp
            AS SELECT user_id, coin, type, ammount, usd, timestamp
            FROM coins WHERE user_id = 999;

            UPDATE tmp SET user_id = {};

            INSERT INTO coins (user_id, coin, type, ammount, usd, timestamp)
            SELECT * FROM tmp;
            '''.format(msg.from_user.id)
            cursor = con.cursor()
            cursor.executescript(sql)
            con.commit()
        
        bot.send_message(msg.chat.id, loc['complete'])
        send_keyboard_start(msg, loc['what_next'])
    except:
        send_keyboard_demo(msg, loc['failed_command'])

# FUNC LEVEL 2 START -> HELP

# Показывает справку
def ShowHelp(msg):
    try:     
        bot.send_message(msg.chat.id, loc['btn4_help_reply'], parse_mode = 'HTML')
        send_keyboard_start(msg, loc['select_command'])
    except:
        send_keyboard_demo(msg, loc['failed_command'])

# ============================================================
# БД

# подключаем базу данных
conn = sqlite3.connect(PATH_DB)
cursor = conn.cursor()

query = '''
    CREATE TABLE IF NOT EXISTS coins (
        id INTEGER UNIQUE,
        user_id INTEGER,
        coin TEXT,
        type TEXT,
        ammount REAL,
        usd REAL,
        timestamp INTEGER,
        PRIMARY KEY (id)
    )
'''

try:
    cursor.execute(query)
except:
    sys.exit(loc['failed_dbquery'])


# ============================================================
# ОПРОС БОТА

bot.polling(none_stop=True)