#http://shop.kongfz.com/180897/all/0_100_0_0_1_sort_desc_0_1000/
import time
import requests
import wget
from retry import retry
from pyquery import PyQuery as pq
import os
import pandas as pd
from selenium import webdriver



@retry(tries=3, delay=2)#报错重试
def download(img_url,path):
    time.sleep(1)
    print (img_url)
    downloadfile = wget.download(img_url, out=path, bar=None)
    return downloadfile

headers= {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Host':'book.kongfz.com',
    'Upgrade-Insecure-Requests':'1'}

def findISBN(path):
    res = requests.get(path,headers=headers)
    doc = pq(res.text)
    #body > div.main - box > div.main.content > div.main - bot.clear - fix > div.right - block > ul > li.item - detail - page > div.major - info.clear - fix > div.major - info - main > div.major - info - text > div > ul.detail - list1 > li: nth - child(5) > span
    item_doc = doc("body > div.main-box > div.main.content > div.main-top.clear-fix > div.major-function-box.clear-fix > div.major-function > div.base-info > div.keywords-define.keywords-define-1200.clear-fix ")
    title=item_doc("ul:nth-child(1) > li:nth-child(3) > span.keywords-define-title").text()
    ISBN=item_doc("ul:nth-child(1) > li:nth-child(3) > span.keywords-define-txt").text()
    # body > div.main-box > div.main.content > div.main-bot.clear-fix > div.right-block > ul > li.item-detail-page > div.major-info.clear-fix > div.major-info-main > div.major-info-text > div > ul.detail-list1 > li:nth-child(5) > span
    ISBN1=doc("body > div.main-box > div.main.content > div.main-bot.clear-fix > div.right-block > ul > li.item-detail-page > div.major-info.clear-fix > div.major-info-main > div.major-info-text > div > ul.detail-list1 > li:nth-child(5) > span").text()
    if "ISBN" in title:
        return ISBN
    else:
        return ISBN1

def findPic(path):
    res = requests.get(path, headers=headers)
    doc = pq(res.text)
    picHerf=doc("body > div.main-box > div.main.content > div.main-top.clear-fix > div.major-function-box.clear-fix > div.exhibition.pull-left > ul > li > img").attr("src")
    if picHerf is None:
        return None
    return "http:"+picHerf

i=17777
herfSets=set()
start=30
end=41
# driver = webdriver.Chrome()

for t in range(start,end):
    pieces = []
    columns = ['code', 'title', 'ISBN', 'author', 'publisher', 'publisherTimes', 'birthDate', 'quality', 'BlNew',
               'price', 'transPrice', 'sellDate', 'bookHref']
    driver = webdriver.PhantomJS()
    for pages in range(1, 21):
        page = pages+t*20-20
        path = "http://shop.kongfz.com/180897/all/0_100_0_0_%d_sort_desc_10_1000/" % page
        driver.get(path)
        res = driver.page_source
        doc = pq(res)
        item_doc = doc('#listBox > div')
        for numb in range(1, 101):
            item = item_doc("div:nth-child(%d)" % numb);
            # listBox > div > div:nth-child(1) > a
            title = item("a").text().replace("/", "").replace(" ", "")
            bookHref = item("a").attr("href")
            if (title in herfSets or bookHref is None or len(bookHref) < 25):
                print()
                continue
            isbn = findISBN(bookHref)
            # listBox > div > div:nth-child(1) > div.row-author
            author = item("div.row-author").text().replace("/", "").replace(" ", "")
            # listBox > div > div:nth-child(1) > div.row-press
            publisher = item("div.row-press").text().replace("/", "").replace(" ", "")
            # #listBox > div > div:nth-child(1) > div.row-years
            publisherTimes = "null"
            # null
            birthDate = item("div.row-years").text().replace("/", "").replace(" ", "")
            if (birthDate >= '2016'):
                continue
            # #listBox > div > div:nth-child(1) > div.row-quality
            quality = "null"
            # listBox > div:nth-child(1) > div.item-other-info > div.first-info.clearfix > div.quality
            BlNew = item("div.first-info.clearfix > div.quality").text()
            # #listBox > div > div:nth-child(1) > div.row-price > span.bold
            price = item("div.row-price > span.bold").text()

            herfSets.add(bookHref)
            transPrice = "14"
            sellDate = "null"

            i = i + 1
            # img_url = item("div.item-img > a > img").attr("src")
            img_url = findPic(bookHref)
            if img_url is None:
                img_url = item("div.item-img > div > img").attr("_src")
                if img_url is None:
                    continue
            path = "C:/Users/zoo/PycharmProjects/LJC/file/pic"
            names = "/" + str(i) + ".jpg"
            try:
                downloadfile = wget.download(img_url, out=path, bar=None)
            except:
                downloadfile = download(img_url, path)
            os.rename(downloadfile, path + names)
            pieces.append([i, title, isbn, author, publisher, publisherTimes, birthDate, quality, BlNew, price, transPrice,sellDate, bookHref])
            herfSets.add(title)
    driver.close()
    dataFrame = pd.DataFrame(pieces, columns=columns)
    dataFrame.to_csv('C:/Users/zoo/PycharmProjects/LJC/file/demo%d.csv'%t)
    print(dataFrame)