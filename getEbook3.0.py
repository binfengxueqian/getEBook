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

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
}
# @vthread.pool(100)
def getText(index,name,url):
    # time.sleep(4)
    try:
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        responseText = response.text.replace('\n', '')
        text = re.findall('<div class="content".*?>(.*?)<center>', responseText)[0].replace('&nbsp;', ' ')
        try:
            text = text.replace('<br />', '\n')
            BookContent[index] = name+'\n'+text+'\n'+'\n'
            print(name, '成功')
        except:
            print('文本处理错误')
    except:
        print(name,'失败')

def getbook(url):
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
            json.dump(Book,f,ensure_ascii=False,indent=4)
            f.close()
        for _ in range(len(book)):
            BookContent.append('')
        ts = []
        for item in book:
            t = threading.Thread(target=getText,args=(item['index'],item['ChapterName'],item['ChatperUrl']))
            t.start()
            ts.append(t)
        for t in ts:
            t.join()
        # vthread.pool.close_all()
        # while threading.active_count()>2:
        #     pass

        with open(Book['name']+'/'+Book['name']+'.txt','w+',encoding='utf-8')as f:
            for i in BookContent:
                f.write(i)
            f.close()
        print('爬取小说成功')

    except:
        print('小说下载失败')

def getBook(query):
    url = 'http://www.biquger.com/modules/article/search.php?searchkey='+query
    print(url)
    try:
        response = requests.get(url=url,headers = headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        try:
            responseText1 = response.text.replace('\n','')
            bookinfo_1 = re.findall('<tr><td.*?<a href="(.*?)">(.*?)</a></td><td.*?</a></td><td.*?>(.*?)</td>.*?</tr>',responseText1)

            bookinfos = []
            print('搜索结果如下：')
            for i in bookinfo_1:
                bookinfo = {}
                bookinfo['BookName'] = i[1]
                bookinfo['BookUrl'] = i[0]
                bookinfo['anthor'] = i[2]
                bookinfo['index'] = bookinfo_1.index(i)
                bookinfos.append(bookinfo)
                print('序号：',bookinfo['index'],'\t书名：',bookinfo['BookName'],'\t作者：',bookinfo['anthor'])
            print('序号：',bookinfo['index']+1,'\t取消下载')
            bkindex = int(input('请输入您要下载的序号：'))
            if bkindex<len(bookinfos):
                print('您要下载的是:'+bookinfos[bkindex]['anthor']+'的'+bookinfos[bkindex]['BookName'])
                print('正在为您下载……')
                getbook(bookinfos[bkindex]['BookUrl'])
            else:
                print('取消下载')
        except:
            print('文章搜索解析失败')
    except:
        print('文章搜索失败')

Bookname = input('请输入小说名：')
getBook(Bookname)
