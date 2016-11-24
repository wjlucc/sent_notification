#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on Wed Nov 23 16:22:43 2016

@author: wjluck
"""

## 这个Python脚本是用来爬取哈工大深圳校园通知的。
## 将'http://www.hitsz.edu.cn/index.php?s=/index/news/fid/138/cid/234.html' 网址下更新的通知发送到指定的邮箱。



import urllib2
from bs4 import BeautifulSoup

import smtplib
from email.header import Header
from email.mime.text import MIMEText

import time

##  获得网页内容
def get_page(url):
    response = urllib2.urlopen(url)
    if response.getcode() == 200: 
        return response.read()
    else:
        return None

##  解析网页内容。返回当前通知的标题，以及通知的最大序号。
def get_news(page):
    news_title = {}
    soup = BeautifulSoup(page, 'html.parser', from_encoding = 'utf-8')
    news_node_set = soup.find('div',class_='news_lista-left f_l').find_all('li')
    for node in news_node_set:
        url = node.find('a').get('href')
        data = node.get_text()
        start = url.find('eid')
        end = url.find('.html')
        label = int(url[start+4:end])
        news_title[label] = (data,url)  
    max_index = max(news_title.keys())
    return news_title,max_index
    
## 过滤之前的内容，生成新内容  
def get_unread_news(news,news_label):
    unread_news = {}    
    max_new = 0
    for num in news:        
        #index = news[num][0].find('2016-')
        #date = news[num][0][index:]        
        url = news[num][1]           
        if(num > news_label):
            key = news[num][0]
            unread_news[num] = (key,url)
        if(num > max_new):
            max_new = num
    news_label = max_new
    return unread_news,news_label

## 生成要发送的文本
def email_content(unread_news):
    order = unread_news.keys()
    order.sort(reverse=True)
    content = ''
    for new in order:
        index = unread_news[new][0].find('2016-')
        date = unread_news[new][0][index:] 
        title = unread_news[new][0][:index]
        url = 'http://www.hitsz.edu.cn' + unread_news[new][1] 
        news = '<p>' +  date + '\t<a href=' + url + '>' + title + '</a></p>'
        content = content + news 
    return content

## 发送邮件，第二个参数是订阅者地址list。  
def send_email(content,subscription):
    server = smtplib.SMTP('smtp.163.com', 25)
    #server.set_debuglevel(1)
    server.login('XXXXXXX@163.com', 'XXX密码****') #这里填写用于发送邮件的邮箱和密码。若使用163邮箱，密码为客户端使用的客户端授权码。
    msg = MIMEText(content, 'html', 'utf-8')         
    msg['From'] = 'HITsz<HITsz@hitsz.edu.cn>'
    msg['Subject'] = Header(u'校园网最新通知', 'utf8').encode()
    msg['To'] = u'dingyuezhe@qq.com'    
    server.sendmail('fasognzhe@163.com', subscription, msg.as_string())
    server.quit()

if __name__ == "__main__":
    news_label = 0
    page_url = 'http://www.hitsz.edu.cn/index.php?s=/index/news/fid/138/cid/234.html'
    subscription = ['SSSSSS@qq.com']    
    while(1):        
        try:            
            
            page = get_page(page_url)
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print  t + '-- get new page'
            
            news,max_news = get_news(page)
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print t + '-- get news'            
            if(max_news == news_label):
                time.sleep(1800)
                continue
            
            unread_news,news_label = get_unread_news(news,news_label)  # 这里用到了 news_label 作为标签，检查是否是已读通知
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print t + '-- get unread news'
            
            content = email_content(unread_news)            
            send_email(content,subscription)
            t =  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print t + '-- send email to ' + str(subscription)
            print 
        except:
            t =  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print t + '-- except occured!'
            time.sleep(1800)
            continue
        time.sleep(1800) # 控制检查新闻的间隔时间，单位为秒
        
    
