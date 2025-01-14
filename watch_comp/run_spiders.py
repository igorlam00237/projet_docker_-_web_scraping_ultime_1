from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Importing spiders
from watch_comp.spiders.spider_1 import Spider1Spider
from watch_comp.spiders.spider_4 import Spider4Spider
from watch_comp.spiders.spider_2 import Spider2Spider

from watch_comp.spiders.spider_3 import Spider3Spider

if __name__ == "__main__":
    # Load scrapy settings
    process = CrawlerProcess(settings=get_project_settings())

    # Add the spider to execute
    process.crawl(Spider1Spider)
    process.crawl(Spider4Spider)
    process.crawl(Spider2Spider)

    process.crawl(Spider3Spider)

    # Executing spiders
    process.start()