import scrapy
from watch_comp.items import WatchCompItem
import json

class Spider1Spider(scrapy.Spider):
    name = "spider_1"
    allowed_domains = ["maty.com"]
    start_urls = ["https://www.maty.com/montres.html"]

    def parse(self, response):
        # Extract watches on the initial page
        watches = response.xpath("//div[contains(@class, 'produit pl-event')]")
        for watch in watches:
            item = WatchCompItem()
            
            item['name'] = watch.xpath(".//h2[contains(@class, 'desc')]//span/a/text()").get()
            item['price'] = watch.xpath(".//p[contains(@class, 'prix-final')]/text()").get()
            
            relative_url = watch.xpath(".//h2[contains(@class, 'desc')]//@href").get()
            
            # Skip if name or price is missing
            if not item['name'] or not item['price']:
                self.logger.warning(f"Missing essential data: {item}")
                continue

            if relative_url:
                item['url'] = response.urljoin(relative_url)
                yield response.follow(item['url'], callback=self.parse_item, meta={'item': item})

            #yield item

        # Find link to next page
        next_page = response.xpath("//div[contains(@class, 'page-buttons next')]//span/@data-href").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    
    def parse_item(self, response):

        item = response.meta['item']

        item['ref'] = response.xpath("//div[@id='generales']/ul/li[3]/p[2]/text()").get()

        yield item

