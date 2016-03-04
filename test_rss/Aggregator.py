# -*- coding: utf-8 -*-
import psycopg2
import feedparser
import lxml.html
import urllib.request as r
from urllib import error
import datetime
from random import choice
import string
import re
import tldextract
import time

class Aggregator(object):

    db_name = "test"
    user = "testuser"
    host = ""
    password = "test"

    def __init__(self, *args, **kwargs):
        self.main_func(urls=self.get_feed_urls())


    def connect_to_database(self, db_name, user, host, password):
        return psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (db_name, user, host, password))

    def get_feed_urls(self):
        urls = []
        db = self.connect_to_database(db_name=self.db_name, user=self.user, host=self.host, password=self.password)
        cursor = db.cursor()
        query = "SELECT link FROM rss_channels"
        cursor.execute(query)
        url_feeds = cursor.fetchall()
        db.close()
        for i in range(len(url_feeds)):
            urls.append(url_feeds[i][0])
        return urls

    def parse_current_url(self, url=''):
        url_parse = feedparser.parse(url)
        return [i for i in url_parse.entries]

    def last_element(self, feed):
        array = []
        for i in range(len(feed)):
            args = {"title": feed[i].title, "link": feed[i].link, "main_cover": ""}
            keys = feed[i].keys()
            # AUTHOR
            if "author" in keys: args["author"] = feed[i].author
            else: args["author"] = ""
            # CONTENT
            if "content" in keys: args["content"] = feed[i].content[0]["value"]
            else: args["content"] = ""
            # DATE
            if "date" in keys: args["date"] = feed[i].published
            elif "published" in keys: args["date"] = feed[i]["published"]
            elif "updated" in keys: args["date"] = feed[i]["updated"]
            else: args["date"] = feed[i]["updated"]
            # DESCRIPTION
            if "description" in keys: args["description"] = feed[i].description
            elif "summary_detail" in keys: args["description"] = feed[i]['summary_detail']['value']
            else: args["description"] = feed[i]['summary']
            array.append(args)
        return array

    def set_user_rss_read(self, user_id, rss_news_id, rss_portal_id):
        db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
        cursor = db.cursor()
        query = "INSERT INTO user_rss_news_read(user_id, rss_news_id, rss_portal_id, read) VALUES(%s,%s,%s,%s)"
        data_query = (user_id, rss_news_id, rss_portal_id, False)
        cursor.execute(query, data_query)
        db.commit()
        return 0

    def get_amount_of_user_readers(self, portal_id):
        db = self.connect_to_database(db_name=self.db_name, user=self.user, host=self.host, password=self.password)
        cursor = db.cursor()
        query = "SELECT user_id FROM user_rss_news UR WHERE portal_id=%s AND UR.check=TRUE"
        data_query = [portal_id]
        cursor.execute(query, data_query)
        amount = cursor.fetchall()
        db.close()
        return [len(amount), amount]

    def parse_img(self, url):
        try:
            return lxml.html.parse(r.urlopen(url)).xpath('//img')
        except:
            return []

    def result(self, url):
        print(self.parse_img(url))
        if not self.parse_img(url=url):
            return False
        else:
            array = []
            for i in self.parse_img(url):
                if i.get('width') and i.get('height'):
                    if "%" in i.get('width') or "%" in i.get('height'):
                        width = 800
                        height = 600
                        array.append({'size': str(width*height), 'src': i.get('src')})
                    else:
                        width, height = i.get('width'), i.get('height')
                        match_w, match_h = re.findall("(\d+)", width), re.findall("(\d+)", height)
                        width, height = match_w[0], match_h[0]
                        array.append({'size': int(float(width)*float(height)), 'src': i.get('src')})
                else:
                    pass
            return array

    def main_func(self, urls):
        db = self.connect_to_database(db_name=self.db_name, user=self.user, host=self.host, password=self.password)
        cursor = db.cursor()
        num = 0
        for url in urls:
            num += 1
            print("#%s Current url: %s" % (num, url))
            data_all = self.last_element(self.parse_current_url(url=url))
            for data in data_all:
                try:
                    new_date = data["date"].split()
                    time = new_date[4].split(":")

                    if len(new_date[1]) > len(new_date[2]):
                        tmp = new_date[1][:3]
                        new_date[1] = new_date[2][:2]
                        new_date[2] = tmp

                    month_ru = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
                    if str(new_date[2]).encode("utf-8").lower() in month_ru:
                        mon = month_ru.index(str(new_date[2]).encode("utf-8").lower())+1
                    else:
                        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                        mon = months.index(new_date[2])+1
                    # print("hour", time[0])
                    # print("minute", time[1])
                    # print("sec", time[2])
                    if time[0] in [24, "24"]:
                        time[0] = "00"
                    date_posted = datetime.datetime(int(new_date[3][:4]), mon, int(new_date[1]), int(time[0]), int(time[1]), int(time[2]))
                except IndexError:
                    date_posted = data["date"]


                query_0 = "SELECT ID FROM news_rss WHERE link=%s"
                data_query_0 = [data["link"]]
                cursor.execute(query_0, data_query_0)
                count = cursor.fetchall()

                match_2 = re.findall(r'src=\"(.*?)\"\s.*/>', data["content"])
                if len(match_2) >= 1:
                    data["main_cover"] = str(match_2[0])
                else:
                    data["main_cover"] = str(match_2)
                if len(match_2) == 0:
                    match_3 = re.findall(r'src=\"(.*?)\"\s.*/>', data["description"])
                    a = str(match_3)

                    if len(match_3) >= 1:
                        data["main_cover"] = str(match_3[0])
                    else:
                        data["main_cover"] = str(match_3)


                data["content"] = data["content"].replace("\xa0", " ").replace("%", "%%").replace("> ", "> ").replace(" </", "</").replace(" <", " <").replace("\n<", "<").replace("\n", " ").replace("'", "&rsquo;")
                data["title"] = data["title"].replace('"', '').replace("\xa0", " ").replace("%", "%%").replace("> ", "> ").replace(" </", "</").replace(" <", " <").replace("\n<", "<").replace("\n", " ").replace("'", "&rsquo;")
                data["description"] = data["description"].replace("\xa0", "").replace("%", "%%").replace("> ", "> ").replace(" </", "</").replace(" <", " <").replace("\n<", "<").replace("\n", " ").replace("'", "&rsquo;")


                if data["main_cover"] == '[]':
                    end = self.result(data['link'])
                    if end != False:
                        max_item = 0
                        for i in range(len(end)):
                            if int(end[i]['size']) > max_item:
                                max_item = int(end[i]['size'])
                        for i in range(len(end)):
                            if int(end[i]['size']) == max_item:
                                current_cover = end[i]['src']
                                data["main_cover"] = current_cover


                match_tabs = re.findall(r'[\s]{2,}', data["description"])
                for i in match_tabs:
                    data["description"] = data["description"].replace(i, " ")
                data["description"] = data["description"].replace("\n", "").replace("\t", "")

                query_for_rss = "SELECT * FROM rss_portals"
                cursor.execute(query_for_rss)
                portals_list = cursor.fetchall()


                # print("data: ", data)
                n = tldextract.extract(data['link'])
                n_d, n_s = n.domain, n.suffix
                new_url = n_d+"."+n_s
                for current_portal in portals_list:

                    if current_portal[2] in new_url or new_url in current_portal[2] or current_portal[2].split('.')[0] in new_url:
                        print("portal id: ", current_portal[0])
                        # print("cat id: ", current_portal[8])
                        current_rss_news_id = current_portal[0]    # CURRENT PORTAL ID
                        current_rss_news_cat_id = current_portal[8]
                if len(count) == 0:
                    query = """INSERT INTO news_rss(title, date_posted, post_text, link, portal_name_id, category_id, content_value, author, nuid) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    data_query = (data["title"],
                                  date_posted,
                                  data["description"],
                                  data["link"],
                                  current_rss_news_id,
                                  current_rss_news_cat_id,
                                  data["content"],
                                  data["author"],
                                  ''.join(choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _
                                                      in range(33)))
                    cursor.execute(query, data_query)
                    query_2 = "SELECT ID FROM news_rss WHERE title=%s"
                    data_query_2 = [data["title"]]
                    cursor.execute(query_2, data_query_2)
                    current_rss_id = cursor.fetchone()[0]


                    query_3 = "INSERT INTO rss_news_covers(rss_news_id, main_cover) VALUES (%s, %s)"
                    data_query_3 = (int(current_rss_id), data["main_cover"])
                    cursor.execute(query_3, data_query_3)


                    query_rss_portal = "UPDATE rss_portals SET cover=%s WHERE id=%s"
                    query_rss_portal_data=(data["main_cover"], int(current_rss_news_id))
                    cursor.execute(query_rss_portal, query_rss_portal_data)


                    db.commit()
                    instance = self.get_amount_of_user_readers(current_rss_news_id)
                    users = [i[0] for i in instance[1]]
                    for i in range(len(users)):
                        self.set_user_rss_read(users[i], current_rss_id, current_rss_news_id)
                else:
                    pass
        print("================END ONE MORE LOOP====================")
        db.close()
        return 0


if __name__ == "__main__":
    while True:
        Aggregator()
        time.sleep(60*60)   # One hour remaining
