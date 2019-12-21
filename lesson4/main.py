from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from lesson4.avitoparse import settings
from lesson4.avitoparse.spiders.avito import AvitoSpider

if __name__ == '__main__':
    cr_settings = Settings()
    cr_settings.setmodule(settings)
    process = CrawlerProcess(settings=cr_settings)
    process.crawl(AvitoSpider)
    process.start()