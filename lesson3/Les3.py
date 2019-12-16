from bs4 import BeautifulSoup
import requests
import re
import datetime
from pymongo import MongoClient

start_url = 'https://geekbrains.ru/posts'
client = MongoClient('localhost', 27017)
db = client.geekbrains
collection = db.posts


# get last page number
resp = requests.get(start_url)
last_page = 0
for item in re.findall(r'/posts\?page=(\d+)', resp.text):
    last_page = int(item) if last_page < int(item) else last_page

# get all post links from all pages
links = []
i = 1
while i <= 53:
    resp = requests.get(start_url + '?page=' + str(i))
    soup = BeautifulSoup(resp.text, 'lxml')
    for anchor in soup.find_all('a', href=re.compile(r'/posts/')):
        links.append(anchor['href'])
    i = i + 1

# remove duplicates from links
links = list(dict.fromkeys(links))

# request web-pages from all links, get required info from web-pages and insert this info into database
i = 6
while i < len(links):
    url = 'https://geekbrains.ru' + links[i]
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    title = soup.find(attrs={'class': 'blogpost-title'}).getText()
    date = soup.find('time')['datetime'][:10]
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    author = soup.find('div', {'itemprop': 'author'}).getText()
    dbRecord = {
        'title': title,
        'url': url,
        'date': date,
        'author': author
    }
    collection.insert_one(dbRecord)
    i = i + 1



