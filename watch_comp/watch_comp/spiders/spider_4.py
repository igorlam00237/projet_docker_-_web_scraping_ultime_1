import scrapy

from watch_comp.items import WatchCompItem


class Spider4Spider(scrapy.Spider):
    name = "spider_4"
    allowed_domains = ["ocarat.com"]
    start_urls = ["https://ocarat.com/montre/"]

    def parse(self, response):
        
        watches = response.xpath("//div[contains(@class, 'product-container')]")

        for watch in watches:

            item = WatchCompItem()

            item['name'] = watch.xpath(".//div[contains(@class, 'product-main-container')]//div[2]/text()").get()
            item['price'] = watch.xpath(".//div[contains(@class, 'product-main-container')]/div[contains(@class, 'content_price')]/span/text()").get()
            


            relative_url = watch.xpath(".//div[contains(@class, 'product-main-container')]//a/@href").get()

            if relative_url:

                item['url'] = response.urljoin(relative_url)

                yield response.follow(item['url'], callback=self.parse_item, meta={'item': item})


            # yield item

            # Find link to next page
        next_page = response.xpath("//link[@rel='next']/@content").get()
        #next_page = response.xpath("//ul[@class='pagination']//li[@id='pagination_next_bottom']/a/@href").get()
        #next_page = response.urljoin(next_page)

        if next_page:
            #self.logger.info(f"Next page found: {next_page}")

            yield response.follow(next_page, callback=self.parse)
        #else:
            #self.logger.info("No next page found.")
    def parse_item(self, response):
        item = response.meta['item']

        item['ref'] = response.xpath("//table[contains(@class, 'table table-data-sheet')]//tr[2]/td[@class='feature_values']/text()").get()

        yield item
