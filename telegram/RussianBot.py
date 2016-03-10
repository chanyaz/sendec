# Telegram bot of Insydia
# Strategic region is Eastern Asia


import telebot
import psycopg2
import re
from telebot import types
import datetime

TOKEN = "186702512:AAF_cBNESXW4E8zGMKu-p4HDoblUxy0LTLw"
bot = telebot.TeleBot(TOKEN)

#DB_NAME = "insydia_main_content_database"
#USER = "eprivalov_db"
#PASSWORD = "InsydiaDBAdministrator192239"

DB_NAME = "test"
USER = "testuser"
PASSWORD = "test"

CONNECT_DB = "dbname='%s' user='%s' host='' password='%s'" % (DB_NAME, USER, PASSWORD)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=3,resize_keyboard=True)
    markup.add('Последнее', 'Интересное', 'Категории', 'Помощь')
    welcome_text="""Команда Insydia приветствует вас.
Здесь вы можете узнать о последних новостях на нашем портале.
Мы будем поддерживать данное направление и обновлять функционал нашего робота.

Спасибо, что начали пользоваться InsydiaRussianBot."""
    bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=markup)


@bot.message_handler(regexp='^Категории$')
def categories(message):
    """
    Categories menu
    :param message:
    :return:
    """
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('Технологии', 'Развлечения', 'Авто', 'Космос', 'Био', 'Меню')
    bot.send_message(chat_id=message.chat.id, text="Выберие одну из предложенных ниже категорий", reply_markup=markup)


@bot.message_handler(regexp='^(Технологии|Развлечения|Авто|Космос|Био)$')
def categories(message):
    match = re.findall(r'(Технологии|Развлечения|Авто|Космос|Био)', message.text)
    category = match[0]
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('Последнее(%s)' % category[0], 'Последние 5(%s)' % category[0], 'Меню')
    bot.send_message(chat_id=message.chat.id, text="Выберите количество новостей", reply_markup=markup)


@bot.message_handler(regexp='^Последние\s[\d]+\((Т|Р|А|К|Б)\)$')
def categories(message):
    """
    Last N articles of current category
    :param message:
    :return:
    """
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Последнее', 'Интересное', 'Категории', 'Помощь')
    cat_dict = {
        "Т": 1,    # Technology
        "Р": 2,    # Entertainment
        "А": 3,    # Auto
        "К": 4,    # Space
        "Б": 5    # Bio
    }
    match = re.findall(r'\d+', message.text)
    match_cat = re.findall(r'\((Т|Р|А|К|Б)\)', message.text)
    amount = match[0]
    cat_letter = match_cat[0]
    if int(amount) > 10:
        bot.send_message(chat_id=message.chat.id, text="1-10")
    else:
        db = psycopg2.connect(CONNECT_DB)
        cursor = db.cursor()
        query_set = "SELECT id, news_title_russian, news_post_date, slug, teaser_russian FROM news WHERE news_category_id=%s ORDER BY id DESC LIMIT %s"
        cat_id = cat_dict[cat_letter]
        data_query_set = (cat_id, amount,)
        cursor.execute(query_set, data_query_set)
        item = cursor.fetchall()
        for i in range(len(item)):
            date = datetime.date.isoformat(item[0][2]).split('-')
            article = types.InlineQueryResultArticle(title="*%s*" % item[i][1],
                                                     message_text="%s" % item[i][4],
                                                     url="https://insydia.com/news/{year}/{month}/{day}/{id}/{slug}/".format(year=int(date[0]),
                                                                                                            month=int(date[1]),
                                                                                                            day=int(date[2]),
                                                                                                            id=item[i][0],
                                                                                                            slug=item[i][3]),
                                                     id=message.chat.id)
            try:
                bot.send_message(chat_id=message.chat.id,
                                 reply_markup=markup,
                                 text=article.title+"\n"+article.message_text+"\n"+article.url,
                                 parse_mode="Markdown")
            except TypeError:
                pass
    markup = types.ReplyKeyboardMarkup(row_width=3,resize_keyboard=True)
    markup.add('Последнее', 'Интересное', 'Категории', 'Помощь')
    try:
        bot.send_message(chat_id=message.chat.id, reply_markup=markup)
    except TypeError:
        pass


@bot.message_handler(regexp='^Последнее\((Т|Р|А|К|Б)\)$')
def categories_last_one(message):
    """
    Last one article of the current category
    :param message:
    :return:
    """
    markup = types.ReplyKeyboardMarkup(row_width=3,resize_keyboard=True)
    markup.add('Последнее', 'Интересное', 'Категории', 'Помощь')
    cat_dict = {
        "Т": 1,    # Technology
        "Р": 2,    # Entertainment
        "А": 3,    # Auto
        "К": 4,    # Space
        "Б": 5    # Bio
    }
    match_cat = re.findall(r'\((Т|Р|А|К|Б)\)', message.text)
    cat_letter = match_cat[0]
    db = psycopg2.connect(CONNECT_DB)
    cursor = db.cursor()
    query_set = "SELECT id, news_title_russian, news_post_date, slug, teaser_russian FROM news WHERE news_category_id=%s ORDER BY id DESC LIMIT 1"
    cat_id = cat_dict[cat_letter]
    data_query_set = (cat_id,)
    cursor.execute(query_set, data_query_set)
    item = cursor.fetchall()
    for i in range(len(item)):
        date = datetime.date.isoformat(item[0][2]).split('-')
        article = types.InlineQueryResultArticle(title="*%s*" % item[0][1],
                                                 message_text="%s" % item[0][4],
                                                 url="https://insydia.com/news/{year}/{month}/{day}/{id}/{slug}/".format(year=int(date[0]),
                                                                                                        month=int(date[1]),
                                                                                                        day=int(date[2]),
                                                                                                        id=item[0][0],
                                                                                                        slug=item[0][3]),
                                                 id=message.chat.id)
        try:
            bot.send_message(chat_id=message.chat.id,
                             reply_markup=markup,
                             text=article.title+"\n"+article.message_text+"\n"+article.url,
                             parse_mode="Markdown")
        except TypeError:
            pass
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Последнее', 'Интересное', 'Категории', 'Помощь')
    try:
        bot.send_message(chat_id=message.chat.id, reply_markup=markup)
    except TypeError:
        pass


@bot.message_handler(regexp='^Меню$')
def back_to_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=3,resize_keyboard=True)
    markup.add('Последнее', 'Интересное', 'Категории', 'Помощь')
    welcome_text="Чем я могу вам помочь?"
    bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=markup)


@bot.message_handler(regexp='^Интересное$')
def back_to_menu(message):
    """
    Last one interesting article of the current category
    :param message:
    :return:
    """
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Последнее', 'Интересное', 'Категории', 'Помощь')
    db = psycopg2.connect(CONNECT_DB)
    cursor = db.cursor()
    query_set = "SELECT  t1.id, t1.news_title_russian, t1.news_post_date, t1.slug, t1.teaser_russian FROM news t1 INNER JOIN news_watches t2 ON t1.id=t2.news_id ORDER BY t2.watches DESC LIMIT 1"
    # data_query_set = [amount]
    cursor.execute(query_set)
    item = cursor.fetchall()
    date = datetime.date.isoformat(item[0][2]).split('-')
    article = types.InlineQueryResultArticle(title="*%s*" % item[0][1],
                                             message_text="%s" % item[0][4],
                                             url="https://insydia.com/news/{year}/{month}/{day}/{id}/{slug}/".format(year=int(date[0]),
                                                                                                    month=int(date[1]),
                                                                                                    day=int(date[2]),
                                                                                                    id=item[0][0],
                                                                                                    slug=item[0][3]),
                                             id=message.chat.id)
    try:
        bot.send_message(chat_id=message.chat.id,
                         reply_markup=markup,
                         text=article.title+"\n"+article.message_text+"\n"+article.url,
                         parse_mode="Markdown")
    except TypeError:
        pass


@bot.message_handler(regexp='^Последнее$')
def back_to_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Последнее', 'Интересное', 'Категории', 'Помощь')
    db = psycopg2.connect(CONNECT_DB)
    cursor = db.cursor()
    query_set = "SELECT id, news_title_russian, news_post_date, slug, teaser_russian FROM news ORDER BY news_post_date DESC LIMIT 1"
    cursor.execute(query_set)
    item = cursor.fetchall()
    date = datetime.date.isoformat(item[0][2]).split('-')
    article = types.InlineQueryResultArticle(title="*%s*" % item[0][1],
                                             message_text="%s" % item[0][4],
                                             url="https://insydia.com/news/{year}/{month}/{day}/{id}/{slug}/".format(year=int(date[0]),
                                                                                                    month=int(date[1]),
                                                                                                    day=int(date[2]),
                                                                                                    id=item[0][0],
                                                                                                    slug=item[0][3]),
                                             id=message.chat.id)
    try:
        bot.send_message(chat_id=message.chat.id,
                         reply_markup=markup,
                         text=article.title+"\n"+article.message_text+"\n"+article.url,
                         parse_mode="Markdown")
    except TypeError:
        pass


@bot.message_handler(regexp='^Помощь')
def help_menu(message):
    """
    Help menu
    :param message:
    :return:
    """
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Меню')
    string = """If you have any problems, you can write to support@insydia.com. We will be very glad to help you and
may be tell something interesting.

Also, you can write to advert@insydia.com for the advertisement questions. Let's cooperate and give all news from IT industry all over the World.

Insydia Team
https://insydia.com
"""
    bot.send_message(chat_id=message.chat.id, text=string, reply_markup=markup)


@bot.message_handler(regexp='[^Технологии|Развлечения|Авто|Космос|Био|Меню|Помощь|Последнее|Интересное|(Последнее\((Т|Р|А|К|Б)\))]$')
def unsupported_symbols(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Последнее', 'Интересное', 'Категории', 'Помощь')
    string="Простите, я вас не понимаю."
    bot.send_message(chat_id=message.chat.id, text=string, reply_markup=markup)


bot.polling()
