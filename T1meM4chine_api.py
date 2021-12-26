# -*- coding: UTF-8 -*-

# Author: c10udlnk(https://github.com/c10udlnk)
# Author's blog: https://c10udlnk.top/
# Github repo: https://github.com/c10udlnk/hexo-T1meM4chine
# Enjoy it!

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime, timedelta

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

def setColor(string, color):
    colorfulString = {"content": string, "color": color}
    return "\x1b[38;5;{color}m{content}\x1b[0m".format(**colorfulString)

def printMenu():
    print(setColor("\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n", 4))
    print(setColor("正在生成你的HEXO博客时光机~\n", 6))
    print(setColor("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n", 4))

def getHtmlSC(url):
    res = session.get(url)
    res.encoding = 'utf-8'
    return res.text

def convertToLocaltime(t):
    return str(datetime.strptime(t[:19], "%Y-%m-%dT%H:%M:%S") + timedelta(hours = 8))

def parseHomePage(url):
    soup = BeautifulSoup(getHtmlSC(url), "lxml")
    key = ["Blog_title", "Blog_author", "Blog_description"]
    value = [soup.title.string, soup.find(attrs = {"name":"author"})["content"], soup.find(attrs = {"name":"description"})["content"]]
    return dict(zip(key, value))

def parseAtomXML(url):
    soup = BeautifulSoup(getHtmlSC(url), "lxml-xml")
    titles = [x.string for x in soup.find_all("title")[1:]]
    ids = [x.string for x in soup.find_all("id")[1:]]
    publish_times = [convertToLocaltime(x.string) for x in soup.find_all("published")]
    update_times = [convertToLocaltime(x.string) for x in soup.find_all("updated")[1:]]
    pageInfo = {}
    for post in zip(titles, ids, publish_times, update_times):
        pageInfo.update({post[0]: {"id": post[1], "publish_time": post[2], "update_time": post[3]}})
    homePage = soup.find_all(href = True)[1]["href"]
    homeInfo = parseHomePage(homePage)
    return homeInfo, pageInfo

def parseHeader(url):
    text = getHtmlSC(url)
    true, false, null = 'true', 'false', 'null'
    info = eval(text)
    key = ["Create_time", "Last_time"]
    value = [convertToLocaltime(info["created_at"]), (datetime.utcnow()-datetime.strptime(info["created_at"][:19], "%Y-%m-%dT%H:%M:%S")).days]
    return dict(zip(key, value))

def parsePage(url):
    soup = BeautifulSoup(getHtmlSC(url), "lxml")
    # 暂不支持Slides的字数统计
    if soup.find(class_="reveal") is not None:
        return {}
    key = ["wordcount"]
    value = []
    wordcount = soup.find(class_="word-count").string
    if wordcount[-1] == 'k':
        value.append(float(wordcount[:-1]))
    else:
        value.append(round(int(wordcount)/1000, 1))
    return dict(zip(key, value))

def makeAnnualReview(homepage, posts, y):
    allWordcnt = 0
    for k, v in posts.items():
        v.update(parsePage(v["id"]))
        if "wordcount" in v.keys():
            allWordcnt += v["wordcount"]
    annualPosts = {k: v for k, v in posts.items() if v["publish_time"][:4] == y}
    annualWordcnt = 0
    annualposts = ""
    for k, v in annualPosts.items():
        if "wordcount" in v.keys():
            annualWordcnt += v["wordcount"]
        annualposts = setColor(k, 9) + setColor("\n[>] ", 9) + setColor(v["id"], 14) + "\n" + annualposts
    info = {
        "year": y,
        "blog_author": homepage["Blog_author"],
        "blog_title": homepage["Blog_title"],
        "last": homepage["Last_time"],
        "firstPost": list(posts.keys())[-1],
        "allPost_cnt": len(posts),
        "allPost_sum": allWordcnt,
        "annualPost_cnt": len(annualPosts),
        "annualPost_sum": annualWordcnt,
        "allPosts": annualposts
    }
    key = ["y_create", "m_create", "d_create", "h_create", "min_create", "s_create", "y_first", "m_first", "d_first"]
    value =homepage["Create_time"][:10].split('-') + homepage["Create_time"][11:].split(':') + list(posts.values())[-1]["publish_time"][:10].split('-')
    info.update(dict(zip(key, value)))
    fmt = setColor("你好呀，{blog_author}！\n{y_create}年{m_create}月{d_create}日{h_create}:{min_create}:{s_create}，\n数字世界中多了一个小世界——{blog_title}，\n距今已经运行了{last}天，\n留有{allPost_cnt}篇你的足迹，共有{allPost_sum:0.2f}k字。\n\n{y_first}年{m_first}月{d_first}日，\n你在这里发布了第一篇Blog：《{firstPost}》，\n不知你现在还是否记得TA呢？\n\n这一年来，你推送了{annualPost_cnt}篇Blog共{annualPost_sum:0.2f}k字，\n新的一年也要坚持推送Blog呀～\n\n\n", 13) + setColor("{year}年新Blogs汇总：\n{allPosts}", 54)
    print(fmt.format(**info))