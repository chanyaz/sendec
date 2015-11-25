import feedparser
import sqlite3
import datetime, time

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
    return {"title": feed[0].title, "date": feed[0].published, "description": feed[0].description, "link": feed[0].link}


def connect_to_db(urls):
    #urls = ["http://appleinsider.ru/feed"]
    for url in urls:
        db = sqlite3.connect("/home/eprivalov/PycharmProjects/sendec/db.sqlite3")
        cursor = db.cursor()
        #print(url)
        data = last_element(parse_current_url(url=url))
        new_date = data["date"].split()
        time = new_date[4].split(":")
        cursor.execute("SELECT rowid FROM news_rss WHERE link=?", [data["link"]])
        count = cursor.fetchall()
        if len(count) == 0:
            cursor.execute("""INSERT INTO news_rss(title, date_posted, post_text, link, portal_name_id, category_id) VALUES(?, ?, ?, ?, ?, ?)""",(data["title"], datetime.datetime(int(new_date[3]), 11, int(new_date[1]), int(time[0]), int(time[1]), int(time[2])), data["description"], data["link"], 1, 1))
            db.commit()
            db.close()
            print("Inserted from: ", url)
        else:
            print("Already exists: ", url)
    print("================END ONE MORE LOOP====================")            

urls_of_portals = get_feed_urls()
while True:
    connect_to_db(urls=urls_of_portals)
    time.sleep(1)


def fill_rss_table():
    import json


    db = sqlite3.connect("/home/eprivalov/PycharmProjects/sendec/db.sqlite3")
    cursor = db.cursor()

    with open("dictionary_portals.json") as json_file:
        json_data = json.load(json_file)

    print(json_data)

    cursor.execute("SELECT * FROM news_portal")
    list = cursor.fetchall()
    print("ID_list: ", list[0][0])

    cursor.execute("SELECT * FROM news_rss")
    rss = cursor.fetchall()
    print("ID_rss: ", rss[0][0])
    print("LINK_rss: ", rss[0][6])
    print("len_list: ", len(list))
    print("len_rss: ", len(rss))
    print(rss[2][0])



    end = len(rss)*len(list)
    cur_iter = 0
    for i in range(len(rss)):
        for j in range(len(list)):
            cur_iter += 1
            if str(list[j][2]) in str(rss[i][6]):
                id = str(rss[i][0])
                cursor.execute("UPDATE news_rss SET portal_name_id=? WHERE id=?", (str(list[j][0]), id))
                db.commit()
                print("Iter #", cur_iter, "Complete..........", cur_iter/end*100, "%", "When total end is ", end)
            else:
                continue
    db.close()

#fill_rss_table()