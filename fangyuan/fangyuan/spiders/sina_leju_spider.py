# -*- coding: utf-8 -*-

import re
import json
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

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
from fangyuan.utils import house_filter

MAX_DETAIL_LENGTH = 128

class SinaLejuSpider(CrawlSpider):
    name = "sina_leju"
    allowed_domains = ["sh.zufang.sina.com.cn", "bj.zufang.sina.com.cn"]
    start_urls = [
        "http://sh.zufang.sina.com.cn/house/v0-t1-n1/",
        "http://bj.zufang.sina.com.cn/house/v0-t1-n1/",
        "http://sh.zufang.sina.com.cn/house/v0-t3-n1/",
        "http://sh.zufang.sina.com.cn/house/v0-t12-n1/",
        "http://bj.zufang.sina.com.cn/house/v0-t3-n1/"
    ]
    rules = [
        Rule(sle(allow=("/house/v0-t1-n\d{,1}/")), follow=True, callback='parse_item'),
        Rule(sle(allow=("/house/v0-t3-n\d{,1}/")), follow=True, callback='parse_item'),
        Rule(sle(allow=("/house/v0-t12-n\d{,1}/")), follow=True, callback='parse_item'),
        #Rule(sle(allow=("/house/v0-t1-n\d{,4}")), follow=True, callback='parse_item'),
        #Rule(sle(allow=("/house/v0-t3-n\d{,4}")), follow=True, callback='parse_item'),
        #Rule(sle(allow=("/house/v0-t12-n\d{,4}")), follow=True, callback='parse_item')
    ]

    def parse_details(self, response):
        sel = Selector(response)
        item = HouseItem()

        owner_mobile = sel.xpath(("/html/body/div[@id='sroll_Top']/div[@class='container'][1]"
                                  "/div[@class='house']/div[@class='areas']/div[@class='areas_Left']"
                                  "/div[@class='HouseInfo']/div[@class='HouseInfo_M']/span"
                                  "[@class='Tel_t f12br']/text()")).extract()
        if owner_mobile == []:
            return item

        item["owner_mobile"] = owner_mobile[0].strip()

        item["source"] = "新浪乐居".decode("utf-8")
        item['detail_link'] = response.url
        if item['detail_link'].startswith("http://bj."):
            item["city"] = "北京".decode("utf-8")
        else:
            item["city"] = "上海".decode("utf-8")

        district = sel.xpath("/html/body/div[@class='container']/div[@class='bread']/a[2]/text()").extract()
        if district == []:
            item["district"] = ""
        else:
            item["district"] = district[0]

        bizcircle = sel.xpath("/html/body/div[@class='container']/div[@class='bread']/a[3]/text()").extract()
        if bizcircle == []:
            item["bizcircle"] = ""
        else:
            item["bizcircle"] = bizcircle[0]

        resblock = sel.xpath("/html/body/div[@class='container']/div[@class='bread']/a[4]/text()").extract()
        if resblock == []:
            item["resblock"] = ""
        else:
            item["resblock"] = resblock[0]

        address = sel.xpath(("/html/body/div[@id='sroll_Top']/div[@class='container'][2]"
                             "/div[@class='Wrap_Left']/div[@class='container720'][1]"
                             "/div[@class='map_bottom']/div[@id='map_con']"
                             "/div[@class='map_xxdz']/p[1]/text()")).extract()
        if address == []:
            item["address"] = ""
        else:
            item["address"] = address[0]

        update_time = sel.xpath(("/html/body/div[@class='container']/div[@class='bread']"
                                 "/div[@class='f']/text()")).extract()
        if update_time == []:
            item["update_time"] = ""
        else:
            ss = update_time[0].split("时间：".decode("utf-8"))
            item["update_time"] = ss[1]

        detail = sel.xpath(("/html/body/div[@id='sroll_Top']/div[@class='container'][2]"
                            "/div[@class='Wrap_Left']/div[@class='container720'][1]"
                            "/div[@class='container720']/div[@class='searlab_box']/p/text()")).extract()
        if detail == []:
            item["detail"] = ""
        else:
            item["detail"] = detail[0][:MAX_DETAIL_LENGTH]

        title = sel.xpath(("/html/body/div[@id='sroll_Top']/div[@class='container'][1]"
                            "/div[@class='house']/div[@class='titlebg']/span/text()")).extract()
        if title == []:
            item["title"] = ""
        else:
            item["title"] = title[0]

        rent = sel.xpath(("/html/body/div[@id='sroll_Top']/div[@class='container'][1]"
                          "/div[@class='house']/div[@class='areas']/div[@class='areas_Left']"
                          "/div[@class='HouseInfo']/div[@class='HouseInfo_B HouseInfo_BZ']"
                          "/ul/li[@class='CommunityIntr'][1]/span[@class='hs rd']/text()")).extract()
        if rent == []:
            item["rent"] = ""
        else:
            item["rent"] = rent[0]

        owner = sel.xpath(("/html/body/div[@id='sroll_Top']/div[@class='container'][1]"
                           "/div[@class='house']/div[@class='areas']/div[@class='areas_Left']"
                           "/div[@class='HouseInfo']/div[@class='HouseInfo_M']"
                           "/span[@class='Tel_n']/text()")).extract()
        if owner == []:
             item["owner"] = ""
        else:
            item["owner"] = owner[0].strip()

        return item

    def parse_item(self, response):
        items = []
        sel = Selector(response)
        base_url = get_base_url(response)
        divs = sel.xpath('//div[@class="search_item_font_list"]')
        for div in divs:
            owner_mobile = div.xpath('.//div[@class="search_font_line4_list_m"]//text()').extract()[0]
            resblock_name = div.xpath('.//div[@class="search_font_line2_list"]//a//text()').extract()
            if resblock_name == []:
                resblock_name = ""
            else:
                resblock_name = resblock_name[0]
            if house_filter.recent_crawled_house(owner_mobile, resblock_name):
                info('RECENT CRAWLED HOUSE: %s, %s, %s' %(owner_mobile, resblock_name, response.url))
                continue

            relative_url = div.xpath('.//div[@class="search_font_line1_tit_list"]//@href').extract()[0]
            relative_url = urljoin_rfc(base_url, relative_url)

            yield scrapy.Request(relative_url, callback=self.parse_details)

    def _process_request(self, request):
        info('process ' + str(request))
        return request

