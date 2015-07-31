# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class HouseItem(Item):
    #mongodb_id = Field()
    name = Field()
    mobile = Field()
    company = Field()
    city = Field()
    source = Field()
    update_time = Field()


