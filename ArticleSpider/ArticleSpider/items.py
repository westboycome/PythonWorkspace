# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from ArticleSpider.utils.common import extract_num
from ArticleSpider.settings import SQL_DATATIME_FORMATE
from w3lib.html import remove_tags


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, '%Y/%m/%d').date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums

def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else:
        return value

def return_value(value):
    return value


class ArticleItemLoader(ItemLoader):
    #自定义itemLoader
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )
    content = scrapy.Field()

    def get_insertsql(self):
        insert_sql = """
        insert into jobbole_article(title, create_date, url, url_object_id,front_image_url, front_image_path,  praise_nums, comment_nums, fav_nums, tags, content)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE fav_nums=VALUES(fav_nums), praise_nums = VALUES (praise_nums), comment_nums = VALUES (comment_nums)
        """
        params = (self['title'], self['create_date'], self['url'], self['url_object_id'], self['front_image_url'][0],
        self['front_image_path'], self['praise_nums'], self['comment_nums'], self['fav_nums'], self['tags'], self['content'])
        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insertsql(self):
        #插入知乎question表的sql语句
        insert_sql = """
        insert into zhihu_question(zhihu_id, topics, url, title,content, answer_num,  comments_num, watch_user_num, click_num, crawl_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE content=VALUES (content), answer_num = VALUES (answer_num), comments_num= VALUES (comments_num),
        watch_user_num=VALUES (watch_user_num), click_num = VALUES (click_num)
        """
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]))

        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = int(self["watch_user_num"][1])
        else:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = 0

        crawl_time = datetime.datetime.now().strftime(SQL_DATATIME_FORMATE)
        params = (zhihu_id, topics, url, title, content, answer_num,  comments_num, watch_user_num, click_num, crawl_time)
        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_tiem = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insertsql(self):
        #插入知乎answer表的sql语句 主键冲突的时候只更新数据
        insert_sql = """
        insert into zhihu_answer(zhihu_id, url, question_id, author_id,content, parise_num, comments_num, create_tiem, update_time, crawl_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE content=VALUE (content), comments_num=VALUE (comments_num), parise_num = VALUE (parise_num), update_time = VALUE (update_time)
        """
        create_tiem = datetime.datetime.fromtimestamp(self["create_tiem"]).strftime(SQL_DATATIME_FORMATE)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATATIME_FORMATE)
        crawl_time = self["crawl_time"].strftime(SQL_DATATIME_FORMATE)
        params = (self["zhihu_id"], self["url"], self["question_id"], self["author_id"],
                  self["content"], self["parise_num"], self["comments_num"],
                  create_tiem, update_time, crawl_time)
        return insert_sql, params


def remove_splash(value):
    #去掉工作城市的斜线
    return value.replace("/", "")


def handel_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != '查看地图']
    return "".join(addr_list)

class LagouItemLoader(ItemLoader):
    #自定义itemLoader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    #拉勾网职位信息
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    tags = scrapy.Field(
        input_processor= Join(",")
    )
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handel_jobaddr)
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insertsql(self):
        insert_sql = """
            insert into lagou(url,url_object_id,title,salary,job_city,work_years,degree_need,job_type
            ,publish_time,tags,job_advantage,job_desc,job_addr,company_name,company_url,crawl_time)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary=VALUE (salary), work_years=VALUE (work_years),
            job_desc = VALUE (job_desc), update_time = VALUE (update_time)
        """
        params = (
            self["url"], self["url_object_id"], self["title"], self["salary"], self["job_city"], self["work_years"],
            self["degree_need"], self["job_type"], self["publish_time"], self["tags"], self["job_advantage"],
            self["job_desc"], self["job_addr"], self["company_name"], self["company_url"], self["crawl_time"].strftime(SQL_DATATIME_FORMATE)
        )
        return insert_sql, params
