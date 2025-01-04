import scrapy
from watch_comp.items import WatchCompItem

class Spider1Spider(scrapy.Spider):
    name = "spider_1"
    allowed_domains = ["www.cleor.com"]
    start_urls = ["https://www.cleor.com/montres-homme-C10G1.htm"]

    def parse(self, response):
        watches = response.xpath("//div[contains(@class, 'product-thumb')]")

        for watch in watches:

            item = WatchCompItem()

            item['name'] = watch.xpath(".//div[contains(@class, 'caption')]/div[contains(@class, 'name')]/a/text()").get()
            item['price'] = watch.xpath(".//div[contains(@class, 'caption')]/p[@class='price']/text()").get()

            relative_url = watch.xpath(".//div[contains(@class, 'caption')]/div[contains(@class, 'name')]/a/@href").get()
            item['url'] = response.urljoin(relative_url)

            yield item

            # yield {
            #     'name': watch.xpath(".//div[contains(@class, 'caption')]/div[contains(@class, 'name')]/a/text()").get(),
            #     'price': watch.xpath(".//div[contains(@class, 'caption')]/p[@class='price']/text()").get(),
            #     'url': watch.xpath(".//div[contains(@class, 'caption')]/div[contains(@class, 'name')]/a/@href").get()
            # }

        # Find link to next page
        next_page = response.xpath("//ul/li/a[@rel='next']/@href").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse) 
