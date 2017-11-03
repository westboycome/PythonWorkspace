# _*_ coding:utf-8 _*_

from selenium import webdriver
from scrapy.selector import Selector

browser = webdriver.Chrome(executable_path="E:/github-project/drive/chromedriver.exe")
# browser.get("https://detail.tmall.hk/hk/item.htm?id=536341445378&spm=875.7931836/B.2017041.7.f92af4eoVLijK&scm=1007.12144.81309.73133_0&pvid=37d595f0-55f5-4821-ac9e-8e30bd4bde88")
# browser.get("https://www.zhihu.com/#signin")
# browser.get("http://weibo.com/")
browser.get("http://www.oschina.net/")


# print(browser.page_source)
# t_selector = Selector(text=browser.page_source)
# print(t_selector.css(".tm-promo-price .tm-yen::text").extract())
# browser.find_element_by_css_selector(".account input-wrapper input[name='account']").send_keys("476878873@qq.com")
# browser.find_element_by_css_selector("verification input-wrapper input[name='password']").send_keys("lfh05121439")
# browser.find_element_by_css_selector(".button-wrapper button.sign-button").click()

#selenium 完成微博登录

import time
time.sleep(10)
browser.find_element_by_css_selector("#loginname").send_keys("")
browser.find_element_by_css_selector(".info_list password input[node-type='password']").send_keys("")
browser.find_element_by_css_selector(".info_list login_btn a[node-type='submitBtn']").click()

#鼠标自动下拉
for i in range(10):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scroillHeight; return lenOfPage;")
# browser.quit()

#设置chromedrive 不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.amgaged_default_content_settings.images": 2}
chrome_opt.add_experimental_option("prefs", prefs)

#phantomjs 无界面的浏览器，多进程情况下phantomjs性能会下降很严重
browser2 = webdriver.Chrome(executable_path="")
browser2.get("")
print(browser2.page_source)
