import requests
import json
import re
import os
import threading
book_content = []
book = {}
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
}

def get_chapter(index,name,url):
    try:
        r = requests.get(url=url, headers=headers)
        r.raise_for_status()
        r.encoding = 'utf-8'
        rt = r.text.replace('\n', '')
        text = re.findall('<div class="content".*?>(.*?)<center>', rt)[0].replace('&nbsp;', ' ')
        try:
            text = text.replace('<br />', '\n')
            book_content[index] = name+'\n'+'\n'+text+'\n'+'\n'
            print(name, '成功')
        except:
            print('文本处理错误')
    except:
        print(name,'失败')

def get_book(url):
    chapters = []
    try:
        r = requests.get(url=url, headers=headers)
        r.raise_for_status()
        r.encoding = 'utf-8'
        bcs = re.findall('<dd><a href="(.*?)".*?>(.*?)</a></dd>', r.text.replace('\n', ''))
        for bc in bcs:
            chapter = {}
            a = bc[0]
            if not a.startswith('http'):
                a = 'http://www.biquger.com' + a
            chapter['name'] = bc[1]
            chapter['url'] = a
            chapter['index'] = bcs.index(bc)
            chapters.append(chapter)
        book['name'] = re.findall('<h1>(.*?)</h1>', r.text.replace('\n', ''))[0]
        book['url'] = url
        book['author'] = re.findall('<p>作&nbsp;&nbsp;&nbsp;&nbsp;者：(.*?)</p>', r.text.replace('\n', ''))[0]
        book['chapters'] = chapters
        if not os.path.exists(book['name']):
            os.mkdir(book['name'])
        with open(book['name']+'/book.json','w',encoding='utf-8')as f:
            json.dump(book,f,ensure_ascii=False,indent=4)
            f.close()
        for _ in range(len(chapters)):
            book_content.append('')

        for i in range(len(chapters)%500):
            ts = []
            if (i+1)*500<len(chapters):
                for item in chapters[i*500:(i+1)*500]:
                    t = threading.Thread(target=get_chapter,args=(item['index'],item['name'],item['url']))
                    t.start()
                    ts.append(t)
                for t in ts:
                    t.join()
            else:
                for item in chapters[i*500:]:
                    t = threading.Thread(target=get_chapter,args=(item['index'],item['name'],item['url']))
                    t.start()
                    ts.append(t)
                for t in ts:
                    t.join()
        with open(book['name']+'/'+book['name']+'.txt','w+',encoding='utf-8')as f:
            for i in book_content:
                f.write(i)
            f.close()
        print('爬取小说成功')
    except:
        print('小说下载失败')

def search_book(query):
    url = 'http://www.biquger.com/modules/article/search.php?searchkey='+query
    bookinfos = []
    try:
        r = requests.get(url=url,headers = headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        try:
            bis = re.findall('<tr><td.*?<a href="(.*?)">(.*?)</a></td><td.*?</a></td><td.*?>(.*?)</td>.*?</tr>',r.text.replace('\n',''))
            for bi in bis:
                bookinfo = {}
                bookinfo['name'] = bi[1]
                bookinfo['url'] = bi[0]
                bookinfo['anthor'] = bi[2]
                bookinfo['index'] = bis.index(bi)
                bookinfos.append(bookinfo)
            return bookinfos
        except:
            print('未搜索到相关小说')
            return None
    except:
        print('文章搜索失败')
        return None

if __name__ == '__main__':
    searchname = input('请输入小说名：')
    searchinfo = search_book(searchname)
    print('搜索结果如下：')
    if searchinfo:
        for info in searchinfo:
            print('序号：', info['index'], '\t书名：', info['name'], '\t作者：', info['anthor'])
        print('序号：', info['index'] + 1, '\t取消下载')
        bkindex = int(input('请输入您要下载的序号：'))
        if bkindex < len(searchinfo):
            print('您要下载的是:' + searchinfo[bkindex]['anthor'] + '的' + searchinfo[bkindex]['name'])
            print('正在为您下载……')
            get_book(searchinfo[bkindex]['url'])
        else:
            print('取消下载')