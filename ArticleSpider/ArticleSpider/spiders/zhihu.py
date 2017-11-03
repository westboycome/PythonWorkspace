# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
import random

from urllib import parse
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuAnswerItem, ZhihuQuestionItem
from ArticleSpider.settings import user_agent_list


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    #question第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={1}&limit={2}&sort_by=default"
    random_index = random.randint(0, len(user_agent_list)-1)
    random_agent = user_agent_list[random_index]
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': random_agent
    }
    #配置setting参数
    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        """
        提取html中的所有url 并跟踪这些url进一步爬取
        """
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_qustion)
            else:
                # yield scrapy.Request(url, headers=self.headers, callback=self.parse)
                pass

    def parse_qustion(self, response):
        #处理question页面，提取出item
        match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        if match_obj:
            question_id = match_obj.group(2)
        if "QuestionHeader-title" in response.text:
            item_load = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_load.add_css("title", "h1.QuestionHeader-title::text")
            item_load.add_css('content', ".QuestionHeader-detail span::text")
            item_load.add_value("url", response.url)
            item_load.add_value("zhihu_id", question_id)
            item_load.add_css("answer_num", ".List-headerText span::text")
            item_load.add_css("comments_num", ".QuestionHeader-Comment button::text")
            item_load.add_css("watch_user_num", ".NumberBoard-value::text")
            item_load.add_css("topics", ".QuestionHeader-topics .Popover div::text")
            question_item = item_load.load_item()
        else:
            item_load = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_load.add_xpath("title", "//*[@id='zh-question-title']/h2/a/text()|//*[@id='zh-question-title']/h2/span/text()")
            item_load.add_css('content', '#zh-question-detail::text')
            item_load.add_value("url", response.url)
            item_load.add_value("zhihu_id", question_id)
            item_load.add_css("answer_num", ".List-headerText span::text")
            item_load.add_css("comment_num", "#zh-question-meta-wrap a[name='addcomment']::text")
            item_load.add_xpath("watch_user_num", "//*[@id='zh-question-side-header-wrap']/text()|//*[@id='zh-question-followers-sidebar']/div/a/strong/text()")
            item_load.add_css("topics", ".zm-tag-editor-labels .a::text")
            question_item = item_load.load_item()

        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        totals_answer = ans_json["paging"]["totals"]
        next_url = ans_json["paging"]["next"]
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["parise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_tiem"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
            yield answer_item
        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

        # item_load = ItemLoader(item=ZhihuQuestionItem, response=response)
        # item_load.add_css('title', 'h1.QuestionHeader-title::text')
        # item_load.add_css('content', '')

    def start_requests(self):
        return [scrapy.Request("https://www.zhihu.com/#signin", headers=self.headers, callback=self.login)]

    def login(self, response):
        response_text = response.text
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text, re.DOTALL)
        xsrf = ''
        if match_obj:
            xsrf = match_obj.group(1)

        if xsrf:
            post_data = {
                "_xsrf": xsrf,
                "email": "476878873@qq.com",
                "password": "lfh05124139",
                "captcha_type": "cn",
                "captcha": {"img_size": '[200, 44]', "input_points": ''}
            }
            import time
            t = str(int(time.time()*1000))
            captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login&lang=cn".format(t)
            yield scrapy.Request(captcha_url, headers=self.headers, meta={'post_data':post_data}, callback=self.login_after_capthha)

    def login_after_capthha(self, response):
        with open("yzm.jpg", "wb") as f:
            f.write(response.body)
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
        post_data = response.meta.get("post_data", {})
        post_url = "https://www.zhihu.com/login/email"
        post_data["captcha"]["input_points"] = yzm
        return [scrapy.FormRequest(
                url=post_url,
                formdata=post_data,
                headers=self.headers,
                callback=self.check_login
            )]

    def check_login(self, response):
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json['msg'] == "登陆成功":
            for url in self.start_urls:
                 yield scrapy.Request(url, dont_filter=True, headers=self.headers)
        # url = "https://www.zhihu.com/question/35931586"
        # yield scrapy.Request(url, dont_filter=True, headers=self.headers)