from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from lesson5.hhparse import settings
from lesson5.hhparse.spiders.hh import HhSpider

if __name__ == '__main__':
    cr_settings = Settings()
    cr_settings.setmodule(settings)
    process = CrawlerProcess(settings=cr_settings)
    process.crawl(HhSpider)
    process.start()
