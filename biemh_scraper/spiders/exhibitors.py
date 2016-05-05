import scrapy

class ExhibitorsSpider(scrapy.Spider):
  name="exhibitors"
  allowed_domains=["biemh.bilbaoexhibitioncentre.com"]
  start_urls=['http://biemh.bilbaoexhibitioncentre.com/en/exhibitor-directory/']

  def parseexhibitor(self, response):
    name=response.xpath("//*/div[@class='standard_wrapper']/h2/text()").extract()[0]
    stand=response.xpath("//*/h4/text()").extract()[0].lstrip("Stand: ")
    description="".join(response.xpath(".//*/div[@class='fila'][2]/div/text()").extract())

    data=response.xpath("//div[@class='fila']/ul/li/text()").extract()
    sector=[]
    countries=[]
    categories=[]
    for item in data:
      if item.isupper(): categories.append(item)
      elif any(i in item for i in [",",".",":","-"]): sector.append(item)
      else: countries.append(item)

    contactinfo=response.xpath("//p[@class='fila']/text()").extract()
    addr=[]
    telephone=""
    fax=""
    for item in contactinfo:
      if "Tel" in item: telephone=item[-9:]
      elif "Fax" in item: fax=item[-9:]
      if item.isupper(): addr.append(item)
    address=" ".join(addr)

    try:
      web=response.xpath("//p[@class='fila']/a/@href").extract()[0]
    except IndexError:
      web=""


    yield { "name": name, 
            "contact": {
               "address": address, 
               "telephone": telephone, 
               "web": web,
               "stand": stand
            },
            "description": description,
            "sector": sector,
            "countries": countries,
            "categories": categories
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

