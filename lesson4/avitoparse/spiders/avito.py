# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from lesson4.avitoparse.items import AvitoparseItem


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/nevinnomyssk/kvartiry/prodam']
    base_url_request = '/nevinnomyssk/kvartiry/prodam'
    page_number = 1

    def parse(self, response: HtmlResponse):
        has_next_page = True
        pagination_span_text = response.xpath(
            '//span[contains(@data-marker, "pagination-button/next")]'
        ).extract_first()
        if pagination_span_text:
            has_next_page = False if 'readonly' in pagination_span_text else True

        adverts_urls = response.xpath('//a[contains(@class, "snippet-link")]/@href').extract()

        if has_next_page:
            AvitoSpider.page_number = AvitoSpider.page_number + 1
            next_url = self.base_url_request + '?p=' + str(AvitoSpider.page_number)
            yield response.follow(next_url, callback=self.parse)

        for url in adverts_urls:
            yield response.follow(url, callback=self.advert_parse)

    def advert_parse(self, response: HtmlResponse):
        title = response.xpath('//span[contains(@class, "title-info-title-text")]/text()').extract_first()

        price = response.xpath('//span[contains(@class, "js-item-price")]/text()').extract_first()

        attrs = response.xpath('//li[contains(@class, "item-params-list-item")]').extract()
        clean_attrs = []
        for attr in attrs:
            clean_attrs.append(self.remove_html_tags(attr))

        yield AvitoparseItem(
            title=title,
            price=price,
            attrs=clean_attrs
        )

    def remove_html_tags(self, text):
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
