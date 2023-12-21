import matplotlib.pyplot as plt
import numpy as np
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove
import pandas as pd
import os
import csv

# Создание бота
bot = telebot.TeleBot('6845988169:AAEH66eYGnWn50oWQkQnzvizmvln0yma-nU')

# Обработка команды /start
@bot.message_handler(commands=['start','Выбрать действие','choose'])
def handle_start(message):
    name = message.from_user.first_name
    if message.text == '/start':
        bot.send_message(message.chat.id, text=f'Привет, {name}! Я бот, который знает информацию о ВВП стран мира.')
    bot.send_message(message.chat.id, text=f'Выбери, что тебе хочется узнать:', reply_markup=kb)

# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    global chat_id
    try:
        chat_id = message.chat.id
        cols = [str(i) for i in range(1999,2023) if i!=2011]
        df['percent'] = (df['2022']-df['1999'])/df['1999'] #прирост ВВП 1999-2022 год
        df['sum'] = df[cols].sum(axis=1)
        df_2 = df[df['Country']==message.text]
        vvp = df_2['sum'].tolist()
        vvp2022 = df_2['2022'].tolist()
        av_vvp = round(vvp[0]/22,1)
        growth = (df_2['percent']*100).tolist()
        res = f'{message.text}\nВВП за 2022 год: {round(vvp2022[0],1)} млрд $\nСредний ВВП с 1999 по 2022: {round(av_vvp,1)} млрд $\nПрирост ВВП с 1999 по 2022: {round(growth[0],1)} %'
        bot.send_message(message.chat.id, text=res)
    except: 
        bot.reply_to(message, "Произошла ошибка")

# Обработка команды /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message, "Список доступных команд:\n/start - начать работу с ботом\n/help - показать список команд")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data in ['1','2','3','4']:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ожидайте...", reply_markup=None)
    if call.data == '5':
        bot.send_message(call.message.chat.id, text='Чтобы узнать информацию про конкретную страну просто напишите ее название, например: Китай')
    elif call.data == '4':
        try:
            top_5_loss()
            bot.send_photo(call.message.chat.id,photo =open('top5loss.png','rb'))
            os.remove('top5loss.png')
        except:pass

    elif call.data == '3':
        try:
            top_5_worst()
            bot.send_photo(call.message.chat.id,photo =open('top5worst.png','rb'))
            os.remove('top5worst.png')
        except:pass
        
    elif call.data == '1':
        try:
            top_5_growth()
            bot.send_photo(call.message.chat.id,photo =open('top5growth.png','rb'))
            os.remove('top5growth.png')
        except:pass
    elif call.data == '2':
        try:
            top_5_best()
            bot.send_photo(call.message.chat.id,photo =open('top5best.png','rb'))
            os.remove('top5best.png')
        except:pass
def top_5_best():
    cols = [str(i) for i in range(1999,2023) if i!=2011]
    for i in cols:
        df[i] = df[i].astype(float)
    df['sum'] = df[cols].sum(axis=1)
    df_2 = df.nlargest(5, "sum")
    countries = df_2["Country"].tolist()
    countries=[i.replace('Соединенные Штаты','США') for i in countries]
    vvp = (df_2['sum']).tolist()
    av_vvp = [round(i/22,1) for i in vvp]
    plt.barh(countries,av_vvp,color = 'blue')
    plt.title('Топ 5 стран по среднему ВВП (по убыванию)',loc='left')
    plt.xlabel("ВВП, млрд $")
    plt.ylabel("Страны")
    plt.tight_layout()
    plt.savefig("top5best.png")
    plt.clf()

def top_5_growth(): #посчитать в процентах
    df['percent'] = (df['2022']-df['1999'])/df['1999']
    df_2 = df.nlargest(5,'percent')
    countries = df_2["Country"].tolist()
    growth = df_2['percent'].tolist()
    growth = [i*100 for i in growth]
    plt.barh(countries,growth,color = 'blue')
    plt.title('Топ 5 стран по приросту ВВП (по убыванию)',loc='left')
    plt.xlabel("Прирост ВВП в процентах, %")
    plt.ylabel("Страны")
    plt.tight_layout()
    plt.savefig("top5growth.png")
    plt.clf()

def top_5_worst():
    cols = [str(i) for i in range(1999,2023) if i!=2011]
    for i in cols:
        df[i] = df[i].astype(float)
    df['sum'] = df[cols].sum(axis=1)
    df_2 = df.nsmallest(5, "sum")
    countries = df_2["Country"].tolist()
    vvp = (df_2['sum']).tolist()
    av_vvp = [round(i/22,1) for i in vvp]
    plt.barh(countries,av_vvp,color = 'blue')
    plt.title('Топ 5 стран с наименьшим средним ВВП (по убыванию)',loc='left')
    plt.xlabel("ВВП, млрд $")
    plt.ylabel("Страны")
    plt.tight_layout()
    plt.savefig("top5worst.png")
    plt.clf()

def top_5_loss():  #посчитать в процентах
    df['percent'] = (df['2022']-df['1999'])/df['1999']
    df_2 = df.nsmallest(5,'percent')
    countries = df_2["Country"].tolist()
    growth = df_2['percent'].tolist()
    growth = [i*100 for i in growth]
    plt.barh(countries,growth,color = 'blue')
    plt.title('Топ 5 худших стран по приросту ВВП (по убыванию)',loc='left')
    plt.xlabel("Прирост ВВП в процентах, %")
    plt.ylabel("Страны")
    plt.tight_layout()
    plt.savefig("top5loss.png")
    plt.clf()

filename = 'GDP_2_result.csv'
df = pd.read_csv(filename)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton('Выбрать действие'))

kb = telebot.types.InlineKeyboardMarkup()
inline_button1 = telebot.types.InlineKeyboardButton('Топ 5 стран по приросту ВВП', callback_data='1')
inline_button2 = telebot.types.InlineKeyboardButton('Топ 5 стран по среднему ВВП', callback_data='2') 
inline_button3 = telebot.types.InlineKeyboardButton('Топ 5 стран с наименьшим ВВП ', callback_data='3') 
inline_button4= telebot.types.InlineKeyboardButton('Топ 5 худших стран по приросту ВВП', callback_data='4')
inline_button5= telebot.types.InlineKeyboardButton('Узнать данные о конкретной стране', callback_data='5')
kb.add(inline_button1)
kb.add(inline_button2)
kb.add(inline_button3)
kb.add(inline_button4)
kb.add(inline_button5)

# Запуск бота
bot.infinity_polling()