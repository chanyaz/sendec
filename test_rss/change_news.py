with open("news_kristina.json", "r+") as file:
    f = file.read()
#a = f.replace('"verbose":', ', "verbose":')
a = f.replace('"', "'").replace("\n", " ").replace("' }, 'object-'", '" }, "object-"').replace("': { 'portal': '", '": { "portal": "').replace("', 'category': '", '", "category": "').replace("', 'title': '", '", "title": "').replace("', 'text': '", '", "text": "').replace("', 'date': '", '", "date": "').replace("' }, 'object-", '" }, "object-').replace("'news': { 'object-1\"", '"news": { "object-1\"').replace("':{ 'portal': '", '":{ "portal": "').replace("' } 'object-", '" } "object-').replace('" } "object-', '" }, "object-')

with open("news_kristina_2.json", "a+") as file_2:
    file_2.write(a)
print("success")
