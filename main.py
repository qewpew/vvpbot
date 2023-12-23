import matplotlib.pyplot as plt
import numpy as np
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import pandas as pd
import os
import csv
plt.switch_backend('agg')

# Создание бота
bot = telebot.TeleBot('TOKEN')

# Обработка команды /start
@bot.message_handler(commands=['start','Выбрать действие','choose'])
def handle_start(message):
    name = message.from_user.first_name
    if message.text == '/start':
        bot.send_message(message.chat.id, text=f'Привет, {name}! Я бот, который знает информацию о ВВП стран мира.')
    bot.send_message(message.chat.id, text=f'Выбери, что тебе хочется узнать:', reply_markup=kb)

# Обработка текстовых сообщений
# Сделать графики: ввп по годам, прирост ввп, средний ввп по сравнению с топ 5
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    df_2 = df[df['Country'] == message.text]
    if len(df_2) == 0:
        bot.send_message(message.chat.id, "Вы ввели название страны неправильно, попробуйте еще раз", reply_markup=kb)
    else:
        chat_id = message.chat.id
        cols = [str(i) for i in range(1999,2023) if i!=2011] #все доступные года 
        df['percent'] = (df['2022']-df['1999'])/df['1999'] #прирост ВВП 1999-2022 год
        df['sum'] = df[cols].sum(axis=1)
        country = df[df['Country']==message.text]
        allvvp = [list(country[col].tolist())[0] for col in cols]
        vvp2022 = country['2022'].tolist()
        vvp1999 = country['1999'].tolist()
        y = ['1999','2022'] 
        dvvp = [vvp1999,vvp2022] 
        top5 = df.nlargest(5, "sum")
        top5countries = list(top5["Country"].tolist())
        top5countries.append(message.text) 
        if top5countries.count(message.text)==2:
            top5countries.remove(message.text)
        df_2 = df[df['Country'].isin(top5countries)] #дф с нашей страной и топ 5 по ср ввп
        vvp = [list(df[df['Country']==i]['sum'].tolist()) for i in top5countries]
        av_vvp = [round(i[0]/22, 1) for i in vvp] #средние ввп по годам у выбранных стран 
        growth = (df_2['percent']*100).tolist()
        res = f'Прирост ВВП с 1999 по 2022: {round(growth[0],1)} %'
        colors = plt.cm.plasma(np.linspace(0, 1, len(top5countries) * 10))  # Увеличение количества шагов
        
        fig, (ax1, ax2) = plt.subplots(2, 1)
        bar_width = 0.7  # Adjust the width as needed
        bars1 = ax1.bar(top5countries, av_vvp, color=colors[::10], width=bar_width)
        ax1.set_title(f'{message.text}\n Среднее ВВП выбранной страны \nпо сравнению с пятёркой лидеров')
        ax1.set_ylabel("ВВП, млрд $")
        ax1.set_xticklabels(top5countries, rotation=45, ha='right')
        for bar, value in zip(bars1, av_vvp):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(value),
                     ha='center', va='bottom')
        bar_width = 0.7  # Adjust the width as needed
        bars2 = ax2.bar(cols, allvvp, color=colors[::10], width=bar_width)
        ax2.set_title('ВВП выбранной страны с 1999 по 2022 года')
        ax2.set_xlabel("Года")
        ax2.set_ylabel("ВВП, млрд $")
        ax2.set_xticklabels(cols, rotation=45, ha='right')
        ax1.set_ylim(bottom=0, top=max(av_vvp) + 5000)
        ax2.set_ylim(bottom=0, top=max(allvvp) + 5000)
        plt.tight_layout()
        plt.savefig('combined_diagrams.png')
        plt.clf()
        bot.send_photo(chat_id, photo=open('combined_diagrams.png', 'rb'), reply_markup=kb)
        os.remove('combined_diagrams.png')

# Обработка команды /help
@bot.message_handler(commands=['/help'])
def handle_help(message):
    bot.reply_to(message, "Список доступных команд:\n/start - начать работу с ботом\n/help - показать список команд\n/choose - выбрать информацию из предложенных вариантов")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):  
    if call.data == '5':
        bot.send_message(call.message.chat.id, text='Чтобы узнать информацию про конкретную страну просто напишите ее название, например: Китай')
    elif call.data == '4':
        try:
            top_5_loss()
            bot.send_photo(call.message.chat.id, photo=open('top5loss.png','rb'), reply_markup=kb)
            os.remove('top5loss.png')
        except:pass

    elif call.data == '3':
        try:
            top_5_worst()
            bot.send_photo(call.message.chat.id, photo=open('top5worst.png','rb'), reply_markup=kb)
            os.remove('top5worst.png')
        except:pass
        
    elif call.data == '1':
        try:
            top_5_growth()
            bot.send_photo(call.message.chat.id, photo=open('top5growth.png','rb'), reply_markup=kb)
            os.remove('top5growth.png')
        except:pass
    elif call.data == '2':
        try:
            top_5_best()
            bot.send_photo(call.message.chat.id, photo=open('top5best.png','rb'), reply_markup=kb)
            os.remove('top5best.png')
        except:pass
    
def top_5_best():
    cols = [str(i) for i in range(1999, 2023) if i != 2011]
    for col in cols:
        df[col] = df[col].astype(float)
    df['sum'] = df[cols].sum(axis=1)
    df_2 = df.nlargest(5, "sum")
    countries = [country.replace('Соединенные Штаты', 'США') for country in df_2["Country"].tolist()]
    vvp = df_2['sum'].tolist()
    av_vvp = [round(i / 22, 1) for i in vvp]
    colors = plt.cm.plasma(np.linspace(0, 1, len(countries) * 10))
    plt.bar(countries, av_vvp, color=colors[::10])
    for i, v in enumerate(av_vvp):
        plt.text(i, v + 0.11, str(v), color='black', ha='center', va='bottom')
    plt.title('Топ 5 стран по среднему ВВП')
    plt.xlabel("Страны")
    plt.ylabel("ВВП, млрд $")
    plt.xticks(countries, rotation=45, ha='right')
    plt.ylim(0, max(av_vvp)+5000)
    plt.tight_layout()
    plt.savefig("top5best.png")
    plt.clf()

def top_5_growth(): #посчитать в процентах
    df['percent'] = (df['2022'] - df['1999']) / df['1999']
    df_2 = df.nlargest(5, 'percent')
    countries = df_2["Country"].tolist()
    growth = df_2['percent'].tolist()
    growth = [i * 100 for i in growth]
    colors = plt.cm.plasma(np.linspace(0, 1, len(countries) * 10))

    plt.bar(countries, growth, color=colors[::10])

    # Добавление подписей сверху столбцов
    for i, v in enumerate(growth):
        plt.text(i, v + 0.1, f"{v:.1f}%", color='black', ha='center', va='bottom')

    plt.title('Топ 5 стран по приросту ВВП', loc='center')
    plt.ylabel("Прирост ВВП в процентах, %")
    plt.xlabel("Страны")
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, max(growth) + 500)
    plt.tight_layout()
    plt.savefig("top5growth.png")
    plt.clf()

def top_5_worst():
    cols = [str(i) for i in range(1999, 2023) if i != 2011]
    for col in cols:
        df[col] = df[col].astype(float)
    df['sum'] = df[cols].sum(axis=1)
    df_2 = df.nsmallest(5, "sum")[::-1]
    countries = [country.replace('Соединенные Штаты', 'США') for country in df_2["Country"].tolist()]
    vvp = df_2['sum'].tolist()
    av_vvp = [round(i / 22, 1) for i in vvp]
    colors = plt.cm.plasma(np.linspace(0, 1, len(countries) * 10))
    bars = plt.bar(countries, av_vvp, color=colors[::10])
    for bar, label in zip(bars, av_vvp):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, f"{label} млрд $",
                 color='black', ha='center', va='bottom')
    plt.ylim(0, max(av_vvp) + 0.5)
    plt.title('Топ 5 стран с наименьшим средним ВВП (по убыванию)')
    plt.xlabel("Страны")
    plt.ylabel("ВВП, млрд $")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig("top5worst.png")
    plt.clf()

def top_5_loss():  #посчитать в процентах
    df['percent'] = (df['2022'] - df['1999']) / df['1999']
    df_2 = df.nsmallest(5, 'percent')[::-1]
    countries = df_2["Country"].tolist()
    growth = df_2['percent'].tolist()
    growth = [i * 100 for i in growth]
    colors = plt.cm.plasma(np.linspace(0, 1, len(countries)))
    bars = plt.bar(countries, growth, color=colors)
    for bar, label in zip(bars, growth):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, f"{label:.1f}%",
                 color='black', ha='center', va='bottom')
    plt.ylim(max(growth) - 200, max(growth) + 200)
    plt.title('Топ 5 худших стран по приросту ВВП (по убыванию)', loc='center')
    plt.ylabel("Прирост ВВП в процентах, %")
    plt.xlabel("Страны")
    plt.xticks(rotation=45, ha='right')  # Вращение названий стран для лучшей читаемости
    plt.tight_layout()
    plt.savefig("top5loss.png")
    plt.clf()

filename = 'GDP_2_result.csv'
df = pd.read_csv(filename)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton('Выбрать действие'))

kb = telebot.types.InlineKeyboardMarkup()
inline_button1 = telebot.types.InlineKeyboardButton('Топ 5 стран по приросту ВВП с 1999 по 2022', callback_data='1')
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
