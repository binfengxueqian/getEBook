import requests
import json
import re
import os
import threading
import time
import vthread
from getProxies import ProxyIP
import random

# IPPool = ProxyIP.getProxyIPs(ProxyIP,99)

BookContent = []

@vthread.pool(100)
def getText(book):
    # time.sleep(4)
    headers={
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            }
    try:
        response = requests.get(url=book['ChatperUrl'], headers=headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        responseText = response.text.replace('\n', '')
        text = re.findall('<div class="content".*?>(.*?)<center>', responseText)[0].replace('&nbsp;', ' ')
        try:
            text = text.replace('<br />', '\n')
            BookContent[book['index']] = book['ChapterName']+'\n'+text+'\n'+'\n'
            print(book['ChapterName'], '成功')
        except:
            print('文本处理错误')
    except:
        print(book['ChapterName'],'失败')

def getbook(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }
    book = []
    Book = {}
    try:
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        bookChapters = re.findall('<dd><a href="(.*?)".*?>(.*?)</a></dd>', response.text.replace('\n', ''))
        for bookChapter in bookChapters:
            c = {}
            a = bookChapter[0]
            if not a.startswith('http'):
                a = 'http://www.biquger.com' + a
            c['ChapterName'] = bookChapter[1]
            c['ChatperUrl'] = a
            c['index'] = bookChapters.index(bookChapter)
            book.append(c)
        Book['name'] = re.findall('<h1>(.*?)</h1>', response.text.replace('\n', ''))[0]
        Book['url'] = url
        Book['author'] = re.findall('<p>作&nbsp;&nbsp;&nbsp;&nbsp;者：(.*?)</p>', response.text.replace('\n', ''))[0]
        Book['Chapters'] = book
        if not os.path.exists(Book['name']):
            os.mkdir(Book['name'])
        with open(Book['name']+'/Book.json','w',encoding='utf-8')as f:
            json.dump(Book,f,ensure_ascii=False)
            f.close()
        for _ in range(len(book)):
            BookContent.append('')
        for item in book:
            getText(item)
        vthread.pool.close_all()
        while threading.active_count()>2:
            pass

        with open(Book['name']+'/'+Book['name']+'.txt','w+',encoding='utf-8')as f:
            for i in BookContent:
                f.write(i)
            f.close()
        print('爬取小说成功')

    except:
        print('小说下载失败')


getbook('http://www.biquger.com/biquge/102146/')
