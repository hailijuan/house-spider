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

from fangyuan.items import *
from fangyuan.misc.log import *

class d1fySpider(CrawlSpider):
    name = "d1fy"
    allowed_domains = ["bj.01fy.cn", "sh.01fy.cn"]
    start_urls = [
        "http://bj.01fy.cn/rent/list_2_0_0_0-0_0_0-0_0_2_0_1_.html",
        "http://sh.01fy.cn/rent/list_2_0_0_0-0_0_0-0_0_2_0_1_.html"
    ]
    rules = [
        Rule(sle(allow=("list_2_0_0_0-0_0_0-0_0_2_0_\d{,1}_.html")), follow=True, callback='parse_item'),
        #Rule(sle(allow=("list_2_0_0_0-0_0_0-0_0_2_0_\d{,4}_.html")), follow=True, callback='parse_item'),
        Rule(sle(allow=("house_\d.html",)), follow=True, callback='parse_item')
    ]

    def parse_details(self, response):
        sel = Selector(response)

        for div in sel.xpath('//div[@id="content"]'):
            item = HouseItem()
            item["source"] = "第一时间房源网".decode("utf-8")
            item["detail_link"] = response.url

            item['title'] = div.xpath('.//h1//text()').extract()[0]

            update_time = div.xpath('.//div[@class="l_fy"]//p//text()').extract()[0]
            ss = update_time.split("时间：".decode("utf-8"))
            item["update_time"] = ss[1]

            resblock_name = div.xpath('.//dd')[2].xpath('.//text()').extract()
            if resblock_name == []:
                item["resblock"] = ""
            else:
                item["resblock"] = resblock_name[0]

            address = div.xpath('.//dd')[3].xpath('.//text()').extract()[0]
            ss = address.split(" - ")
            item["city"] = ss[0]
            item["district"] = ss[1]
            item["bizcircle"] = ss[2]
            item["address"] = ss[3]

            detail = div.xpath('.//dd')[5].xpath('.//text()').extract()
            if detail == []:
                item["detail"] = ""
            else:
                item["detail"] = detail[0]

            item["rent"] = div.xpath('.//dd')[0].xpath('.//text()').extract()[0]
            item["owner"] = div.xpath('.//dd')[6].xpath('.//text()').extract()[0]

            src_path = div.xpath('.//dd')[7].xpath('.//@src').extract()
            if src_path == []:
                item["owner_mobile"] = div.xpath('.//dd')[7].xpath('.//div[@class="telephone redtelphone"]//text()').extract()[0].strip()
            else:
                #TODO: number recognition
                item["owner_mobile"] = src_path[0]

            info('parsed ' + str(response))
            return item

        return HouseItem()

    def parse_item(self, response):
        sel = Selector(response)
        base_url = get_base_url(response)

        divs = sel.xpath('//div[@id="list"]').xpath('.//div[@class="div01"]')
        for div in divs:
            relative_url = div.xpath('.//a//@href').extract()[0]
            relative_url = urljoin_rfc(base_url, relative_url)
            yield scrapy.Request(relative_url, callback=self.parse_details)

    def _process_request(self, request):
        info('process ' + str(request))
        return request

