# Scrapy settings for itzhaopin project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'fangyuan'

SPIDER_MODULES = ['fangyuan.spiders']
NEWSPIDER_MODULE = 'fangyuan.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = fangyuan (+http://www.yourdomain.com)'

ITEM_PIPELINES = {
    #'fangyuan.pipelines.json_with_encoding.JsonWithEncodingPipeline': 300,
    'fangyuan.pipelines.mongodb.SingleMongodbPipeline': 300,
}

SingleMONGODB_SERVER = "localhost"
SingleMONGODB_PORT = 27017
SingleMONGODB_DB = "house"

LOG_LEVEL = 'INFO'

