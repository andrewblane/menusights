import scrapy

class MenuismSpider(scrapy.Spider):
    name = "menuism"
    allowed_domains = ["menuism.com"]
    start_urls = ["https://www.menuism.com/cities/us/ca/san-francisco/tags/american", ]

    def parse(self, response):
        for sel in response.xpath('//div[2]/div'):
            #title = sel.xpath('a/text()').extract()
            link = sel.xpath('a/@href').extract()
            print link