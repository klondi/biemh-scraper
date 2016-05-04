import scrapy


class ExhibitorsSpider(scrapy.Spider):
  name = "exhibitors"
  allowed_domains = ["biemh.bilbaoexhibitioncentre.com"]
  start_urls = ['http://www.http://biemh.bilbaoexhibitioncentre.com/en/exhibitor-directory/']

  def parseexhibitor(self, response):
    pass

  def parse(self, response):
    pass
