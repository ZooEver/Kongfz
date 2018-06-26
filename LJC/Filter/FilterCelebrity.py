import requests
import wget
from pyquery import PyQuery as pq
import os
import pandas as pd
from selenium import webdriver
import time
from retry import retry
import socket

socket.setdefaulttimeout(20)  # 设置socket层的超时时间为20秒
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
    'Upgrade-Insecure-Requests':'1'
    }

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

pieces=[]
columns=['code','title','ISBN','quality','BlNew','price']
i=18593
herfSets=set()

#driver = webdriver.Chrome()
driver = webdriver.PhantomJS()
for pages in range(1,21):
    page=pages
    time.sleep(1)
    path="http://search.kongfz.com/product_result/?status=0&catnum=21&pubdate=190001h201512&price=5.00h1000.00&pagenum=%d"%page
    driver.get(path)
    res=driver.page_source
    # print(res)
    # res = requests.get(path,headers=headers)
    doc = pq(res)
    # print(res.status_code)
    # print(doc)
    item_doc = doc('#listBox > div')
    for item in item_doc.items():
        # listBox > div:nth-child(1) > div.item-info > div.title > a
        # listBox > div:nth-child(1) > div.item-info > div.title > a
        title = item("div.item-info > div.title > a").text().replace("/","").replace(" ","")
        bookHref = item("div.item-info > div.title > a").attr("href")
        if(title in herfSets):
            continue
        isbn=findISBN(bookHref)
        # listBox > div:nth-child(1) > div.item-info > div.zl-normal-info.clearfix > div.f_left
        itemInfo=item("div.item-info>div.zl-normal-info.clearfix > div.f_left")
        # listBox > div:nth-child(1) > div.item-info > div.zl-normal-info.clearfix > div.f_right > div:nth-child(3) > span.normal-text
        quality=item("div.item-info>div.zl-normal-info.clearfix > div.f_right > div:nth-child(3) > span.normal-text").text().replace("/","").replace(" ","")
        itemOtherInfo= item("div.item-other-info")
        # listBox > div:nth-child(1) > div.item-other-info > div.first-info.clearfix > div.quality
        BlNew=itemOtherInfo("div.first-info.clearfix > div.quality").text()
        # listBox > div:nth-child(1) > div.item-other-info > div.first-info.clearfix > div.f_right.red.price > span.bold
        price=itemOtherInfo("div.first-info.clearfix > div.f_right.red.price > span.bold").text()
        i = i + 1
        #img_url = item("div.item-img > a > img").attr("src")
        img_url=findPic(bookHref)
        if img_url is None:
            img_url = item("div.item-img > div > img").attr("_src")
        path="C:/Users/zoo/PycharmProjects/LJC/file/pic"
        names="/"+str(i)+".jpg"
        try:
            img_url=img_url.replace("http:http:","http:")
            downloadfile = wget.download(img_url, out=path, bar=None)
        except:
            downloadfile = download(img_url, path)
        os.rename(downloadfile, path + names)
        pieces.append([i,title,isbn,quality,BlNew,price])
        herfSets.add(title)
driver.close()
dataFrame=pd.DataFrame(pieces,columns=columns)
dataFrame.to_csv('C:/Users/zoo/PycharmProjects/LJC/file/demo.csv')
print(dataFrame)

