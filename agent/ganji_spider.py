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

class ganjiSpider(CrawlSpider):
    name = "ganji"
    allowed_domains = ["bj.ganji.com", "sh.ganji.com"]
    start_urls = [
        "http://bj.ganji.com/fang1/a2o1/",
    ]
    rules = [
        Rule(sle(allow=("fang1/a2o\d{,4}/")), follow=True, callback='parse_item'),
    ]

    def parse_item(self, response):
        sel = Selector(response)
        base_url = get_base_url(response)

        items = []

        for count in range(1, 11):
            item = HouseItem()
            item["source"] = "ganji"
            #item["detail_link"] = response.url
            mobile = sel.xpath(("/html/body[@class='b-list housing-list']/div[@id='wrapper']"
"/div[@class='leftBox']/div[@class='listBox']/ul[@class='list-broker']/"
"li[@class='list-img clearfix'][%d]/div[@class='list-mod2']/div[@class='broker-info']"
"/span[@class='broker-tel']/text()" % (count))).extract()
            if mobile == []:
                break
            item["mobile"] = mobile[0].strip()

            name = sel.xpath(("/html/body[@class='b-list housing-list']/div[@id='wrapper']"
"/div[@class='leftBox']/div[@class='listBox']/ul[@class='list-broker']/"
"li[@class='list-img clearfix'][%d]/div[@class='list-mod2']/div[@class='broker-info']"
"/span[@class='broker-name']/a/text()" % (count))).extract()
            item["name"] = name[0].strip()
            items.append(item)

        info('parsed ' + str(response))
        return items

    def _process_request(self, request):
        info('process ' + str(request))
        return request

