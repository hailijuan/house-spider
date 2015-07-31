#!/usr/bin/python
#-*-coding:utf-8-*-

import datetime
import traceback

from pprint import pprint
from scrapy import log
from scrapy.exceptions import DropItem, NotConfigured
from pymongo import MongoClient

from fangyuan.utils import color
from fangyuan.utils import house_filter


class NofilesDrop(DropItem):
    """Product with no files exception"""
    def __init__(self, original_url="", *args):
        self.original_url = original_url
        self.style = color.color_style()
        DropItem.__init__(self, *args)

    def __str__(self):#####for usage: print e
        print self.style.ERROR("DROP(NofilesDrop):" + self.original_url)
        return DropItem.__str__(self)

class SingleMongodbPipeline(object):
    """
        save the data to mongodb.
    """

    MONGODB_SERVER = "localhost"
    MONGODB_PORT = 27017
    MONGODB_DB = "house"

    def __init__(self):
        """
            The only async framework that PyMongo fully supports is Gevent.
            
            Currently there is no great way to use PyMongo in conjunction with Tornado or Twisted. PyMongo provides built-in connection pooling, so some of the benefits of those frameworks can be achieved just by writing multi-threaded code that shares a MongoClient.
        """
        
        self.style = color.color_style()
        try:
            client = MongoClient(self.MONGODB_SERVER,self.MONGODB_PORT) 
            self.db = client[self.MONGODB_DB]
        except Exception as e:
            print self.style.ERROR("ERROR(SingleMongodbPipeline): %s"%(str(e),))
            traceback.print_exc()

    @classmethod
    def from_crawler(cls, crawler):
        cls.MONGODB_SERVER = crawler.settings.get('SingleMONGODB_SERVER', 'localhost')
        cls.MONGODB_PORT = crawler.settings.getint('SingleMONGODB_PORT', 27017)
        cls.MONGODB_DB = crawler.settings.get('SingleMONGODB_DB', 'house')
        pipe = cls()
        pipe.crawler = crawler
        return pipe

    def process_item(self, item, spider):
        owner_mobile = item.get('owner_mobile', '')
        resblock = item.get('resblock', '')
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        owner_mobile = owner_mobile .replace(' ', '')

        for doc in self.db['house_detail'].find({"owner_mobile": owner_mobile, "resblock": resblock}):
            if house_filter.within_anti_spam_period(doc["create_time"], current_time):
                raise NofilesDrop(item.get('detail_link', ''))

        house_detail = {
            'title':item.get('title', ''),
            'detail':item.get('detail', ''),
            'detail_link':item.get('detail_link', ''),
            'resblock': resblock,
            'district':item.get('district', ''),
            'bizcircle':item.get('bizcircle', ''),
            'address':item.get('address', ''),
            'city':item.get('city', ''),
            'owner': item.get('owner', ''),
            'owner_mobile': owner_mobile,
            'rent':item.get('rent', ''),
            'source':item.get('source', ''),
            'house_update_time':item.get('update_time', ''),
            'create_time':current_time,
        }
        
        result = self.db['house_detail'].insert(house_detail)
        item["mongodb_id"] = str(result)

        log.msg("Item %s wrote to MongoDB database %s/house_detail" %
                    (result, self.MONGODB_DB),
                    level=log.DEBUG, spider=spider)
        return item

class ShardMongodbPipeline(object):
    """
        save the data to shard mongodb.
    """

    MONGODB_SERVER = "localhost"
    MONGODB_PORT = 27017
    MONGODB_DB = "books_mongo"
    GridFs_Collection = "book_file"

    def __init__(self):
        """
            The only async framework that PyMongo fully supports is Gevent.
            
            Currently there is no great way to use PyMongo in conjunction with Tornado or Twisted. PyMongo provides built-in connection pooling, so some of the benefits of those frameworks can be achieved just by writing multi-threaded code that shares a MongoClient.
        """
        
        self.style = color.color_style()
        try:
            client = MongoClient(self.MONGODB_SERVER,self.MONGODB_PORT) 
            self.db = client[self.MONGODB_DB]
        except Exception as e:
            print self.style.ERROR("ERROR(ShardMongodbPipeline): %s"%(str(e),))
            traceback.print_exc()

    @classmethod
    def from_crawler(cls, crawler):
        cls.MONGODB_SERVER = crawler.settings.get('ShardMONGODB_SERVER', 'localhost')
        cls.MONGODB_PORT = crawler.settings.getint('ShardMONGODB_PORT', 27017)
        cls.MONGODB_DB = crawler.settings.get('ShardMONGODB_DB', 'books_mongo')
        cls.GridFs_Collection = crawler.settings.get('GridFs_Collection', 'book_file')
        pipe = cls()
        pipe.crawler = crawler
        return pipe

    def process_item(self, item, spider):
        book_detail = {
            'book_name':item.get('book_name'),
            'alias_name':item.get('alias_name',[]),
            'author':item.get('author',[]),
            'book_description':item.get('book_description',''),
            'book_covor_image_path':item.get('book_covor_image_path',''),
            'book_covor_image_url':item.get('book_covor_image_url',''),
            'book_download':item.get('book_download',[]),
            'book_file_url':item.get('book_file_url',''),
            'book_file_id':item.get('book_file_id',''),
            'original_url':item.get('original_url',''),
            'update_time':datetime.datetime.utcnow(),
        }
        
        result = self.db['book_detail'].insert(book_detail)
        item["mongodb_id"] = str(result)

        log.msg("Item %s wrote to MongoDB database %s/book_detail" %
                    (result, self.MONGODB_DB),
                    level=log.DEBUG, spider=spider)
        return item
