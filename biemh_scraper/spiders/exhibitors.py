import scrapy

class exhibitors(scrapy.Spider):

  name="exhibitors"
  allowed_domains=["biemh.bilbaoexhibitioncentre.com"]
  start_urls=['http://biemh.bilbaoexhibitioncentre.com/en/exhibitor-directory/']

  def parseexhibitor(self, response):

    name=response.xpath("//*/div[@class='standard_wrapper']/h2/text()").extract()[0]
    stand=response.xpath("//*/h4/text()").extract()[0].lstrip("Stand: ")

    # Assumes descriptin will always be in the second fila div. 
    # TO-DO (maybe): Get videos, pic urls, etc from description
    description="".join(response.xpath("//*/div[@class='fila'][2]/div/text()").extract())

    # Since the data is not ordered in the site, this takes all the data
    # and processes it later
    data=response.xpath("//div[@class='fila']/ul/li/text()").extract()
    sector=[]
    countries=[]
    categories=[]
    for item in data:
      if item.isupper(): categories.append(item)
      # Will put 2+ word countries in the sector field and single word
      # sectors into the country field. 
      # TO-DO (maybe): Filtering by list of countries
      elif any(i in item for i in [",",".",":","-"," "]): sector.append(item)
      else: countries.append(item)

    # Assumes everything in p is contact info. May screw things up
    contactinfo=response.xpath("//p[@class='fila']/text()").extract()
    addr=[]
    telephone=0
    fax=0
    for item in contactinfo:
      if "Tel" in item: telephone=int(item[-9:])
      elif "Fax" in item: fax=int(item[-9:])
      if item.isupper(): addr.append(item)
    address=" ".join(addr)
      # TO-DO (maybe): Add an "other info" field and see what happens

    # Exhibitor page may or may not have a website
    try:
      web=response.xpath("//p[@class='fila']/a/@href").extract()[0]
    except IndexError:
      web=""

    yield { "name": name, 
            "contact": {
              "address": address, 
              "telephone": telephone, 
              "fax": fax,
              "web": web,
              "stand": stand
            },
            "description": description,
            "sector": sector,
            "countries": countries,
            "categories": categories
          }

  def parse(self, response):

    # Promoted and unpromoted exhibitors have different classes but share
    # the same html structures, so the two things are joined and processed
    standsa=response.xpath("//*[@class='resaltadoS']/td[@class='titulo']/a/@href").extract()
    standsb=response.xpath("//*[@class='resaltadoN']/td[@class='titulo']/a/@href").extract()
    for stand in standsa+standsb:
      standurl=response.urljoin(stand)
      yield scrapy.Request(standurl,callback=self.parseexhibitor)

    nexturl=response.xpath("//*[@class='resultados']/div[@class='tablenav']/div/a[@class='next page-numbers']/@href").extract()
    if nexturl: nexturl=response.urljoin(nexturl[0])
    yield scrapy.Request(nexturl, callback=self.parse)
