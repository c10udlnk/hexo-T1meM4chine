import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime,timedelta

def convertToLocaltime(t):
    return str(datetime.strptime(t[:19],"%Y-%m-%dT%H:%M:%S")+timedelta(hours=8))

def getHtmlSC(url):
    time.sleep(0.05)
    res=requests.get(url)
    return res.text

def parseAtomXML(url):
    soup=BeautifulSoup(getHtmlSC(url),"lxml-xml")
    titles=[x.string for x in soup.find_all("title")[1:]]
    ids=[x.string for x in soup.find_all("id")[1:]]
    publish_times=[convertToLocaltime(x.string) for x in soup.find_all("published")]
    update_times=[convertToLocaltime(x.string) for x in soup.find_all("updated")[1:]]
    pageInfo={}
    for post in zip(titles,ids,publish_times,update_times):
        pageInfo.update({post[0]:{"id":post[1],"publish_time":post[2],"update_time":post[3]}})
    homePage=soup.find_all(href=True)[1]["href"]
    homeInfo=parseHomePage(homePage)
    return homeInfo,pageInfo

def parseHomePage(url):
    soup=BeautifulSoup(getHtmlSC(url),"lxml")
    key=["Blog_subtitle","Blog_title","Blog_author","Blog_description"]
    value=soup.title.string.split(" | ")+[soup.find(attrs={"name":"author"})["content"],soup.find(attrs={"name":"description"})["content"]]
    return dict(zip(key,value))

def parseHeader(url):
    text=getHtmlSC(url)
    true,false,null='true','false','null'
    info=eval(text)
    key=["Create_time","Last_time"]
    value=[convertToLocaltime(info["created_at"]),(datetime.utcnow()-datetime.strptime(info["created_at"][:19],"%Y-%m-%dT%H:%M:%S")).days]
    return dict(zip(key,value))

def parsePage(url):
    soup=BeautifulSoup(getHtmlSC(url),"lxml")
    key=["wordcount"]
    value=[]
    wordcount=soup.find(class_="word-count").string
    if wordcount[-1]=='k':
        value.append(float(wordcount[:-1]))
    else:
        value.append(round(int(wordcount)/1000,1))
    return dict(zip(key,value))

def makeAnnualReview(homepage,posts,y):
    allWordcnt=0
    for k,v in posts.items():
        v.update(parsePage(v["id"]))
        allWordcnt+=v["wordcount"]
    annualPosts={k:v for k,v in posts.items() if v["publish_time"][:4]==y}
    annualWordcnt=0
    annualposts=""
    for k,v in annualPosts.items():
        annualWordcnt+=v["wordcount"]
        annualposts=k+"\n[>] "+v["id"]+"\n"+annualposts
    key=["blog_author","y_create","m_create","d_create","h_create","min_create","s_create","blog_title","last","num_allPost","sum_allPost","y_first","m_first","d_first","first","num_annualPost","sum_annualPost","allPosts"]
    value=[homepage["Blog_author"]]+homepage["Create_time"][:10].split('-')+homepage["Create_time"][11:].split(':')+[homepage["Blog_title"],homepage["Last_time"],len(posts),allWordcnt]+list(posts.values())[-1]["publish_time"][:10].split('-')+[list(posts.keys())[-1],len(annualPosts),annualWordcnt,annualposts]
    info=dict(zip(key,value))
    fmt="你好呀，{blog_author}！\n{y_create}年{m_create}月{d_create}日{h_create}:{min_create}:{s_create}，\n数字世界中多了一个小世界——{blog_title}，\n距今已经运行了{last}天，\n留有{num_allPost}篇你的足迹，共有{sum_allPost}k字。\n\n{y_first}年{m_first}月{d_first}日，\n你在这里发布了第一篇Blog：《{first}》，\n不知你现在还是否记得TA呢？\n\n这一年来，你推送了{num_annualPost}篇Blog共{sum_annualPost}k字，\n新的一年也要坚持推送Blog呀～\n\n\n2020年新Blogs汇总：\n{allPosts}"
    print(fmt.format(**info))