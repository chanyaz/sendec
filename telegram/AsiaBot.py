# Telegram bot of Insydia
# Strategic region is Eastern Asia


import telebot
import psycopg2
import re
from telebot import types
import datetime

TOKEN = "203797866:AAFcbifaNX7q_UTvjaoOSz4VVC6MM95tanI"
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
    markup.add('最新', '利益', '分類', '幫幫我')
    welcome_text="""Insydia團隊歡迎你.
在這裡，你可以了解我們網站上的最新消息.
我們將保持這個方向和更新我們的機器人的功能.

感謝您開始使用InsydiaAsiaBot"""
    bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=markup)


@bot.message_handler(regexp='^分類$')
def categories(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('技術類', '娛樂', '娱乐', '太空', '生物材料', '菜單')
    bot.send_message(chat_id=message.chat.id, text="Choose one of the categories below", reply_markup=markup)


@bot.message_handler(regexp='^(技術類|娛樂|娱乐|太空|生物材料)$')
def categories(message):
    match = re.findall(r'(技術類|娛樂|娱乐|太空|生物材料)', message.text)
    category = match[0]
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('最後新聞(%s)' % category, '最近5新聞(%s)' % category, '菜單')
    bot.send_message(chat_id=message.chat.id, text="Choose one of the categories below", reply_markup=markup)


@bot.message_handler(regexp='^最近[\d]+新聞\((技術類|娛樂|娱乐|太空|生物材料)\)$')
def categories(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('最新', '利益', '分類', '幫幫我')
    cat_dict = {
        "技術類": 1,    # Technology
        "娛樂": 2,    # Entertainment
        "娱乐": 3,    # Auto
        "太空": 4,    # Space
        "生物材料": 5    # Bio
    }
    match = re.findall(r'\d+', message.text)
    match_cat = re.findall(r'\((技術類|娛樂|娱乐|太空|生物材料)\)', message.text)
    amount = match[0]
    cat_letter = match_cat[0]
    if int(amount) > 10:
        bot.send_message(chat_id=message.chat.id, text="1-10")
    else:
        db = psycopg2.connect(CONNECT_DB)
        cursor = db.cursor()
        query_set = "SELECT id, news_title_chinese, news_post_date, slug, teaser_chinese FROM news WHERE news_category_id=%s ORDER BY id DESC LIMIT %s"
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
    markup.add('最新', '利益', '分類', '幫幫我')
    try:
        bot.send_message(chat_id=message.chat.id, reply_markup=markup)
    except TypeError:
        pass


@bot.message_handler(regexp='^最後新聞\((技術類|娛樂|娱乐|太空|生物材料)\)$')
def categories_last_one(message):
    markup = types.ReplyKeyboardMarkup(row_width=3,resize_keyboard=True)
    markup.add('最新', '利益', '分類', '幫幫我')
    cat_dict = {
        "技術類": 1,    # Technology
        "娛樂": 2,    # Entertainment
        "娱乐": 3,    # Auto
        "太空": 4,    # Space
        "生物材料": 5    # Bio
    }
    match_cat = re.findall(r'\((技術類|娛樂|娱乐|太空|生物材料)\)', message.text)
    cat_letter = match_cat[0]
    db = psycopg2.connect(CONNECT_DB)
    cursor = db.cursor()
    query_set = "SELECT id, news_title_chinese, news_post_date, slug, teaser_chinese FROM news WHERE news_category_id=%s ORDER BY id DESC LIMIT 1"
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
    markup.add('最新', '利益', '分類', '幫幫我')
    try:
        bot.send_message(chat_id=message.chat.id, reply_markup=markup)
    except TypeError:
        pass


@bot.message_handler(regexp='^菜單$')
def back_to_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=3,resize_keyboard=True)
    markup.add('最新', '利益', '分類', '幫幫我')
    welcome_text="我有什麼可以幫您"
    bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=markup)


@bot.message_handler(regexp='^利益$')
def back_to_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('最新', '利益', '分類', '幫幫我')
    db = psycopg2.connect(CONNECT_DB)
    cursor = db.cursor()
    query_set = "SELECT  t1.id, t1.news_title_chinese, t1.news_post_date, t1.slug, t1.teaser_chinese FROM news t1 INNER JOIN news_watches t2 ON t1.id=t2.news_id ORDER BY t2.watches DESC LIMIT 1"
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


@bot.message_handler(regexp='^最新$')
def back_to_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('最新', '利益', '分類', '幫幫我')
    db = psycopg2.connect(CONNECT_DB)
    cursor = db.cursor()
    query_set = "SELECT id, news_title_chinese, news_post_date, slug, teaser_chinese FROM news ORDER BY news_post_date DESC LIMIT 1"
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


@bot.message_handler(regexp='^幫幫我$')
def help_menu(message):
    """
    Help menu
    :param message:
    :return:
    """
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('菜單')
    string = """If you have any problems, you can write to support@insydia.com. We will be very glad to help you and
may be tell something interesting.

Also, you can write to advert@insydia.com for the advertisement questions. Let's cooperate and give all news from IT industry all over the World.

Insydia Team
https://insydia.com
"""
    bot.send_message(chat_id=message.chat.id, text=string, reply_markup=markup)


@bot.message_handler(regexp='[^最新|利益|分類|幫幫我|菜單|技術類|娛樂|娱乐|太空|生物材料]$')
def unsupported_symbols(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('最新', '利益', '分類', '幫幫我')
    string="我不明白你"
    bot.send_message(chat_id=message.chat.id, text=string, reply_markup=markup)


bot.polling()
