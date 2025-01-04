import scrapy
from watch_comp.items import WatchCompItem


class Spider2Spider(scrapy.Spider):
    name = "spider_2"
    allowed_domains = ["www.bijouteriehaubois.fr"]
    start_urls = ["https://www.bijouteriehaubois.fr/fr/montres"]

    def parse(self, response):

        watches = response.xpath("//a[contains(@class, 'prod-item__container')]")

        for watch in watches:

            item = WatchCompItem()

            item['name'] = watch.xpath(".//div[@class='prod-item__content']//span[@class='prod-item__name']/text()").get()
            item['price'] = watch.xpath(".//div[@class='prod-item__content']/p[@class='prod-item__prix']/text()").get()

            relative_url = watch.xpath("./@href").get()

            if relative_url:

                item['url'] = response.urljoin(relative_url)
                yield response.follow(item['url'], callback=self.parse_item, meta={'item': item})

            # yield item

        # Find link to next page
        next_page = response.xpath("//a[contains(@aria-label, 'Suivante')]/@href").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_item(self, response):

        item = response.meta['item']

        item['ref'] = response.xpath("//li[contains(@data-label, 'Référence')]/p[2]/text()").get()

        yield item
