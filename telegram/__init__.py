import telebot
import psycopg2
import re
import time

TOKEN = "169868104:AAErdiL_Mq6P0Z-RFnHRdC_SF20ipOui-3o"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(regexp="dollar")
def dollar_price(message):
    bot.send_message(chat_id=message.chat.id, text="Dollar price is dohuya")


@bot.message_handler(regexp="^/lastnews$")
def last_news(message):
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()
    query_set = "SELECT * FROM news ORDER BY id DESC LIMIT 1"
    cursor.execute(query_set)
    db.commit()
    item = cursor.fetchall()
    string = "https://www.insydia.com/news/%s/%s/" % (item[0][2], item[0][0])
    bot.send_message(chat_id=message.chat.id, text=string)


@bot.message_handler(regexp="me")
def show_me(message):
    bot.send_message(chat_id=message.chat.id, text=message.chat.id)


@bot.message_handler(commands=["interest_link"])
def get_interest_news(message):
    try:
        db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
        cursor = db.cursor()
        query_set = "SELECT * FROM news t1 INNER JOIN news_watches t2 ON t1.id=t2.news_id ORDER BY t2.watches DESC LIMIT 1"
        # data_query_set = [amount]
        cursor.execute(query_set)
        db.commit()
        item = cursor.fetchall()
        string = "https://insydia.com/%s/%s/" % (item[0][2], item[0][0])
        bot.send_message(chat_id=message.chat.id, text=string)
    except:
        pass


@bot.message_handler(commands=["interest_text"])
def get_interest_news(message):
    try:
        db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
        cursor = db.cursor()
        query_set = "SELECT * FROM news t1 INNER JOIN news_watches t2 ON t1.id=t2.news_id ORDER BY t2.watches DESC LIMIT 1"
        # data_query_set = [amount]
        cursor.execute(query_set)
        db.commit()
        item = cursor.fetchall()
        print(item[0][5])
        import re
        match = re.findall(r'<.*?>', item[0][5])
        for i in match:
            string = item[0][5].replace(i, '')
        bot.send_message(chat_id=message.chat.id, text=string)
    except:
        pass


@bot.message_handler(regexp="^last \d+ news$")
def last_news_2(message):
    match = re.findall(r'\d+', message.text)
    amount = match[0]
    if int(amount) > 10:
        bot.send_message(chat_id=message.chat.id, text="Command: 'last <number> news'\n <number> - number from 1 to 10\nFor example: 'last 7 news'")
    else:
        db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
        cursor = db.cursor()
        query_set = "SELECT news_category_id, id FROM news ORDER BY id DESC LIMIT %s"
        data_query_set = [amount]
        cursor.execute(query_set, data_query_set)
        db.commit()
        item = cursor.fetchall()
        for i in range(len(item)):
            # string = "http://insydia.com/news/%s/%s/" % (item[i][0], item[i][1])
            string = "https://insydia.com/news/4/1/"
            bot.send_message(chat_id=message.chat.id, text=string)


def check_user(username):
    print(username)
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()
    query_set = "SELECT COUNT(username) FROM auth_user WHERE auth_user.username=%s"
    data_query_set = [username]
    cursor.execute(query_set, data_query_set)

    a = cursor.fetchall()[0][0]
    print(a)

    if a == 1:
        return True
    else:
        return False


@bot.message_handler(commands=["rss"])
def current_rss_syndicate(message):
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()
    query_set = "SELECT id FROM news_rss"
    cursor.execute(query_set)
    count = len(cursor.fetchall())
    bot.send_message(chat_id=message.chat.id, text="Syndicated %s news at this time." % count)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(chat_id=message.chat.id, text="Insydia welcomes you! Send your <username> from web-site to confirmation.")
    @bot.message_handler(regexp="^\w+$")
    def get_username(message):
        if check_user(message.text) == True:
            bot.send_message(chat_id=message.chat.id, text="Confirmation complete. Thank you.")

bot.polling()
