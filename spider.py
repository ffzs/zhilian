#encoding:utf-8
import socket
import threading
import pymongo
import random
import json
import requests
import time
import sys
from bs4 import BeautifulSoup
from lxml import etree
from config import *
from Gaode import GaoDE_coordinater
from Tianyancha import Tianyancha

client = pymongo.MongoClient(MONGO_URL,connect=False)
db=client[MONGO_DB]

def get_average(job_sal):
    cut = job_sal.split("-")
    s = 0
    if len(cut)==2:
        for item in cut:
            if "万" in item:
                p = item[:-1]
                q = int(float(p) * 10000)
                # print(p,q)
            else:
                p = item[:-1]
                q = int(float(p) * 1000)
            s += q
    return int(s/len(cut))

def get_job_details(job_url,ip_list):
    usa =  random.choice(USER_AGENTS)
    headers = {
        'Referer': 'https://m.zhaopin.com/beijing-530/?keyword=python&order=0&maprange=3&ishome=0',
        'User-Agent':usa,
    }
    a ,b= " ",","
    about_job, tags = [], []
    ip = random.choice(ip_list)
    try:
        request = requests.get(job_url, headers=headers,proxies=ip)
        selector = etree.HTML(request.text)
        job_name = selector.xpath('//*[@id="r_content"]/div[1]/div/div[1]/div[1]/h1/text()')
        if job_name:
            job_sal = selector.xpath('//*[@id="r_content"]/div[1]/div/div[1]/div[1]/div[1]/text()')[0]
            average_sal = get_average(job_sal)
            company_name = selector.xpath('//*[@id="r_content"]/div[1]/div/div[1]/div[2]/text()')[0]
            company_address = selector.xpath('//*[@id="r_content"]/div[1]/div/div[2]/div/text()')
            if company_address:
                pass
            else:
                company_address =[""]
            coordinate = GaoDE_coordinater.spider(a, company_address[0],ip,usa)
            job_code = job_url.split("/")[-2]
            about_main = BeautifulSoup(request.text, 'lxml').find_all('div', class_="about-main")
            if about_main:
                pass
            else:
                about_main = BeautifulSoup(request.text, 'lxml').find_all('div', class_="about-main")
            for p in about_main:
                about_job.append(p.get_text().strip())
            about_job = a.join(about_job)
            # if KEYWORD in (str(about_job)+str(job_name[0])):
            all_tag = BeautifulSoup(request.text, 'lxml').find_all('span', class_="tag")
            tag_number = len(all_tag)
            for tag in all_tag:
                tags.append(tag.get_text())
            tag = b.join(tags)
            company_condition = Tianyancha.crawl(a,company_name,ip,usa)
            if company_condition:
                pass
            else:
                company_condition ={}
            total = {
                "工作编号":job_code,
                "工作名称": job_name[0],
                "工资范围": job_sal,
                "参考平均工资":average_sal,
                "公司名称": company_name,
                "公司地址": company_address[0],
                "位置坐标":coordinate,
                "工作详情": about_job,
                "工作标签": tag,
                "工作标签数":tag_number,
                "智联网址":job_url,
            }
            # print(total,company_condition)
            result = {**total,**company_condition}
            if lock.acquire():
                save_to_mongo(result)
                with open("ip_zhilian.txt", "a") as file:
                    file.write(json.dumps(ip) + "\n")
                    file.close()
                lock.release()
    except Exception as e:
        print(e)
        print(str(ip) + "不可用,剩余ip数：" + str(len(ip_list)))
        if not ip_list:
            sys.exit()
        if ip in ip_list:
            ip_list.remove(ip)
        get_job_details(job_url, ip_list)
    else:
        print(str(ip) + "可用###剩余ip数：" + str(len(ip_list)) + "###网络状态：" + str(request.status_code))
        if request.status_code != 200:
            if ip in ip_list:
                ip_list.remove(ip)

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到MongoDB成功', result)
        return True
    return False

def get_job_url(url,ip_list):
    socket.setdefaulttimeout(5)
    headers1 = {
        'Referer': 'https://m.fang.com/zf/bj/?jhtype=zf',
        'User-Agent': random.choice(USER_AGENTS)
    }
    try:
        ip = random.choice(ip_list)
    except:
        return False
    else:
        proxies = ip
    try:
        request = requests.get(url,headers=headers1,proxies=proxies)
        all_a = BeautifulSoup(request.text,'lxml').find_all('a',class_="boxsizing")
        for a in all_a:
            job_url = 'https://m.zhaopin.com'+a["data-link"]
            t1 = threading.Thread(target=get_job_details,args=(job_url,ip_list))
            t1.start()
            time.sleep(0.5)

    except Exception as e:
        print(e)
        print(str(ip) + "不可用,剩余ip数：" + str(len(ip_list)))
        if not ip_list:
            sys.exit()
        if ip in ip_list:
            ip_list.remove(ip)
        get_job_url(url, ip_list)
    else:
        print(str(ip) + "可用###剩余ip数：" + str(len(ip_list)) + "###网络状态："+str(request.status_code))
        if request.status_code != 200:
            if ip in ip_list:
                ip_list.remove(ip)

def get_ip_text(file):
    file = open(file)
    ip_list =[]
    for line in file:
        try:
            ip_list.append(json.loads(line.strip()))
        except:
            pass
    return ip_list

if __name__ == '__main__':
    lock = threading.Lock()
    IP_LIST = get_ip_text("ip_pool.txt")
    for page in range(457,600):
        print("--------------正在爬第" + str(page) + "页-----------------")
        a_url = 'https://m.zhaopin.com/' + CITY + '/?keyword=' + KEYWORD + '&pageindex=' + str(
            page) + '&maprange=3&publishdate=30&islocation=0'
        get_job_url(a_url,IP_LIST)


