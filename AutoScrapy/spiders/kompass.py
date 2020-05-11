import scrapy
import json
from AutoScrapy.items import kompassItem

class kompass(scrapy.Spider):
	"""
	Spider to get the data from the Baza Firm PL
	"""
	count = 0
	name = "kompassspider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False',
		'FEED_URI' : 'resultskompass.csv'
	}
	allowed_domains = ['de.kompass.com']
	start_urls = ["https://de.kompass.com/a/online-einzelhandler-e-commerce/81650/"]


	def parse(self, response):
		"""
		:param response: the fully downloaded webpage
		:return: the iterator over the categories links
		"""
		list_of_companies = response.xpath('//*/div[@class="product-list-data"]/h2/a/@href').extract()
		#remove all the links with "#top" as they are pointing to the top of the screen
		for company in list_of_companies:
			if "https" in company:
				yield scrapy.Request(company, callback=self.parse_data)
		for i in range(2,21):
			page = "https://de.kompass.com/a/online-einzelhandler-e-commerce/81650/page-" + str(i)
			yield scrapy.Request(page, callback=self.parse)


	def parse_data(self, response):
		"""
		Method parses the data for each individual company page
		:param response:
		:return:l-companysingle__description l-section
		"""
		item = kompassItem()

		item['name'] = response.xpath('//*/div[@class="companyCol1 blockNameCompany"]/h1/text()').extract_first().strip()
		item['url'] = response.request.url

		#desc
		desc = response.xpath('//*/div[@itemprop="description"]/text()').extract_first()
		if desc:
			item['desc'] = desc.strip()

		street = response.xpath('//*/span[@itemprop="streetAddress"]/text()').extract_first()
		if street:
			item['street'] = street.strip()

		address = response.xpath('//*/p[@class="blockAddress"]/span[2]/text()').extract()[1]
		if address:
			address = address.strip()
			item['zip_code'] = address.split()[0]
			item['city'] = address.split()[1]
		country = response.xpath('//*/span[@itemprop="addressCountry"]/text()').extract_first()
		if country:
			item['country'] = country.strip()
		telephone = response.xpath('//*/input[contains(@id, "freePhoneLabel")]/@value').extract_first()
		if telephone:
			item['telephone'] = telephone
		item['website'] = response.xpath('//*/div[@class="listWww"]//*/@href').extract()
		categories = response.xpath('//*/div[@class="activitiesTree"]/ul/li/a/text()').extract()
		if categories:
			item['categories'] = categories
		yield item


