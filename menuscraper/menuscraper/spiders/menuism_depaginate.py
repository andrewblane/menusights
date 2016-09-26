import scrapy

class MenuismSpider(scrapy.Spider):
    name = "menuism_depaginate"
    allowed_domains = ["menuism.com"]
    start_urls = ["https://www.menuism.com/cities/us/ca/san-francisco/tags/american", ]


    max_id = 10

    def start_requests(self, response):
        base_url = response.xpath('//div[14]/div/div/li[7]/a@href').extract()[:-12]
        for i in range(self.max_id):
            yield Request('base_url{1}'.format(i), callback=self.parse)

    def parse(self, response):
        for sel in response.xpath('//div[2]/div'):
            #title = sel.xpath('a/text()').extract()
            link = sel.xpath('a/@href').extract()
            print link