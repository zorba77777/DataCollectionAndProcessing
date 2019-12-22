# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from scrapy.loader.processors import MapCompose, TakeFirst
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def cleanhtml(raw_html):
    from bs4 import BeautifulSoup
    cleantext = BeautifulSoup(raw_html, "lxml").text
    return cleantext


class HhparseItem(scrapy.Item):
    _id = scrapy.Field()
    title_position = scrapy.Field(output_processor=TakeFirst())
    url_position = scrapy.Field(output_processor=TakeFirst())
    desc_position = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(strip_tags))
    salary = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(strip_tags))
    org_name = scrapy.Field(output_processor=TakeFirst())
    url_org = scrapy.Field(output_processor=TakeFirst())
