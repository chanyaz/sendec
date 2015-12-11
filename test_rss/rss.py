import feedparser
import sqlite3
import datetime, time

db = sqlite3.connect("/home/eprivalov/PycharmProjects/sendec/sendec/db.sqlite3")
cursor = db.cursor()
id = 1
news_title = "Test news"
news_category_id = 1
news_post_date = datetime.datetime.now()
news_post_text = "Test news text"
news_post_text_translate = "Test news text translate"
news_portal_name_id = 1
news_company_owner_id = 1
news_author_id = 1
news_main_cover = ""
news_likes = 0
news_dislikes = 0
cursor.execute("INSERT INTO news(news_title, news_category_id, news_post_date, news_post_text, news_post_text_translate, news_portal_name_id, news_company_owner_id, news_author_id, news_main_cover, news_likes, news_dislikes) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (news_title, news_category_id, news_post_date, news_post_text, news_post_text_translate, news_portal_name_id, news_company_owner_id, news_author_id, news_main_cover, news_likes, news_dislikes))
db.commit()
db.close()

def get_feed_urls():
    with open("rssurls.txt", "r") as file:
        url_feeds = file.readlines()

    for i in range(len(url_feeds)):
        url_feeds[i] = url_feeds[i][:-1]
    return url_feeds


def parse_current_url(url=''):
    url_parse = feedparser.parse(url)
    return [i for i in url_parse.entries]


def last_element(feed):
    args = {"title": feed[0].title, "date": feed[0].published, "description": feed[0].description,
            "link": feed[0].link, "main_cover": ""}

    #print(feed[0].keys())
    keys = feed[0].keys()

    # AUTHOR
    if "author" in keys: args["author"] = feed[0].author
    else: args["author"] = ""
    # CONTENT
    if "content" in keys: args["content"] = feed[0].content[0]["value"]
    else: args["content"] = ""

    return args


def connect_to_db(urls):
    #urls = ["http://appleinsider.ru/feed"]

    db = sqlite3.connect("/home/eprivalov/PycharmProjects/sendec/sendec/db.sqlite3")
    #db = sqlite3.connect("C:\\Users\\eprivalov\\PycharmProjects\\sendec\\sendec\\db.sqlite3")
    cursor = db.cursor()
    for url in urls:
        #print(url)
        data = last_element(parse_current_url(url=url))
        new_date = data["date"].split()
        time = new_date[4].split(":")
        cursor.execute("SELECT rowid FROM news_rss WHERE link=?", [data["link"]])
        count = cursor.fetchall()

        import re
        match_2 = re.findall(r'src=(.*?)\s.*/>', data["content"])
        if len(match_2) >= 1:
            data["main_cover"] = str(match_2[0])
        else:
            data["main_cover"] = str(match_2)

        data["content"] = data["content"].replace('"', '').replace("\xa0", "").replace("%", "%%").replace("> ", ">").replace(" </", "</").replace(" <", "<").replace("\n<", "<").replace("\n", " ").replace("'", "&rsquo;")
        data["description"] = data["description"].replace('"', '&#quot;').replace("\xa0", "").replace("%", "%%").replace("> ", ">").replace(" </", "</").replace(" <", "<").replace("\n<", "<").replace("\n", " ").replace("'", "&rsquo;")
        match = re.findall(r'<.*?>', data["description"])
        for i in match:
            data["description"] = data["description"].replace(i, "")
        data["description"] = data["description"].replace("\n", "")



        if len(count) == 0:
            cursor.execute("""INSERT INTO news_rss(title, date_posted, post_text, link, portal_name_id, category_id, content_value, author) VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",(data["title"], datetime.datetime(int(new_date[3]), 11, int(new_date[1]), int(time[0]), int(time[1]), int(time[2])), data["description"], data["link"], 1, 1, data["content"], data["author"]))

            cursor.execute("SELECT rowid FROM news_rss WHERE title=?", [data["title"]])
            current_rss_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO rss_news_covers(rss_news_id, main_cover) VALUES (?, ?)", (int(current_rss_id), data["main_cover"]))

            db.commit()
            print("Inserted from: ", url)
        else:
            print("Already exists: ", url)
    print("================END ONE MORE LOOP====================")
    db.close()

#while True:
#last_element(parse_current_url(url="http://appleinsider.ru/feed/"))
#print(last_element(parse_current_url(url="http://appleinsider.ru/feed/")))
#    connect_to_db(urls=urls_of_portals)
#    time.sleep(1)

def fill_rss_table():
    import json


    db = sqlite3.connect("/home/eprivalov/PycharmProjects/sendec/sendec/db.sqlite3")
    #db = sqlite3.connect("C:\\Users\\eprivalov\\PycharmProjects\\sendec\\sendec\\db.sqlite3")
    cursor = db.cursor()

    with open("dictionary_portals.json") as json_file_list:
        json_data_list = list(json.load(json_file_list))
    with open("dictionary_portals.json") as json_file:
        json_data = json.load(json_file)

    print(json_data[json_data_list[0]])

    cursor.execute("SELECT * FROM rss_portals")
    list_cur = cursor.fetchall()

    cursor.execute("SELECT * FROM news_rss")
    rss = cursor.fetchall()
    #print(rss[2][0])



    end = len(rss)*len(list_cur)
    cur_iter = 0
    for i in range(len(rss)):
        for j in range(len(list_cur)):
            cur_iter += 1
            if str(list_cur[j][2]) in str(rss[i][6]):
                id = str(rss[i][0])
                cursor.execute("UPDATE news_rss SET portal_name_id=? WHERE id=?", (str(list_cur[j][0]), id))
                db.commit()
                print("Iter #", cur_iter, "Complete..........", cur_iter/end*100, "%", "When total end is ", end)
            else:
                continue
    db.close()

#fill_rss_table()


def fill_rss_portals():
    import json
    db = sqlite3.connect("/home/eprivalov/PycharmProjects/sendec/sendec/db.sqlite3")
    #db = sqlite3.connect("C:\\Users\\eprivalov\\PycharmProjects\\sendec\\sendec\\db.sqlite3")
    cursor = db.cursor()
    with open("dictionary_portals.json") as file_list:
        file_list = list(json.load(file_list))
    with open("dictionary_portals.json") as file:
        portals = json.load(file)
    end = len(portals)
    cur_iter = 0
    cursor.execute("SELECT portal_name FROM news_portal")
    list_portals = cursor.fetchall()
    for i in range(len(portals)):
        cur_iter += 1
        cursor.execute("INSERT INTO rss_portals(portal, portal_base_link, follows) VALUES(?, ?, ?)", (portals[file_list[i]]["name"], portals[file_list[i]]["base_link"], 0))
        db.commit()
        print("Iter #", cur_iter, "Complete..........", cur_iter/end*100, "%", "When total end is ", end)
    db.close()

#fill_rss_portals()


def work_func():
    urls_of_portals = get_feed_urls()
    print("1. Syndicate news\n2.Fill Rss Portals\n3.Update rss-news portals")
    x = int(input("What can I help you? Enter number: "))
    if x == 1:
        while True:
            try:
                connect_to_db(urls=urls_of_portals)
            except IndexError:
                break
    elif x == 2:
        fill_rss_portals()
    elif x == 3:
        fill_rss_table()
    else:
        pass
while True:
    work_func()
