# -*- coding: utf-8 -*-

import re
import json


from scrapy.selector import Selector
try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor as sle
#from scrapy.linkextractors.sgml import SgmlLinkExtractor as sle

from fangyuan.items import *
from fangyuan.misc.log import *

class SinaLejuBeijingSpider(CrawlSpider):
    name = "sina_beijing"
    allowed_domains = ["bj.zufang.sina.com.cn"]
    start_urls = [
        "http://bj.zufang.sina.com.cn/house/v0-n1"
    ]
    rules = [
        Rule(sle(allow=("/house/v0-n\d{,4}")), follow=True, callback='parse_item')
    ]

    def parse_item(self, response):
        items = []
        sel = Selector(response)
        base_url = get_base_url(response)
        divs = sel.xpath('//div[@class="search_item_font_list"]')
        for div in divs:
            item = HouseItem()
            item["source"] = "新浪乐居".decode("utf-8")
            item["city"] = "北京".decode("utf-8")

            item['title'] = div.xpath('.//div[@class="search_font_line1_tit_list"]//text()').extract()[0].strip()

            relative_url = div.xpath('.//div[@class="search_font_line1_tit_list"]//@href').extract()[0]
            item['detail_link'] = urljoin_rfc(base_url, relative_url)

            resblock_name = div.xpath('.//div[@class="search_font_line2_list"]//a//text()').extract()
            if resblock_name == []:
                item["resblock"] = ""
            else:
                item["resblock"] = resblock_name[0].strip()

            item["detail"] = div.xpath('.//div[@class="search_font_line3_l_list"]//text()').extract()[0].strip()
            item["detail"] = item["detail"].replace("\t","")

            item["rent"] = div.xpath('.//div[@class="search_font_line3_r_list_num"]//text()').extract()[0]

            item["owner"] = div.xpath('.//div[@class="search_font_line4_list_l"]//text()').extract()[0].strip()

            item["owner_mobile"] = div.xpath('.//div[@class="search_font_line4_list_m"]//text()').extract()[0]

            items.append(item)

        info('parsed ' + str(response))
        return items


    def _process_request(self, request):
        info('process ' + str(request))
        return request

