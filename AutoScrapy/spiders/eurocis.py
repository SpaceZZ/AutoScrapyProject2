import scrapy
from AutoScrapy.items import EuroCisItem

class Eurocis(scrapy.Spider):
	"""
	Spider to get the data from the Baza Firm PL
	"""
	count = 0
	name = "eurocisspider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False'
	}
	allowed_domains = ['www.eurocis-tradefair.com']
	start_urls = ["https://www.eurocis-tradefair.com/vis/v1/en/directory/a?oid=49779&lang=2"]

	# categories
	# response.xpath('//*[@id="site-wrapper"]/div/div/div/a/@href').extract()

	# link on the page
	#  response.xpath('//*/a[@class="flush"]/@href').extract()
	def parse(self, response):
		"""

		:param response: the fully downloaded webpage
		:return: the iterator over the categories links
		"""
		list_of_indexes = response.xpath('//*[@id="site-wrapper"]/div/div/div/a/@href').extract()
		#remove all the links with "#top" as they are pointing to the top of the screen
		for index in list_of_indexes:
			index = 'https://www.eurocis-tradefair.com' + index
			yield scrapy.Request(index, callback=self.parse_companies)

	def parse_companies(self, response):
		"""
		Method get the list of the companies on the webpage and calls itself with the next page
		:param response:
		:return:
		"""
		list_of_companies = response.xpath('//*/a[@class="flush"]/@href').extract()
		for company in list_of_companies:
			company = 'https://www.eurocis-tradefair.com' + company
			yield scrapy.Request(company,callback=self.parse_data)

	def parse_data(self, response):
		"""
		Method parses the data for each individual company page
		:param response:
		:return:
		"""
		item = EuroCisItem()
		item['name'] = response.xpath('//*/h1[@itemprop="name"]/text()').extract_first()
		item['url'] = response.request.url
		item['street'] = response.xpath('//*/span[@itemprop="streetAddress"]/text()').extract_first()
		item['zip_code'] = response.xpath('//*/span[@itemprop="postalCode"]/text()').extract_first()
		item['city'] = response.xpath('//*/span[@itemprop="addressLocality"]/text()').extract_first()
		item['country'] = response.xpath('//*/span[@itemprop="addressCountry"]/text()').extract_first()
		item['telephone'] = response.xpath('//*/span[@itemprop="telephone"]/text()').extract_first()
		item['fax'] = response.xpath('//*/span[@itemprop="faxNumber"]/text()').extract_first()
		item['email'] = response.xpath('//*/a[@itemprop="email"]/text()').extract_first()
		item['website'] = response.xpath('//*/a[@itemprop="url"]/@href').extract_first()
		item['location'] = response.xpath('//*/li[@class="vis-tracking-location-hall-plan"]/a/span/text()').extract_first()
		categories = response.xpath('//*/div[@id="vis-categories-list"]/div/div/p/text()').extract()
		lst = [item.strip() for item in categories]
		item['categories'] = list(filter(None, lst))
		item['products'] = response.xpath('//*/div[@class="media__body__txt"]/div/h3/text()').extract()
		desc = response.xpath('//*/div[contains(.,"Company details")]/div/text()').extract()
		if desc:
			lst = [item.strip() for item in desc]
			lst = list(filter(None, lst))
			d = "".join(lst)[0:500]
			item['desc'] = d
		yield item


