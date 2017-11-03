# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
import datetime

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from scrapy.loader import ItemLoader
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    # def __init__(self):
    #     self.browser = webdriver.Chrome(executable_path="E:/github-project/drive/chromedriver.exe")
    #     super(JobboleSpider, self).__init__()
    #     dispatcher.connect(self.spider_closed, signals.spider_closed)
    #
    # def spider_closed(self, spider):
    #     #当爬出退出的时候 关闭chrome
    #     print("soider closed")
    #     self.browser.quit()

    def __init__(self):
        self.fail_urls = []

    def parse(self, response):
        #解析列表页中的所有文章url并交给scrapy下载后进行解析
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url),meta={"front_image_url":image_url}, callback=self.parise_detail)

        #scrapy数据收集器
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")

        #提取下一页
        next_url = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parise_detail(self, response):
        # title = response.xpath('//*[@class="entry-header"]/h1/text()').extract()[0]
        # create_time = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace(".", "")
        # praise_nums = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract()[0]
        # fav_nums = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract()[0]
        # match_re = re.match(".*?(\d+).*", fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        # comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        # match_re = re.match(".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        # content = response.xpath('//div[@class="entry"]').extract()[0]
        # tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # # 去重
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ','.join(tag_list)

        article_item = JobBoleArticleItem()

        # 通过css选择器获取字段
        front_image_url = response.meta.get("front_image_url")
        title = response.css(".entry-header h1::text").extract()[0]
        create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace('.', '')
        praise_nums = response.css('span.vote-post-up h10::text').extract()[0]
        fav_nums = response.css('.bookmark-btn::text').extract()[0]
        match_re = re.match(".*?(\d+).*", fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0
        comment_nums = response.css('a[href="#article-comment"] span::text').extract()[0]
        match_re = re.match(".*?(\d+).*", comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0
        content = response.css('div.entry').extract()[0]
        tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        tags = ','.join(tag_list)

        article_item["title"] = title
        article_item["url"] = response.url
        article_item["url_object_id"] = get_md5(response.url)
        try:
            create_date = datetime.datetime.strptime(create_date, '%Y/%m/%d').date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        article_item["create_date"] = create_date
        article_item["front_image_url"] = [front_image_url]
        article_item["praise_nums"] = praise_nums
        article_item["comment_nums"] = comment_nums
        article_item["fav_nums"] = fav_nums
        article_item["tags"] = tags
        article_item["content"] = content

        #通过item_load加载item
        item_load = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_load.add_css("title", ".entry-header h1::text")
        item_load.add_value("url", response.url)
        item_load.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_load.add_css("praise_nums", "span.vote-post-up h10::text")
        item_load.add_css("fav_nums", ".bookmark-btn::text")
        item_load.add_css("comment_nums", 'a[href="#article-comment"] span::text')
        item_load.add_css("content", "div.entry")
        item_load.add_css("tags", "p.entry-meta-hide-on-mobile a::text")

        article_item = item_load.load_item()

        yield article_item
