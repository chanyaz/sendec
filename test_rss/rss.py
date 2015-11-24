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
        db = sqlite3.connect("C:\\Users\\eprivalov\\PycharmProjects\\sendec\\sendec\\db.sqlite3")
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


