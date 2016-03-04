import feedparser
import sqlite3, psycopg2
import datetime, time
import os
import string
from random import choice, randint
import lxml.html
import uuid
import random

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
    # with open("rssurls.txt", "r") as file:
    #     url_feeds = file.readlines()

    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()
    query = "SELECT link FROM rss_channels"
    # data_query = ()
    cursor.execute(query)
    url_feeds = cursor.fetchall()
    db.close()

    print(url_feeds)

    urls = []
    for i in range(len(url_feeds)):
        print(url_feeds[i])
        # url_feeds[i] = url_feeds[i]#[:-1]
        urls.append(url_feeds[i][0])
    # return url_feeds
    return urls


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
    elif "published" in keys: args["date"] = feed[0]["published"]
    elif "updated" in keys: args["date"] = feed[0]["updated"]
    else: args["date"] = feed[0]["updated"]
    # DESCRIPTION
    if "description" in keys: args["description"] = feed[0].description
    elif "summary_detail" in keys: args["description"] = feed[0]['summary_detail']['value']
    else: args["description"] = feed[0]['summary']
    return args


def set_user_rss_read(user_id, rss_news_id, rss_portal_id):
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()
    query = "INSERT INTO user_rss_news_read(user_id, rss_news_id, rss_portal_id, read) VALUES(%s,%s,%s,%s)"
    data_query = (user_id, rss_news_id, rss_portal_id, False)
    cursor.execute(query, data_query)
    db.commit()
    return 0


def get_amount_of_user_readers(portal_id):
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()
    query = "SELECT user_id FROM user_rss_news UR WHERE portal_id=%s AND UR.check=TRUE"
    data_query = [portal_id]
    cursor.execute(query, data_query)
    amount = cursor.fetchall()
    # print("Count: ", len(amount), "\nUsers with IDs: ", amount)
    # for i in amount:
        # print(i[0])

    return [len(amount), amount]


def parse_img(url):
    import urllib.request as r
    from urllib import error
    try:
        return lxml.html.parse(r.urlopen(url)).xpath('//img')
    except error.HTTPError:
        return False


def result(url):
    if parse_img(url) == False:
        return False
    else:
        array = []
        for i in parse_img(url):
            if i.get('width') and i.get('height'):
                array.append({'size': str(int(i.get('width'))*int(i.get('height'))), 'src': i.get('src')})
            else:
                pass
        return array


def connect_to_db(urls):
    #   db = sqlite3.connect(BASE_DIR+"\\db.sqlite3")
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")

    import uuid

    cursor = db.cursor()
    num = 0
    for url in urls:
        num += 1
        print("#%s Current url: %s" % (num, url))
        data = last_element(parse_current_url(url=url))
        # print(data["date"])
        try:
            new_date = data["date"].split()
            time = new_date[4].split(":")


            if len(new_date[1]) > len(new_date[2]):
                tmp = new_date[1][:3]
                new_date[1] = new_date[2][:2]
                new_date[2] = tmp


            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            mon = months.index(new_date[2])+1

            date_posted = datetime.datetime(int(new_date[3][:4]), mon, int(new_date[1]), int(time[0]), int(time[1]), int(time[2]))
        except IndexError:
            date_posted = data["date"]


        query_0 = "SELECT ID FROM news_rss WHERE link=%s"
        data_query_0 = [data["link"]]
        cursor.execute(query_0, data_query_0)
        count = cursor.fetchall()
        import re
        match_2 = re.findall(r'src=\"(.*?)\"\s.*/>', data["content"])
        if len(match_2) >= 1:
            # a = re.findall(r'([=\-_.:](\d+x\d+)+)', str(match_2[0]))[0]
            data["main_cover"] = str(match_2[0])#.replace(a, '')
        else:
            # a = re.findall(r'([=\-_.:](\d+x\d+)+)', str(match_2))[0]
            data["main_cover"] = str(match_2)#.replace(a, '')

        if len(match_2) == 0:
            match_3 = re.findall(r'src=\"(.*?)\"\s.*/>', data["description"])
            a = str(match_3)

            if len(match_3) >= 1:
                data["main_cover"] = str(match_3[0])#.replace(a, '')
            else:
                # a = re.findall(r'([=\-_.:](\d+x\d+)+)', str(match_2))[0]
                data["main_cover"] = str(match_3)#.replace(a, '')


        data["content"] = data["content"].replace("\xa0", " ").replace("%", "%%").replace("> ", "> ").replace(" </", "</").replace(" <", " <").replace("\n<", "<").replace("\n", " ").replace("'", "&rsquo;")
        data["title"] = data["title"].replace('"', '').replace("\xa0", " ").replace("%", "%%").replace("> ", "> ").replace(" </", "</").replace(" <", " <").replace("\n<", "<").replace("\n", " ").replace("'", "&rsquo;")
        data["description"] = data["description"].replace("\xa0", "").replace("%", "%%").replace("> ", "> ").replace(" </", "</").replace(" <", " <").replace("\n<", "<").replace("\n", " ").replace("'", "&rsquo;")


        # TEST
        # match = re.findall(r'<.*?>', data["description"])
        # for i in match:
        #     data["description"] = data["description"].replace(i, "")

    ############## Parse all images from current url #######################
    # def parse_img(url):
    #     return lxml.html.parse(url).xpath('//img')

    # def print_matches(url):
    #     for i in parse_img(url):
    #         print(i.get('width'), i.get('height'), i.get('src'))

    # def result(url):
    #     array = []
    #     for i in parse_img(url):
    #         if i.get('width') and i.get('height'):
    #             array.append({'size':str(int(i.get('width'))*int(i.get('height'))), 'src': i.get('src')})
    #         else:
    #             pass
    #     return array
    #
        if data["main_cover"] == '[]':
            end = result(data['link'])
            if end != False:
                max_item = 0
                for i in range(len(end)):
                    if int(end[i]['size']) > max_item:
                        max_item = int(end[i]['size'])

                for i in range(len(end)):
                    if int(end[i]['size']) == max_item:
                        current_cover = end[i]['src']

                        data["main_cover"] = current_cover
    ############################################################################



        match_tabs = re.findall(r'[\s]{2,}', data["description"])
        for i in match_tabs:
            data["description"] = data["description"].replace(i, " ")
        data["description"] = data["description"].replace("\n", "").replace("\t", "")

        query_for_rss = "SELECT * FROM rss_portals"
        cursor.execute(query_for_rss)
        portals_list = cursor.fetchall()

        for current_portal in portals_list:
            if current_portal[2] in data["link"]:
                current_rss_news_id = current_portal[0]    # CURRENT PORTAL ID
                current_rss_news_cat_id = current_portal[7]

        if len(count) == 0:
            #cursor.execute("""INSERT INTO news_rss(title, date_posted, post_text, link, portal_name_id, category_id, content_value, author) VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",(data["title"], datetime.datetime(int(new_date[3]), 11, int(new_date[1]), int(time[0]), int(time[1]), int(time[2])), data["description"], data["link"], 1, 1, data["content"], data["author"]))
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
            instance = get_amount_of_user_readers(current_rss_news_id)
            user_amount = instance[0]
            users = [i[0] for i in instance[1]]
            for i in range(len(users)):
                set_user_rss_read(users[i], current_rss_id, current_rss_news_id)
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
        file_list = json.load(file_list)
    with open("dictionary_portals.json", encoding="utf-8-sig") as file:
        portals = json.load(file)
    end = len(portals)
    print(end)
    cur_iter = 0
    for i in range(1,len(file_list)):
        i = i+1
        query_0 = "SELECT ID FROM rss_portals WHERE portal=%s"
        data_query_0 = [file_list['object-%s'%i]["name"]]
        cursor.execute(query_0, data_query_0)
        count = cursor.fetchall()


        if len(count) == 0:
            cur_iter += 1
            categories = {"Technology": 1, "Entertainment": 2, "Auto": 3, "Space": 4, "BIO": 5}
            query = "INSERT INTO rss_portals(portal, portal_base_link, follows, description, cover, favicon, verbose_name, category_id, puid) VALUES(%s, %s, %s, %s, %s,%s,%s,%s, %s)"
            data_query = (file_list['object-%s'%i]["name"],
                          file_list['object-%s'%i]["base_link"],
                          0,
                          file_list['object-%s'%i]["description"],
                          file_list['object-%s'%i]["cover"],
                          file_list['object-%s'%i]["favicon"],
                          file_list['object-%s'%i]["verbose"],
                          categories[file_list['object-%s'%i]["category"]],
			  str(uuid.uuid4()),
			 )
            cursor.execute(query, data_query)
            db.commit()


            # Add feed to each portal
            query_test = "SELECT DISTINCT ON (ID) ID FROM rss_portals WHERE portal_base_link=%s"
            query_test_data = [file_list['object-%s'%i]['base_link']]
            cursor.execute(query_test, query_test_data)
            rss_id = cursor.fetchall()
            query_channel = "INSERT INTO rss_channels(portal_id, link) VALUES(%s, %s)"
            query_channel_data = (rss_id[0], file_list['object-%s'%i]["feed"])
            cursor.execute(query_channel, query_channel_data)
            db.commit()



            print("Iter #", cur_iter, "Complete..........", cur_iter/end*100, "%", "When total end is ", end)
        else:
            # Add feed to each portal
            query_test = "SELECT DISTINCT ON (ID) ID FROM rss_portals WHERE portal=%s"
            query_test_data = [file_list['object-%s'%i]['name']]
            cursor.execute(query_test, query_test_data)
            rss_id = cursor.fetchall()
            query_channel = "INSERT INTO rss_channels(portal_id, link) VALUES(%s, %s)"
            query_channel_data = (rss_id[0], file_list['object-%s'%i]["feed"])
            cursor.execute(query_channel, query_channel_data)
            db.commit()


    db.close()


def fill_companies():
    import json
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()
    with open("c_2.json", encoding="utf-8-sig") as file_list:
        file_list = list(json.load(file_list))
    with open("c_2.json", encoding="utf-8-sig") as file:
        companies = json.load(file)

    end = len(companies)
    cur_iter = 0
    current_category_id = 0
    for i in range(end):
        if companies[file_list[i]]['category'] == "technology": current_category_id = 1
        if companies[file_list[i]]['category'] == "entertainment": current_category_id = 2
        if companies[file_list[i]]['category'] == "auto": current_category_id = 3
        if companies[file_list[i]]['category'] == "space": current_category_id = 4
        if companies[file_list[i]]['category'] == "bio" or companies[file_list[i]]['category'] == "bit" : current_category_id = 5
        description = ""

        cur_iter += 1

        query_check = "SELECT * FROM companies WHERE site=%s"
        data_query_check = [companies[file_list[i]]['site']]
        cursor.execute(query_check, data_query_check)
        check = cursor.fetchall()
        print(check)
        print(len(check))
        if len(check) > 0:
            pass
        else:
            query = "INSERT INTO companies(name, verbose_name, site, category_id, logo, description) VALUES(%s, %s, %s, %s, %s, %s)"
            data_query = (companies[file_list[i]]['name'], companies[file_list[i]]['verbose'],
                          companies[file_list[i]]['site'], current_category_id,
                          companies[file_list[i]]['logo'], description)
            cursor.execute(query, data_query)
            db.commit()
        print("Iter #", cur_iter, "Complete..........", cur_iter/end*100, "%", "Dealed with ", companies[file_list[i]]['name'])
    db.close()


def fill_portals():
    import json
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()

    query_portals = "INSERT INTO news_portal(portal_name, portal_base_link) VALUES(%s,%s)"
    query_data = ("Appleinsider", "appleinsider.ru")
    cursor.execute(query_portals, query_data)
    db.commit()
    db.close()

def fill_news():
    import json
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()
    with open("news_zaharov_2.json", encoding="utf-8-sig") as file_list:
        file_list = list(json.load(file_list))
    with open("news_zaharov_2.json", encoding="utf-8-sig") as file:
        news = json.load(file)

    end = len(news)
    cur_iter = 0

    for i in range(end):
        try:
            for j in [1,2,3,4,5]:
            # if news[file_list[i]]['category'] == "technology" and news[file_list[i]]['date'] != "date":
                cur_iter += 1
                news_title_english = "[eng]"+news[file_list[i]]["title"]
                news_title_russian = "[rus]"+news[file_list[i]]["title"]
                news_title_chinese = "[ch]"+news[file_list[i]]["title"]
                news_category_id = j    # Technology
                news_post_date = news[file_list[i]]["date"]
                teaser_english = "[eng] Teaser"
                teaser_russian = "[rus] Teaser"
                teaser_chinese = "[ch] Teaser"
                news_post_text_english = news[file_list[i]]["text"]
                news_post_text_russian = news[file_list[i]]["text"]
                news_post_text_chinese = news[file_list[i]]["text"]
                news_portal_name_id = 1    # Insydia
                news_company_owner_id = 1    # Insydia
                news_author_id = 1    # Saqel
                news_main_cover = ""    # None
                news_likes = 0
                news_dislikes = 0
                photo = ""
                news_tags = "{}"
                slug = "%s-b-a-a-%s" % (j, i)


                query_set = "INSERT INTO news(news_title_english, news_title_russian, news_title_chinese, news_category_id, news_post_date, news_post_text_english, " \
                            "teaser_english, teaser_russian, teaser_chinese, news_post_text_russian, news_post_text_chinese, news_portal_name_id, news_company_owner_id, news_author_id, " \
                            "news_main_cover, photo, news_likes, news_dislikes, news_tags, slug) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                data_query_set = (news_title_english,
                                  news_title_russian,
                                  news_title_chinese,
                                  news_category_id,
                                  news_post_date,
                                  news_post_text_english,
                                  teaser_english,
                                  teaser_russian,
                                  teaser_chinese,
                                  news_post_text_russian,
                                  news_post_text_chinese,
                                  news_portal_name_id,
                                  news_company_owner_id,
                                  news_author_id,
                                  news_main_cover,
                                  photo,
                                  news_likes,
                                  news_dislikes,
                                  news_tags,
                                  slug)
                cursor.execute(query_set, data_query_set)
                db.commit()
                #print(cur_iter, data_query_set)
                print("Iter #", cur_iter, "Complete..........", cur_iter/end*100, "%", "Dealed with ", news_title_english)
        except KeyError:
            print(news[file_list[i]])
    db.close()


def save_rss_news():
    import json
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()

    query_set = "SELECT * FROM news_rss"
    cursor.execute(query_set)
    db.commit()
    data = cursor.fetchall()

    end = len(data)
    count = 0
    with open("save_rss.json", "a+", encoding="utf-8") as file:
        file.write("{")
        for i in range(len(data)):
            count += 1
            file.write('"object":')
            data_dict = {}
            data_dict["title"] = data[i][1]#["title"]
            data_dict["date_posted"] = data[i][2].isoformat()#["date_posted"]
            data_dict["post_text"] = data[i][3]#["post_text"]
            data_dict["portal_name"] = data[i][4]#["portal_name"]
            data_dict["category"] = data[i][5]#["category"]
            data_dict["link"] = data[i][6]#["link"]
            data_dict["author"] = data[i][7]#["author"]
            data_dict["content_value"] = data[i][8]#["content_value"]

            file.write(json.dumps(data_dict))
            file.write(",")
            print("Saving RSS # ", count, " success. In total - ", end, " items")
        file.write("}")
    db.close()


def create_categories():
    db = psycopg2.connect("dbname='test' user='testuser' host='' password='test'")
    cursor = db.cursor()
    categories = ["Technology", "Entertainment", "Auto", "Space", "BIO"]
    for i in categories:
        query_set = "INSERT into news_category(category_name) VALUES(%s)"
        query_data = [i]
        cursor.execute(query_set, query_data)
        db.commit()
        print("Category ", i, "added")
    db.close()


def work_func():
    urls_of_portals = get_feed_urls()
    print("1. Fill Rss Portals\n2. Syndicate news\n3. Fill Companies\n4. Fill news\n5. Save RSS\n6.User readers\n7. Create categories\n8. Fill portals")
    x = int(input("What can I help you? Enter number: "))
    if x == 1:
        fill_rss_portals()
    elif x == 2:
        while True:
            # try:
            connect_to_db(urls=urls_of_portals)
            time.sleep(1)
            # except IndexError:
            #     pass
    elif x == 3:
        fill_companies()
    elif x == 4:
        fill_news()
    elif x == 5:
        save_rss_news()
    elif x == 6:
        get_amount_of_user_readers(3)
    elif x == 7:
        create_categories()
    elif x == 8:
        fill_portals()
    else:
        import sys
        print("Good bye!")
        sys.exit(0)

#fill_start_data_news()
while True:
    work_func()
