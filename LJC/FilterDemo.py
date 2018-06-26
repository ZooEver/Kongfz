#http://search.kongfz.com/product_result/?status=0&catnum=17&pubdate=194901h201512&quality=70h&quaselect=3&price=5.00h2000.00&pagenum=3

import requests
import wget
from pyquery import PyQuery as pq
import os
import pandas as pd
from selenium import webdriver
import time


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
columns=['code','title','ISBN','author','publisher','publisherTimes','birthDate','quality','BlNew','price','transPrice','sellDate','bookHref']
i=15977
herfSets=set()

#driver = webdriver.Chrome()
driver = webdriver.PhantomJS()
for pages in range(1,21):
    page=21-pages
    path="http://search.kongfz.com/product_result/?status=0&catnum=17&pubdate=194901h201512&quality=70h&quaselect=3&price=5.00h2000.00&order=6&pagenum=%d"%page
    time.sleep(1)
    # path='http://book.kongfz.com/Cyiyao/xsv6w%d/'%page
    try:
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
            # listBox > div:nth-child(1) > div.item-info > div.zl-normal-info.clearfix > div.f_left > div:nth-child(1) > span.normal-text
            author=itemInfo("div:nth-child(1) > span.normal-text").text().replace("/","").replace(" ","")
            # listBox > div:nth-child(1) > div.item-info > div.zl-normal-info.clearfix > div.f_left > div:nth-child(2) > span.normal-text
            publisher=itemInfo("div:nth-child(2) > span.normal-text").text().replace("/","").replace(" ","")
            # listBox > div:nth-child(1) > div.item-info > div.zl-normal-info.clearfix > div.f_left > div:nth-child(3) > span.normal-text
            publisherTimes=itemInfo("div:nth-child(3) > span.normal-text").text().replace("/","").replace(" ","")
            # listBox > div:nth-child(1) > div.item-info > div.zl-normal-info.clearfix > div.f_left > div:nth-child(4) > span.normal-text
            birthDate=itemInfo("div:nth-child(4) > span.normal-text").text().replace("/","").replace(" ","")
            # listBox > div:nth-child(1) > div.item-info > div.zl-normal-info.clearfix > div.f_right > div:nth-child(3) > span.normal-text
            quality=item("div.item-info>div.zl-normal-info.clearfix > div.f_right > div:nth-child(3) > span.normal-text").text().replace("/","").replace(" ","")
            itemOtherInfo= item("div.item-other-info")
            # listBox > div:nth-child(1) > div.item-other-info > div.first-info.clearfix > div.quality
            BlNew=itemOtherInfo("div.first-info.clearfix > div.quality").text()
            # listBox > div:nth-child(1) > div.item-other-info > div.first-info.clearfix > div.f_right.red.price > span.bold
            price=itemOtherInfo("div.first-info.clearfix > div.f_right.red.price > span.bold").text()

            herfSets.add(bookHref)
            transPrice=itemOtherInfo("div.ship-fee-box > div> span:nth-child(2)").text()
            sellDate=itemOtherInfo("div.add-time-box > span:nth-child(1)").text()

            i = i + 1
            #img_url = item("div.item-img > a > img").attr("src")
            img_url=findPic(bookHref)
            if img_url is None:
                img_url = item("div.item-img > div > img").attr("_src")
            path="C:/Users/zoo/PycharmProjects/LJC/file/pic"
            names="/"+str(i)+".jpg"
            try:
                downloadfile = wget.download(img_url, out=path, bar=None)
                os.rename(downloadfile, path + names)
            except:
                i=i-1
                continue
            pieces.append([i,title,isbn,author,publisher,publisherTimes,birthDate,quality,BlNew,price,transPrice,sellDate,bookHref])
            herfSets.add(title)
    except:
        continue
        print("意外中断！")
driver.close()
dataFrame=pd.DataFrame(pieces,columns=columns)
dataFrame.to_csv('C:/Users/zoo/PycharmProjects/LJC/file/demo.csv')
print(dataFrame)
print(herfSets)

