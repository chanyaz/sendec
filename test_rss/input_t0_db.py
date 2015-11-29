import sqlite3
import json

def input_to_db():
    db = sqlite3.connect("/home/eprivalov/PycharmProjects/sendec/sendec/db.sqlite3")
    #db = sqlite3.connect("C:\\Users\\eprivalov\\PycharmProjects\\sendec\\sendec\\db.sqlite3")
    cursor = db.cursor()

    with open("dictionary_portals.json") as json_file_list:
        json_data_list = list(json.load(json_file_list))

    with open("dictionary_portals.json") as json_file:
        json_data = json.load(json_file)



    for i in range(len(json_data)):
        cursor.execute("""SELECT rowid FROM news_portal WHERE portal_name=?""", [json_data[json_data_list[i]]["name"]])
        count = cursor.fetchall()
        if len(count) == 0:
            cursor.execute("""INSERT INTO news_portal(portal_name, portal_base_link) VALUES(?, ?)""", (json_data[json_data_list[i]]["name"], json_data[json_data_list[i]]["base_link"]))
            db.commit()
            print("Added: ", json_data[json_data_list[i]]["name"])
        else:
            continue
    db.close()


def input_companies():
    db = sqlite3.connect("/home/eprivalov/PycharmProjects/sendec/sendec/db.sqlite3")
    #db = sqlite3.connect("C:\\Users\\eprivalov\\PycharmProjects\\sendec\\sendec\\db.sqlite3")
    cursor = db.cursor()
    with open("dictionary_companies.json") as json_file_list:
        json_data_list = list(json.load(json_file_list))
    with open("dictionary_companies.json") as json_file:
        json_data = json.load(json_file)
    for i in range(len(json_data)):
        cursor.execute("""SELECT * FROM companies WHERE name=?""", [json_data[json_data_list[i]]["name"]])
        count = cursor.fetchall()
        if len(count) == 0:
            cursor.execute("""INSERT INTO companies(name, verbose_name, site, category_id, logo) VALUES(?, ?, ?, ?, ?)""", (json_data[json_data_list[i]]["name"], "verbose", "site", "category_id", "logo"))
            db.commit()
            print("Added: ", json_data[json_data_list[i]]["name"])
        else:
            continue
    print("Companies amount: ", len(json_data_list))
    db.close()

input_companies()
#input_to_db()

