# _*_coding:_utf-8 _*_
import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='123456', db="python", charset='utf8')
cursor = conn.cursor()


def crawl_ips():
    #爬取西刺的免费ip代理
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"}
    for i in range(2460):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)
        selector = Selector(text=re.text)
        all_trs = selector.css("#ip_list tr")

        ip_lists = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])
            all_texts = tr.css("td::text").extract()

            ip = all_texts[0]
            port = all_texts[1]
            proxy_type = all_texts[5]

            ip_lists.append((ip, port, proxy_type, speed))

        for ip_info in ip_lists:
            cursor.execute(
                "insert proxy_ip(ip, port, speed, proxy_type) VALUE('{0}', '{1}', {2}, 'HTTP')".format(
                    ip_info[0], ip_info[1], ip_info[3]
                )
            )
            conn.commit()


class GetIP(object):
    def delete_ip(self, ip):
        #从数据库中删除无效的ip
        delete_sql = "delete from proxy_ip WHERE ip = '{0}'".format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port):
        #判断ip是否可用
        http_url = "http://www.baidu.com"
        proxy_ur = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_ur,
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code <= 300:
                print("effective ip")
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        #从数据库随机获取一个ip
        random_sql = "select ip, port from proxy_ip ORDER By RAND() limit 1"
        result = cursor.execute(random_sql)
        for ip_infor in cursor.fetchall():
            ip = ip_infor[0]
            port = ip_infor[1]

            judge_ip = self.judge_ip(ip, port)
            if judge_ip:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()

# print(crawl_ips())
if __name__ == "__main__":
    get_ip = GetIP()
    get_ip.get_random_ip()