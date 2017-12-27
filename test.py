import json
import random
import socket
import threading
from Tianyancha import Tianyancha
import pymongo
import sys
import time
from config import *
from Gaode import GaoDE_coordinater

client = pymongo.MongoClient(MONGO_URL,connect=False)
db=client[MONGO_DB]


def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到MongoDB成功', result)
        return True
    return False


def get_location(company,ip_list):
    socket.setdefaulttimeout(5)
    usa = random.choice(USER_AGENTS)
    ip = random.choice(ip_list)
    try:
        # coordinater = GaoDE_coordinater.spider(0,company,ip,usa)
        # lon = coordinater.split(",")[0]
        # lat = coordinater.split(",")[1]
        # total = {
        #     "company":company,
        #     "lon":lon,
        #     "lat":lat
        # }
        result = Tianyancha.crawl(0,company,ip,usa)
        save_to_mongo(result)

    except Exception as e:
        print(e)
        print(str(ip) + "不可用,剩余ip数：" + str(len(ip_list)))
        if not ip_list:
            sys.exit()
        if ip in ip_list:
            ip_list.remove(ip)
        get_location(company, ip_list)

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
    ip_list = get_ip_text("ip_pool.txt")
    file = open("company_.txt", encoding="utf-8")
    for line in file:
        line = line.strip()
        print(line)
        t1 = threading.Thread(target=get_location, args=(line, ip_list))
        t1.start()
        time.sleep(1)
    time.sleep(1000)

