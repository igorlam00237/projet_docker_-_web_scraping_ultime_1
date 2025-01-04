import scrapy

from watch_comp.items import WatchCompItem


class Spider3Spider(scrapy.Spider):
    name = "spider_3"
    allowed_domains = ["www.cleor.com"]
    start_urls = ["https://www.cleor.com/montres-C10.htm"]

    def parse(self, response):
        
        watches = response.xpath("//div[contains(@class, 'product-thumb')]")

        for watch in watches:

            item = WatchCompItem()

            item['name'] = watch.xpath(".//div[contains(@class, 'caption')]/div[contains(@class, 'name')]/a/text()").get()
            item['price'] = watch.xpath(".//div[contains(@class, 'caption')]/p[@class='price']/text()").get()


            relative_url = watch.xpath(".//div[contains(@class, 'caption')]/div[contains(@class, 'name')]/a/@href").get()

            if relative_url:

                item['url'] = response.urljoin(relative_url)

                yield response.follow(item['url'], callback=self.parse_item, meta={'item': item})


            # yield item

            # Find link to next page
        next_page = response.xpath("//a[contains(@title, 'Next page')]/@href").get()

        if next_page and not next_page.startswith("javascript:"):
            yield response.follow(next_page, callback=self.parse)

    def parse_item(self, response):
        item = response.meta['item']

        item['ref'] = response.xpath("//ul[contains(@class, 'description')]//li/span/text()").get()

        yield item
