import json
import threading
import urllib.parse
import time
from bs4 import BeautifulSoup
import requests
import random
from config import *
import pymongo

client = pymongo.MongoClient(MONGO_URL,connect=False)
db = client[MONGO_DB]

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print("成功存入mongodb"+str(result))
        return True
    return False

def get_company_infor(content,ip_list):
    ip = random.choice(ip_list)
    headers = {
        'Referer': 'https://m.tianyancha.com/?jsid=SEM-BAIDU-PZPC-000000',
        'User-Agent': random.choice(USER_AGENTS)
    }
    keyword = urllib.parse.quote(content)
    url = "https://m.tianyancha.com/search?key=" + keyword + "&checkFrom=searchBox"
    try:
        response = requests.get(url=url, headers=headers,proxies = ip)
        soup = BeautifulSoup(response.text,"lxml")
        if soup.find("a",class_="query_name in-block"):
            name = soup.find("a",class_="query_name in-block").find("span").get_text()
            if soup.find("a",class_="legalPersonName"):
                legalperson =soup.find("a",class_="legalPersonName").get_text()
            else:
                legalperson = ""
            registered_capital = soup.find("div",class_="search_row_new_mobil").find_all("div",class_="title")[1].find("span").get_text()
            registered_time = soup.find("div",class_="search_row_new_mobil").find_all("div",class_="title")[2].find("span").get_text()
            if soup.find("svg"):
                score = soup.find("svg").find("text").get_text()
            else:
                score = ""
            tiany_url = "https://m.tianyancha.com" + soup.find("a",class_="query_name in-block")["href"]

            total = {
                "company":content,
                "get_name": name,
                "legal_person":legalperson,
                "registered_capital": registered_capital,
                "registered_time": registered_time,
                "score": score,
                "url": tiany_url,
            }
            save_to_mongo(total)
        else:
            with open("miss_company.txt","a",encoding="utf-8") as f:
                f.write(content+"\n")
                f.close()

    except Exception as e:
        print(content,e,ip,"不可用")
        if ip in ip_list:
            ip_list.remove(ip)
        get_company_infor(content,ip_list)
    else:
        print("访问状态：",response.status_code)
        if response.status_code!=200:
            get_company_infor(content,ip_list)

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
    print(ip_list)
    file = open("company_detials.txt", encoding="utf-8")
    for line in file:
        line = line.strip()
        print(line)
        t1 = threading.Thread(target=get_company_infor, args=(line, ip_list))
        t1.start()
        time.sleep(1)

