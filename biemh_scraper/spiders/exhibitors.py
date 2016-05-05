import scrapy

class ExhibitorsSpider(scrapy.Spider):
  name="exhibitors"
  allowed_domains=["biemh.bilbaoexhibitioncentre.com"]
  start_urls=['http://biemh.bilbaoexhibitioncentre.com/en/exhibitor-directory/']

  def parseexhibitor(self, response):
    name=response.xpath("//*/div[@class='standard_wrapper']/h2/text()").extract()[0]
    addr, addr2, tel, _ = response.xpath("//*[@class='medio']/p/text()").extract()
    address=addr+addr2
    telephone=tel.lstrip(" Tel.: ")
    web=response.xpath("//*[@class='medio']/p/a/text()").extract()[0]
    stand=response.xpath("//*/h4/text()").extract()[0]
    description="\n".join(response.xpath(".//*/div[@class='fila'][2]/div/text()").extract())
    sector=response.xpath("//*/div[@class='fila'][3]/ul/li/text()").extract()
    countries=response.xpath("//*/div[@class='fila'][4]/ul/li/text()").extract()
    categories=response.xpath("//*/div[@class='fila'][5]/ul/li/text()").extract()

    yield { "name": name, 
            "contact":{
              "address": address, 
              "telephone": telephone, 
              "stand": stand
            }
            "description": description
            "sector": sector
            "countries": []
            "categories": []
          }

  def parse(self, response):
    standsa=response.xpath("//*[@class='resaltadoS']/td[@class='titulo']/a/@href").extract()
    standsb=response.xpath("//*[@class='resaltadoN']/td[@class='titulo']/a/@href").extract()
    for stand in standsa+standsb:
      standurl=response.urljoin(stand)
      yield scrapy.Request(standurl,callback=self.parseexhibitor)

    nexturl=response.xpath("//*[@class='resultados']/div[@class='tablenav']/div/a[@class='next page-numbers']/@href").extract()
    if nexturl: nexturl=response.urljoin(nexturl[0])
    yield scrapy.Request(nexturl, callback=self.parse)

