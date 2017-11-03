# -*- coding: utf-8 -*-
__author__ = 'bobby'

import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")

agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
header = {
    "HOST": "www.zhihu.com",
    "Referer": "https://www.zhizhu.com",
    'User-Agent': agent
}


def is_login():
    #通过个人中心页面返回状态码来判断是否为登录状态
    inbox_url = "https://www.zhihu.com/question/56250357/answer/148534773"
    response = session.get(inbox_url, headers=header, allow_redirects=False)
    if response.status_code != 200:
        return False
    else:
        return True


def get_xsrf():
    #获取xsrf code
    response = session.get("https://www.zhihu.com", headers=header)
    match_obj = re.search(r'.*value="(.*?)"', response.text)
    if match_obj:
        return (match_obj.group(1))
    else:
        return ""


def get_index():
    response = session.get("https://www.zhihu.com", headers=header)
    with open("index_page.html", "wb") as f:
        f.write(response.text.encode("utf-8"))
    print("ok")


def get_yzm():
    import time
    t = str(int(time.time()*1000))
    url = "https://www.zhihu.com/captcha.gif?r={0}&type=login&lang=cn".format(t)
    #不能用request请求
    t = session.get(url, headers=header)
    with open("yzm.jpg", "wb") as f:
        f.write(t.content)
        f.close()

    from PIL import Image
    try:
        im = Image.open("yzm.jpg")
        im.show()
        im.close()
    except:
        pass
    #[[18.5,20.6094],[39.5,27.6094],[71.5,26.6094],[88.5,26.6094],[108.5,20.6094],[138.5,26.6094],[167.5,15.60938]]
    print("[[18.5,20.6094],[39.5,27.6094],[71.5,26.6094],[88.5,26.6094],[108.5,20.6094],[138.5,26.6094],[167.5,15.60938]]")
    yzm = input("输入验证码\n")
    return yzm


def zhihu_login(account, password):
    #知乎登录
    if re.match("^1\d{10}",account):
        print ("手机号码登录")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password,
            "captcha_type": "cn",
            "captcha": {"img_size": '[200, 44]',
                        "input_points": get_yzm()}
        }
    else:
        if "@" in account:
            #判断用户名是否为邮箱
            print("邮箱方式登录")
            post_url = "https://www.zhihu.com/login/email"
            post_data = {
                "_xsrf": get_xsrf(),
                "email": account,
                "password": password,
                "captcha_type": "cn",
               "captcha": {"img_size": '[200, 44]', "input_points": get_yzm()}
            }

    response_text = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()

zhihu_login("476878873@qq.com", "lfh05124139")
#get_index()
# get_xsrf()
#get_yzm()