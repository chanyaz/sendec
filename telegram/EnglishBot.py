import telebot
import psycopg2
import re
from telebot import types
import datetime
"""
Команда Insydia приветствует вас.
Здесь вы можете узнать о последних новостях на нашем портале.
Мы будем поддерживать данное направление и обновлять функционал нашего робота.

Спасибо, что начали пользоваться InsydiaAsiaBot.
"""


TOKEN = "196531742:AAGUaoxgMbin0gAAzOfulW58RPtbECrCkK0"
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
    markup.add('Latest', 'Interest', 'Categories', 'Help')
    welcome_text="""Команда Insydia приветствует вас.
Здесь вы можете узнать о последних новостях на нашем портале.
Мы будем поддерживать данное направление и обновлять функционал нашего робота.

Спасибо, что начали пользоваться InsydiaEnglishBot."""
    bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=markup)


@bot.message_handler(regexp='^Categories$')
def categories(message):
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
    """
    Last N articles of current category
    :param message:
    :return:
    """
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Latest', 'Interest', 'Categories', 'Help')
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
        query_set = "SELECT id, news_title_english, news_post_date, slug, teaser_english FROM news WHERE news_category_id=%s ORDER BY id DESC LIMIT %s"
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
    markup.add('Latest', 'Interest', 'Categories', 'Help')
    try:
        bot.send_message(chat_id=message.chat.id, reply_markup=markup)
    except TypeError:
        pass


@bot.message_handler(regexp='^Last\snews\((T|E|A|S|B)\)$')
def categories_last_one(message):
    """
    Last one article of the current category
    :param message:
    :return:
    """
    markup = types.ReplyKeyboardMarkup(row_width=3,resize_keyboard=True)
    markup.add('Latest', 'Interest', 'Categories', 'Help')
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
    query_set = "SELECT id, news_title_english, news_post_date, slug, teaser_english FROM news WHERE news_category_id=%s ORDER BY id DESC LIMIT 1"
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
    markup.add('Latest', 'Interest', 'Categories', 'Help')
    try:
        bot.send_message(chat_id=message.chat.id, reply_markup=markup)
    except TypeError:
        pass


@bot.message_handler(regexp='^Menu')
def back_to_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=3,resize_keyboard=True)
    markup.add('Latest', 'Interest', 'Categories', 'Help')
    welcome_text="How can I help you?"
    bot.send_message(chat_id=message.chat.id, text=welcome_text, reply_markup=markup)


@bot.message_handler(regexp='^Interest')
def back_to_menu(message):
    """
    Last one interesting article of the current category
    :param message:
    :return:
    """
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Latest', 'Interest', 'Categories', 'Help')
    db = psycopg2.connect(CONNECT_DB)
    cursor = db.cursor()
    query_set = "SELECT  t1.id, t1.news_title_english, t1.news_post_date, t1.slug, t1.teaser_english FROM news t1 INNER JOIN news_watches t2 ON t1.id=t2.news_id ORDER BY t2.watches DESC LIMIT 1"
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


@bot.message_handler(regexp='^Latest')
def back_to_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Latest', 'Interest', 'Categories', 'Help')
    db = psycopg2.connect(CONNECT_DB)
    cursor = db.cursor()
    query_set = "SELECT id, news_title_english, news_post_date, slug, teaser_english FROM news ORDER BY news_post_date DESC LIMIT 1"
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



@bot.message_handler(regexp='[^Technology|Entertainment|Auto|Space|Bio|Menu|Help|Latest|Interest|(Last\snews\((T|E|A|S|B)\))]$')
def unsupported_symbols(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add('Latest', 'Interest', 'Categories', 'Help')
    string="Sorry, I don't understand you."
    bot.send_message(chat_id=message.chat.id, text=string, reply_markup=markup)



bot.polling()
