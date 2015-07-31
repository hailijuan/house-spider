# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class HouseItem(Item):
    mongodb_id = Field()
    title = Field()
    detail = Field()
    detail_link = Field()

    city = Field()
    district = Field()
    bizcircle = Field()
    resblock = Field()
    address = Field()

    update_time = Field()

    rent = Field()
    owner = Field()
    owner_mobile = Field()
    source = Field()


