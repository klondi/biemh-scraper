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
    description="".join(response.xpath("//*/div[@class='fila'][2]/div/text()").extract()).strip()

    # Since the data is not ordered in the site, this takes all the data
    # and processes it later
    data=response.xpath("//div[@class='fila']/ul/li/text()").extract()
    sector=[]
    countries=[]
    categories=[]
    misc_information=[]
    country_list=["Russian Federation"]
    for item in data:
      if item.isupper(): categories.append(item)
      elif len(item)==1 or item in country_list: countries.append(item)
      elif any(i in item for i in [",",".",":","-"," "]): sector.append(item)
      else: misc_information.append(item)

    # Assumes everything in p is contact info. May screw things up
    contactinfo=response.xpath("//p[@class='fila']/text()").extract()
    addr=[]
    telephone=""
    fax=""
    misccontact=""
    for item in contactinfo:
      if "Tel" in item: telephone=item.lstrip("Tel.: ")
      elif "Fax" in item: fax=item.lstrip("Fax: ")
      elif item.isupper(): addr.append(item)
      else: misccontact=item
    address=" ".join(addr)

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
              "stand": stand,
              "misc_contactinfo": misccontact
            },
            "description": description,
            "sector": sector,
            "countries": countries,
            "categories": categories,
            "misc_info": misc_information
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
    # Next button URLs are also found in other search tabs. when only 2 tabs have it, it's the last page
    if len(nexturl)==3: 
      nexturl=response.urljoin(nexturl[0])
      # Callback sometimes fail and skips a page
      yield scrapy.Request(nexturl, callback=self.parse)
