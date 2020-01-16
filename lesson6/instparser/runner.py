import os
from os.path import join, dirname
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from lesson6.instparser import settings
from lesson6.instparser.spiders.instagram import InstagramSpider

do_env = join(dirname(__file__), '.env')
dotenv.load_dotenv(do_env)

INST_LOGIN = os.getenv('INST_LOGIN')
INST_PSWRD = os.getenv('INST_PSWRD')

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)

    process.crawl(InstagramSpider,['geekbrains','andreykirichenko'],INST_LOGIN,INST_PSWRD)
    process.start()
