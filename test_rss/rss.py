import feedparser
import sqlite3, psycopg2
import datetime, time
import os

def fill_start_data_news():
    #db = sqlite3.connect(BASE_DIR+"\\db.sqlite3")
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
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
    query = """INSERT INTO news(news_title, news_category_id, news_post_date, news_post_text, news_post_text_translate, news_portal_name_id, news_company_owner_id, news_author_id, news_main_cover, news_likes, news_dislikes) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    data_query = (news_title, news_category_id, news_post_date, news_post_text, news_post_text_translate, news_portal_name_id, news_company_owner_id, news_author_id, news_main_cover, news_likes, news_dislikes)
    cursor.execute(query, data_query)
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
    args = {"title": feed[0].title, "link": feed[0].link, "main_cover": ""}
    keys = feed[0].keys()
    # AUTHOR
    if "author" in keys: args["author"] = feed[0].author
    else: args["author"] = ""
    # CONTENT
    if "content" in keys: args["content"] = feed[0].content[0]["value"]
    else: args["content"] = ""
    # DATE
    if "date" in keys: args["date"] = feed[0].published
    else: args["date"] = feed[0].published
    # DESCRIPTION
    if "description" in keys: args["description"] = feed[0].description
    else: args["description"] = feed[0]['summary_detail']['value']
    return args


def connect_to_db(urls):
    #db = sqlite3.connect(BASE_DIR+"\\db.sqlite3")
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()
    for url in urls:
        data = last_element(parse_current_url(url=url))
        new_date = data["date"].split()
        time = new_date[4].split(":")
        query_0 = "SELECT ID FROM news_rss WHERE link=%s"
        data_query_0 = [data["link"]]
        cursor.execute(query_0, data_query_0)
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
            #cursor.execute("""INSERT INTO news_rss(title, date_posted, post_text, link, portal_name_id, category_id, content_value, author) VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",(data["title"], datetime.datetime(int(new_date[3]), 11, int(new_date[1]), int(time[0]), int(time[1]), int(time[2])), data["description"], data["link"], 1, 1, data["content"], data["author"]))
            query = """INSERT INTO news_rss(title, date_posted, post_text, link, portal_name_id, category_id, content_value, author) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
            data_query = (data["title"], datetime.datetime(int(new_date[3]), 11, int(new_date[1]), int(time[0]), int(time[1]), int(time[2])), data["description"], data["link"], 1, 1, data["content"], data["author"])
            cursor.execute(query, data_query)
            query_2 = "SELECT ID FROM news_rss WHERE title=%s"
            data_query_2 = [data["title"]]
            cursor.execute(query_2, data_query_2)
            current_rss_id = cursor.fetchone()[0]
            query_3 = "INSERT INTO rss_news_covers(rss_news_id, main_cover) VALUES (%s, %s)"
            data_query_3 = (int(current_rss_id), data["main_cover"])
            cursor.execute(query_3, data_query_3)
            db.commit()
            print("Inserted from: ", url)
        else:
            print("Already exists: ", url)
    print("================END ONE MORE LOOP====================")
    db.close()


def fill_rss_table():
    import json
    #db = sqlite3.connect(BASE_DIR+"\\db.sqlite3")
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()
    with open("dictionary_portals.json", encoding="utf-8-sig") as json_file_list:
        json_data_list = list(json.load(json_file_list))
    with open("dictionary_portals.json", encoding="utf-8-sig") as json_file:
        json_data = json.load(json_file)
    query_0 = "SELECT * FROM rss_portals"
    cursor.execute(query_0)
    list_cur = cursor.fetchall()
    query_1 = "SELECT * FROM news_rss"
    cursor.execute(query_1)
    rss = cursor.fetchall()
    end = len(rss)*len(list_cur)
    cur_iter = 0
    for i in range(len(rss)):
        for j in range(len(list_cur)):
            cur_iter += 1
            if str(list_cur[j][2]) in str(rss[i][6]):
                id = str(rss[i][0])
                query = "UPDATE news_rss SET portal_name_id=%s WHERE id=%s"
                data_query = (str(list_cur[j][0]), id)
                cursor.execute(query, data_query)
                db.commit()
                print("Iter #", cur_iter, "Complete..........", cur_iter/end*100, "%", "When total end is ", end)
            else:
                continue
    db.close()


def fill_rss_portals():
    import json
    #db = sqlite3.connect(BASE_DIR+"\\db.sqlite3")
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()
    with open("dictionary_portals.json", encoding="utf-8-sig") as file_list:
        file_list = list(json.load(file_list))
    with open("dictionary_portals.json", encoding="utf-8-sig") as file:
        portals = json.load(file)
    end = len(portals)
    cur_iter = 0
    query_0 = "SELECT portal_name FROM news_portal"
    cursor.execute(query_0)
    list_portals = cursor.fetchall()
    for i in range(len(portals)):
        cur_iter += 1
        query = "INSERT INTO rss_portals(portal, portal_base_link, follows) VALUES(%s, %s, %s)"
        data_query = (portals[file_list[i]]["name"], portals[file_list[i]]["base_link"], 0)
        cursor.execute(query,data_query)
        db.commit()
        print("Iter #", cur_iter, "Complete..........", cur_iter/end*100, "%", "When total end is ", end)
    db.close()


def work_func():
    urls_of_portals = get_feed_urls()
    print("1. Fill Rss Portals\n2. Syndicate news")
    x = int(input("What can I help you? Enter number: "))
    if x == 1:
        fill_rss_portals()
    elif x == 2:
        while True:
            try:
                connect_to_db(urls=urls_of_portals)
                time.sleep(1)
            except IndexError:
                pass
    else:
        import sys
        print("Good bye!")
        sys.exit(0)

#fill_start_data_news()
while True:
    work_func()