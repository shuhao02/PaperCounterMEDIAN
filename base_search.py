import requests
from bs4 import BeautifulSoup
import xlwt, os
from time import sleep
from tqdm import tqdm

def find_cite(ref):
    r = requests.get(ref, headers=head)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "html.parser")
    if soup.find(class_='gs_fl gs_flb gs_invis') != None:
        for i in soup.find(class_='gs_fl gs_flb gs_invis').find_all('a'):
            if 'cites=' in i.get('href'):
                return i.get('href').split('cites=')[-1].split('&')[0]
            
    for i in soup.find_all(class_='gs_fl'):
        for j in i.find_all('a'):
            if 'cites=' in j.get('href'):
                print("选择了第一个相关的文章，请二次确认其正确性: " 'https://scholar.google.com' + j.get('href'))
                return j.get('href').split('cites=')[-1].split('&')[0]
    sleep(sleep_time + 0.001)
    print("没有找到对应的文章！")
    return None

def find_home(ref):
    sleep(sleep_time + 0.002)
    r = requests.get(ref, headers=head)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "html.parser")
    articles = soup.find_all(class_="gs_ri")
    for s in soup.find_all(class_='gsc_prf_ila'):
        if s.text == '首页':
            return s.get('href')
    sleep(sleep_time + 0.0005)
    return None

class Article(object):
    title = ""
    article_link = ""
    authors = ""
    authors_links = []
    journal = ""
    def __init__(self):
        title = "New Paper"

def print_articles(articles, sheet):
    for article in articles:
        paper = Article()
        title_name = ''
        try: 
            title = article.find('h3')
            paper.title = title.text
            title_name = title.text
            paper.article_link = title.a.get('href')

            journal = article.find(class_="gs_a")
            paper.journal =journal.text

            authors_addrs = journal.find_all('a')
            paper.authors_links = []
            for authors_addr in authors_addrs:
                paper.authors_links.append(authors_addr.get('href'))
            
            save_xls(sheet, paper)
#             abstract = article.find(class_="gs_rs")
#             paper.abstract = abstract.text
        except:
            if title_name != '':
                print("丢失文章信息：", title_name)
            continue
        

def save_xls(sheet, paper):
    global TotalNum
    global PaperNum
    # print("正在保存文章信息：", PaperNum, paper.title)
    sheet.write(TotalNum, 0, PaperNum)
    sheet.write(TotalNum, 1, paper.title)
    sheet.write(TotalNum, 2, paper.article_link)
    sheet.write(TotalNum, 3, paper.journal.split('-')[1])
    sheet.write(TotalNum, 4, paper.journal.split('-')[0])
    for i in paper.authors_links:
        sheet.write(TotalNum, 5, 'https://scholar.google.com'+i.split('&hl')[0])
        home = find_home('https://scholar.lanfanshu.cn'+i.split('&hl')[0])
        if home != None:
            sheet.write(TotalNum, 6, ''+home)
        TotalNum+=1
    TotalNum += 1
    PaperNum += 1


head = {'user-agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre"}
TotalNum=0
PaperNum=0
sleep_time = 0.1

def generate_author_link(paper_title):
    head = {'user-agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre"}
    TotalNum=0
    PaperNum=0
    sleep_time = 0.1
    paper_link = 'https://scholar.lanfanshu.cn/scholar?q=%s' % paper_title
    cite_id = find_cite(paper_link)
    if cite_id is None:
        exit(1)
    
    myxls = xlwt.Workbook()
    sheet1 = myxls.add_sheet(u'PaperInfo', True)
    column = ['序号', '文章题目','文章链接','期刊', '作者', '作者链接', '作者网页']
    for i in range(0, len(column)):
        sheet1.write(TotalNum, i, column[i])
    TotalNum+=1

    start = 0
    for i in tqdm(range(10)):
        if start == 0:
            ref = 'https://scholar.lanfanshu.cn/scholar?hl=zh-CN&as_sdt=2005&sciodt=0,5&cites=' + str(cite_id)
        else:
            ref = 'https://scholar.lanfanshu.cn/scholar?start='+ str(start) +'&hl=zh-CN&as_sdt=2005&sciodt=0,5&cites=' + str(cite_id)
        # print('使用的网址：', ref)
        try:
            r = requests.get(ref, headers=head)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, "html.parser")
            articles = soup.find_all(class_="gs_ri")
            print_articles(articles, sheet1)
            sleep(sleep_time + 0.003)
            start = start + 10
            if len(articles) == 0:
                break
        except:
            break

    myxls.save('data/PaperInfo_%s.xls' % paper_title)

if __name__ == '__main__':
    paper_title = input("请输入所需要检索的文章名：")
    paper_link = 'https://scholar.lanfanshu.cn/scholar?q=%s' % paper_title
    cite_id = find_cite(paper_link)
    if cite_id is None:
        exit(1)
    
    myxls = xlwt.Workbook()
    sheet1 = myxls.add_sheet(u'PaperInfo', True)
    column = ['序号', '文章题目','文章链接','期刊', '作者', '作者链接', '作者网页']
    for i in range(0, len(column)):
        sheet1.write(TotalNum, i, column[i])
    TotalNum+=1

    start = 0
    for i in tqdm(range(10)):
        if start == 0:
            ref = 'https://scholar.lanfanshu.cn/scholar?hl=zh-CN&as_sdt=2005&sciodt=0,5&cites=' + str(cite_id)
        else:
            ref = 'https://scholar.lanfanshu.cn/scholar?start='+ str(start) +'&hl=zh-CN&as_sdt=2005&sciodt=0,5&cites=' + str(cite_id)
        # print('使用的网址：', ref)
        try:
            r = requests.get(ref, headers=head)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, "html.parser")
            articles = soup.find_all(class_="gs_ri")
            print_articles(articles, sheet1)
            sleep(sleep_time + 0.003)
            start = start + 10
            if len(articles) == 0:
                break
        except:
            break

    myxls.save('data/PaperInfo_%s.xls' % paper_title)