# -*- coding: utf-8 -*-

import re
import json
import scrapy

from scrapy.selector import Selector
try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor as sle

from agent.items import *
from agent.misc.log import *

class sinaAgentSpider(CrawlSpider):
    name = "sina_agent"
    allowed_domains = ["bj.esf.sina.com.cn", "sh.esf.sina.com.cn"]
    start_urls = [
        "http://bj.esf.sina.com.cn/agent/j2-m3-n1/",
        "http://sh.esf.sina.com.cn/agent/j2-m3-n1/",
    ]
    rules = [
        Rule(sle(allow=("agent/j2-m3-n\d{,4}/")), follow=True, callback='parse_item'),
        #Rule(sle(allow=("house/v1-n\d{,4}/")), follow=True, callback='parse_item'),
    ]

    def parse_item(self, response):
        sel = Selector(response)
        base_url = get_base_url(response)
        if base_url.__contains__("sh.esf.sina.com"):
            city_code = "shanghai"
        else:
            city_code = "beijing"

        items = []

        divs = sel.xpath('//div[@class="hall_people_list"]')
        for div in divs:
            item = HouseItem()
            item["source"] = "sina"
            item["city"] = city_code
            for sub_div in div.xpath('.//div[@class="hall_people_house_font"]'):
                text = sub_div.xpath('.//text()')
                if len(text) <= 1:
                    continue
                key, value = text[0], text[1]
                if key.extract().startswith(u'手机'):
                    item["mobile"] = value.extract()
                    item["name"] = div.xpath('.//div[@class="hall_people_house_name_l"]/a/text()').extract()[0]
                    break

            items.append(item)

        info('parsed ' + str(response))
        return items

    def _process_request(self, request):
        info('process ' + str(request))
        return request

