import urllib.parse
import requests
from lxml import etree
import random


class Tianyancha(object):

    def __init__(self):
        pass

    def crawl(self,content,ip,usa):
        headers = {
                    'Referer': 'https://m.tianyancha.com/?jsid=SEM-BAIDU-PZPC-000000',
                    'User-Agent': usa
                }

        keyword =urllib.parse.quote(content)
        url = "https://m.tianyancha.com/search?key="+keyword+"&checkFrom=searchBox"
        requset = requests.get(url=url, headers=headers, proxies=ip).text
        selector = etree.HTML(requset)
        com_name = selector.xpath('/html/body/div[2]/div[4]/div[1]/div[1]/div[1]/a/span/em/text()')
        if com_name:
            tiany_url = "https://m.tianyancha.com"+selector.xpath('/html/body/div[2]/div[4]/div[1]/div[1]/div[1]/a/@href')[0]
            capital = selector.xpath('/html/body/div[2]/div[4]/div[1]/div[4]/div/div/div[2]/span/text()')[0]
            register_time = selector.xpath('/html/body/div[2]/div[4]/div[1]/div[4]/div/div/div[3]/span/text()')[0]
            score = selector.xpath('/html/body/div[2]/div[4]/div[1]/div[4]/div/svg/text[1]/text()')[0]
            all = {
                "公司":com_name[0],
                "注册资金":capital,
                "注册时间":register_time,
                "得分":score,
                "详情地址":tiany_url,
            }
            return all

if __name__ == '__main__':
    content = "北京布雷恩科技有限公司"
    app = Tianyancha()
    usa = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0"
    ip = {"http": "http://183.129.160.75:3128"}
    a = app.crawl(content,ip,usa)
    print(a)