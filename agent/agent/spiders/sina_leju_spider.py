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

class sinaSpider(CrawlSpider):
    name = "sina"
    allowed_domains = ["bj.zufang.sina.com.cn", "sh.zufang.sina.com.cn"]
    start_urls = [
        "http://bj.zufang.sina.com.cn/house/v1-n1/",
        "http://sh.zufang.sina.com.cn/house/v1-n1/",
    ]
    rules = [
        Rule(sle(allow=("house/v1-n\d{,1}/")), follow=True, callback='parse_item'),
        #Rule(sle(allow=("house/v1-n\d{,4}/")), follow=True, callback='parse_item'),
    ]

    def parse_item(self, response):
        sel = Selector(response)
        base_url = get_base_url(response)
        if base_url.__contains__("sh.zufang.sina.com"):
            city_code = "shanghai"
        else:
            city_code = "beijing"

        items = []

        divs = sel.xpath('//div[@class="search_item_font_list"]')
        for div in divs:
            item = HouseItem()
            item["source"] = "sina"
            item["city"] = city_code
            item["name"] = div.xpath('.//div[@class="search_font_line4_list_l"]//text()').extract()[0].strip()
            item["mobile"] = div.xpath('.//div[@class="search_font_line4_list_m"]//text()').extract()[0]
            items.append(item)

        info('parsed ' + str(response))
        return items

    def _process_request(self, request):
        info('process ' + str(request))
        return request

