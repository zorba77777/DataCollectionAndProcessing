# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AvitoparseItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    attrs = scrapy.Field()
