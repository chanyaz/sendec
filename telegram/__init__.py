import telebot
import psycopg2
import re
from telebot import types

"""
Команда Insydia приветствует вас.
Здесь вы можете узнать о последних новостях на нашем портале.
Мы будем поддерживать данное направление и обновлять функционал нашего робота.

Спасибо, что начали пользоваться InsydiaAsiaBot.
"""


TOKEN = "169868104:AAErdiL_Mq6P0Z-RFnHRdC_SF20ipOui-3o"
bot = telebot.TeleBot(TOKEN)

#DB_NAME = "insydia_main_content_database"
#USER = "eprivalov_db"
#PASSWORD = "InsydiaDBAdministrator192239"

DB_NAME = "test"
USER = "testuser"
PASSWORD = "test"

CONNECT_DB = "dbname='%s' user='%s' host='' password='%s'" % (DB_NAME, USER, PASSWORD)


@bot.message_handler(commands=["rss"])
def current_rss_syndicate(message):
    db = psycopg2.connect(CONNECT_DB)
    cursor = db.cursor()
    query_set = "SELECT id FROM news_rss"
    cursor.execute(query_set)
    count = len(cursor.fetchall())
    bot.send_message(chat_id=message.chat.id, text="Syndicated %s news at this time." % count)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=3,resize_keyboard=True)
    markup.add('Latest', 'Interest', 'Categories', 'Help')
    welcome_text="""Insydia團隊歡迎你。
在這裡，你可以了解我們網站上的最新消息。
我們將保持這個方向和更新我們的機器人的功能。

感謝您開始使用InsydiaAsiaBot"""
    bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=markup)


@bot.message_handler(regexp='^Categories$')
def categories(message):
    # print(message)
    # chat_id = message.chat.id
    # if message.text == 'Categories':
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('Technology', 'Entertainment', 'Auto', 'Space', 'Bio', 'Menu')
    bot.send_message(chat_id=message.chat.id, text="Choose one of the categories below", reply_markup=markup)


@bot.message_handler(regexp='^(Technology|Entertainment|Auto|Space|Bio)$')
def categories(message):

    match = re.findall(r'(Technology|Entertainment|Auto|Space|Bio)', message.text)
    category = match[0]
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('Last news(%s)' % category[0], 'Last 5 news(%s)' % category[0], 'Menu')
    bot.send_message(chat_id=message.chat.id, text="Choose one of the categories below", reply_markup=markup)


@bot.message_handler(regexp='^Last\s[\d]+\snews\((T|E|A|S|B)\)$')
def categories(message):
    cat_dict = {
        "T": 1,    # Technology
        "E": 2,    # Entertainment
        "A": 3,    # Auto
        "S": 4,    # Space
        "B": 5    # Bio
    }
    match = re.findall(r'\d+', message.text)
    match_cat = re.findall(r'\((T|E|A|S|B)\)', message.text)
    amount = match[0]
    cat_letter = match_cat[0]
    if int(amount) > 10:
        bot.send_message(chat_id=message.chat.id, text="1-10")
    else:
        db = psycopg2.connect(CONNECT_DB)
        cursor = db.cursor()
        query_set = "SELECT news_category_id, id, news_title_english FROM news WHERE news_category_id=%s ORDER BY id DESC LIMIT %s"
        cat_id = cat_dict[cat_letter]
        data_query_set = (cat_id, amount,)
        cursor.execute(query_set, data_query_set)
        item = cursor.fetchall()
        for i in range(len(item)):
            string = "%s\nhttps://insydia.com/news/%s/%s/" % (item[i][2], item[i][0], item[i][1])
            bot.send_message(chat_id=message.chat.id, text=string)
    markup = types.ReplyKeyboardMarkup(row_width=3,resize_keyboard=True)
    markup.add('Latest', 'Interest', 'Categories', 'Help')
    welcome_text="""Insydia團隊歡迎你。
在這裡，你可以了解我們網站上的最新消息。
我們將保持這個方向和更新我們的機器人的功能。

感謝您開始使用InsydiaAsiaBot"""
    bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=markup)


@bot.message_handler(regexp='^Last\snews\((T|E|A|S|B)\)$')
def categories_last_one(message):
    cat_dict = {
        "T": 1,    # Technology
        "E": 2,    # Entertainment
        "A": 3,    # Auto
        "S": 4,    # Space
        "B": 5    # Bio
    }
    match_cat = re.findall(r'\((T|E|A|S|B)\)', message.text)
    cat_letter = match_cat[0]
    db = psycopg2.connect(CONNECT_DB)
    cursor = db.cursor()
    query_set = "SELECT news_category_id, id, news_title_english FROM news WHERE news_category_id=%s ORDER BY id DESC LIMIT 1"
    cat_id = cat_dict[cat_letter]
    data_query_set = (cat_id,)
    cursor.execute(query_set, data_query_set)
    item = cursor.fetchall()
    for i in range(len(item)):
        string = "%s\nhttps://insydia.com/news/%s/%s/" % (item[i][2], item[i][0], item[i][1])
        bot.send_message(chat_id=message.chat.id, text=string)
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Latest', 'Interest', 'Categories', 'Help')
    welcome_text="""Insydia團隊歡迎你。
在這裡，你可以了解我們網站上的最新消息。
我們將保持這個方向和更新我們的機器人的功能。

感謝您開始使用InsydiaAsiaBot"""
    bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=markup)


@bot.message_handler(regexp='^Menu$')
def back_to_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=3,resize_keyboard=True)
    markup.add('Latest', 'Interest', 'Categories', 'Reviews', 'Help')
    welcome_text="""Insydia團隊歡迎你。
在這裡，你可以了解我們網站上的最新消息。
我們將保持這個方向和更新我們的機器人的功能。

感謝您開始使用InsydiaAsiaBot"""
    bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=markup)


@bot.message_handler(regexp='^Interest$')
def back_to_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Latest', 'Interest', 'Categories', 'Help')
    db = psycopg2.connect(CONNECT_DB)
    cursor = db.cursor()
    query_set = "SELECT news_id, news_title_english, news_category_id FROM news t1 INNER JOIN news_watches t2 ON t1.id=t2.news_id ORDER BY t2.watches DESC LIMIT 1"
    # data_query_set = [amount]
    cursor.execute(query_set)
    db.commit()
    item = cursor.fetchall()
    string = "%s\nhttps://insydia.com/%s/%s/" % (item[0][1], item[0][2], item[0][0])
    bot.send_message(chat_id=message.chat.id, text=string, reply_markup=markup)


@bot.message_handler(regexp='^Latest$')
def back_to_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Latest', 'Interest', 'Categories', 'Help')
    db = psycopg2.connect(CONNECT_DB)
    cursor = db.cursor()
    query_set = "SELECT id, news_title_english, news_category_id FROM news ORDER BY news_post_date DESC LIMIT 1"
    # data_query_set = [amount]
    cursor.execute(query_set)
    db.commit()
    item = cursor.fetchall()
    string = "%s\nhttps://insydia.com/%s/%s/" % (item[0][1], item[0][2], item[0][0])
    bot.send_message(chat_id=message.chat.id, text=string, reply_markup=markup)


@bot.message_handler(regexp='^Help$')
def help_menu(message):
    """
    Help menu
    :param message:
    :return:
    """
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Menu')
    string = """If you have any problems, you can write to support@insydia.com. We will be very glad to help you and
may be tell something interesting.

Also, you can write to advert@insydia.com for the advertisement questions. Let's cooperate and give all news from IT industry all over the World.

Insydia Team
https://insydia.com
"""
    bot.send_message(chat_id=message.chat.id, text=string, reply_markup=markup)



bot.polling()
