import requests
import wget
from pyquery import PyQuery as pq
import os
import pandas as pd


headers= {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Host':'book.kongfz.com',
    'Upgrade-Insecure-Requests':'1'
    }

def test():
    path = 'http://book.kongfz.com/Cyiyao/xsv6w1/'
    res = requests.get(path, headers=headers)
    doc = pq(res.text)
    # listBox > div:nth-child(1) > div.item-info > div.title > a
    item_doc = doc('#listBox > div')
    for item in item_doc.items():
        bookHref = item("div.item-info > div.title > a").attr("href")
        tt=bookHref.replace("http://book.kongfz.com/","").split("/")
        print(bookHref)
        findISBN(bookHref)
def findISBN(path):
    res = requests.get(path,headers=headers)
    doc = pq(res.text)
    #body > div.main - box > div.main.content > div.main - bot.clear - fix > div.right - block > ul > li.item - detail - page > div.major - info.clear - fix > div.major - info - main > div.major - info - text > div > ul.detail - list1 > li: nth - child(5) > span
    item_doc = doc("body > div.main-box > div.main.content > div.main-top.clear-fix > div.major-function-box.clear-fix > div.major-function > div.base-info > div.keywords-define.keywords-define-1200.clear-fix ")
    title=item_doc("ul:nth-child(1) > li:nth-child(3) > span.keywords-define-title").text()
    ISBN=item_doc("ul:nth-child(1) > li:nth-child(3) > span.keywords-define-txt").text()
    item_doc1 = doc("body > div.main-box > div.main.content > div.main-bot.clear-fix > div.right-block > ul > li.item-detail-page > div.major-info.clear-fix > div.major-info-main > div.major-info-text > div > ul.detail-list1 > li:nth-child(5) > span")
    print(item_doc1)
    if "ISBN" in title:
        return ISBN
    else:
        return "null"

test()


