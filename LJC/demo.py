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
columns=['code','title','ISBN','author','publisher','birthDate','quality','BlNew','price','transPrice','sellDate','bookHref']
i=900
herfSets=set()
for pages in range(1,101):
    page=101-pages
    path='http://book.kongfz.com/Cyiyao/xsv6w%d/'%page
    print(path)
    res = requests.get(path,headers=headers)
    doc = pq(res.text)
    # listBox > div:nth-child(1) > div.item-info > div.title > a
    item_doc = doc('#listBox > div')
    for item in item_doc.items():

        # listBox > div:nth-child(1) > div.item-info > div.title > a
        title = item("div.item-info > div.title > a").text().replace("/","").replace(" ","")
        bookHref = item("div.item-info > div.title > a").attr("href")
        if(bookHref in herfSets):
            continue
        isbn=findISBN(bookHref)
        itemInfo=item("div.item-info>div.zl-isbn-info>span.text")
        author=itemInfo.eq(0).text().replace("/","").replace(" ","")
        publisher=itemInfo.eq(1).text().replace("/","").replace(" ","")
        birthDate=itemInfo.eq(2).text().replace("/","").replace(" ","")
        if(birthDate[0:4]>'2015'):
            continue

        quality=itemInfo.eq(3).text().replace("/","").replace(" ","")
        itemOtherInfo= item("div.item-other-info")
        BlNew=itemOtherInfo("div.first-info.clearfix > div.quality.bold.gray3").text()
        price=itemOtherInfo("div.first-info.clearfix > div.f_right.red.price > span.bold").text()
        if(price<'5'):
            continue

        herfSets.add(bookHref)
        transPrice=itemOtherInfo("div.ship-fee-box > div> span:nth-child(2)").text()
        sellDate=itemOtherInfo("div.add-time-box > span:nth-child(1)").text()

        i = i + 1
        #img_url = item("div.item-img > a > img").attr("src")
        img_url=findPic(bookHref)
        if img_url is None:
            img_url = item("div.item-img > a > img").attr("src")
        path="C:/Users/zoo/PycharmProjects/LJC/file/pic"
        names="/"+str(i)+".jpg"
        downloadfile = wget.download(img_url,out=path, bar=None)
        os.rename(downloadfile,path+names)
        pieces.append([i,title,isbn,author,publisher,birthDate,quality,BlNew,price,transPrice,sellDate,bookHref])

dataFrame=pd.DataFrame(pieces,columns=columns)
dataFrame.to_csv('C:/Users/zoo/PycharmProjects/LJC/file/demo.csv')
print(dataFrame)
print(herfSets)

