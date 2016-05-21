import scrapy

class exhibitors(scrapy.Spider):

  name="exhibitors"
  allowed_domains=["biemh.bilbaoexhibitioncentre.com"]
  start_urls=['http://biemh.bilbaoexhibitioncentre.com/en/exhibitor-directory/?pagenum=11&num_elem=100&nombre&pais&pabellon&sector&subsector&producto&destino=expositores&idioma=US&tab=expositores&seccli&contextual&buscar=2&letra']

  def parseexhibitor(self, response):

    name=response.xpath("//*/div[@class='standard_wrapper']/h2/text()").extract()[0]
    stand=response.xpath("//*/h4/text()").extract()[0].lstrip("Stand: ")

    # Assumes description will always be in the second fila div. 
    # TO-DO (maybe): Get videos, pic urls, etc from description
    description="".join(response.xpath("//*/div[@class='fila'][2]/div/text()").extract()).strip()

    # Since the data is not ordered in the site, this takes all the data
    # and processes it later
    data=response.xpath("//div[@class='fila']/ul/li/text()").extract()
    sector=[]
    countries=[]
    categories=[]
    country_list=["Russian Federation", "United States", "United Kingdom"]
    for item in data:
      if item.isupper(): categories.append(item)
      elif item in country_list: countries.append(item)
      elif any(i in item for i in [",",".",":","-"," ","/"]): sector.append(item)
      else: countries.append(item)

    # Assumes everything in p is contact info. May screw things up
    contactinfo=response.xpath("//p[@class='fila']/text()").extract()
    addr=[]
    telephone=""
    fax=""
    for item in contactinfo:
      if "Tel" in item: telephone=item.strip().lstrip("Tel.: ")
      elif "Fax" in item: fax=item.strip().lstrip("Fax: ")
      elif item.isupper(): addr.append(item)
    address=" ".join(addr)

    # Exhibitor page may or may not have a website
    try:                web=response.xpath("//p[@class='fila']/a/@href").extract()[0]
    except IndexError:  web=""

    yield { "name": name, 
            "contact": {
              "address": address, 
              "telephone": telephone, 
              "fax": fax,
              "web": web,
              "stand": stand,
            },
            "description": description,
            "sector": sector,
            "countries": countries,
            "categories": categories,
          }

  def parse(self, response):

    # Promoted and unpromoted exhibitors have different classes but share
    # the same html structures, so the two things are joined and processed
    standsa=response.xpath("//*[@class='resaltadoS']/td[@class='titulo']/a/@href").extract()
    standsb=response.xpath("//*[@class='resaltadoN']/td[@class='titulo']/a/@href").extract()
    for stand in standsa+standsb:
      standurl=response.urljoin(stand)
      try:
        yield scrapy.Request(standurl,callback=self.parseexhibitor)
      except Exception as e: 
        print "Error parsing"
        print e
        exit()

    # nexturl=response.xpath("//*[@class='resultados']/div[@class='tablenav']/div/a[@class='next page-numbers']/@href").extract()
    # Next button URLs are also found in other search tabs. when only 2 tabs have it, it's the last page
    if len(nexturl)==3: 
      npurl=response.urljoin(nexturl[0])
      try:
        yield scrapy.Request(npurl, callback=self.parse)
      except Exception as e:
        print "Error parsing"
        print e
        exit()