# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from lesson5.hhparse.items import HhparseItem
from scrapy.loader import ItemLoader
import re


class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://naryan-mar.hh.ru/region/vacancies']

    def parse(self, response: HtmlResponse):
        next_button = response.xpath('//span[contains(@class, "HH-Pager-Controls-Next")]').extract_first()

        url_positions = response.xpath('//a[contains(@data-qa, "vacancy-serp__vacancy-title")]/@href').extract()

        if next_button:
            next_url = response.xpath('//a[contains(@data-qa, "pager-next")]/@href').extract_first()
            yield response.follow(next_url, callback=self.parse)

        for url in url_positions:
            yield response.follow(url, callback=self.position_parse)

    def position_parse(self, response: HtmlResponse):
        item = ItemLoader(HhparseItem(), response)
        item.add_xpath('title_position', '//h1/span/text()')
        item.add_value('url_position', response.url)
        item.add_xpath('desc_position', '//div[contains(@data-qa, "vacancy-description")]')
        item.add_xpath('salary', '//p[contains(@class, "vacancy-salary")]')
        item.add_xpath('org_name', '//span[contains(@itemprop, "name")]/span/text()')
        item.add_xpath('url_org', '//a[contains(@itemprop, "hiringOrganization")]/@href')
        yield item.load_item()








