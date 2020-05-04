import scrapy
from AutoScrapy.items import eloungeItem

class ELounge(scrapy.Spider):
	"""
	Spider to get the data from the eurocis
	"""
	count = 0
	name = "eloungespider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False',
		'FEED_URI': 'resultselounge.csv'
	}
	allowed_domains = ['www.ecommerce-lounge.de']
	start_urls = ["http://www.ecommerce-lounge.de/anbieterverzeichnis/"]

	def parse(self, response):
		"""
		Method looks for the indexes

		:param response: the fully downloaded webpage
		:return: the iterator over the categories links
		"""
		list_of_indexes = response.xpath('//*/li[@list-group-item"]/a/@href').extract()
		#remove all the links with "#top" as they are pointing to the top of the screen
		for index in list_of_indexes:
			yield scrapy.Request(index, callback=self.parse_companies)

	def parse_companies(self, response):
		"""
		Method get the list of the companies on the webpage and calls itself with the next page
		:param response:
		:return:
		"""
		list_of_companies = response.xpath('//*/div[@class="media-body"]')
		for company in list_of_companies:
			link = company.xpath('.//@href').extract_first()
			item = eloungeItem()
			address = company.xpath('.//p/text()').extract_first()
			if address:
				item['zip_code'] = address.split()[0]
				item['city'] = address.split()[1]
			yield scrapy.Request(link, callback=self.parse_data, meta={'item': item})
		next = response.xpath('//*/li[@class="hidden-xs active"]/following-sibling::li[1]/a/@href').extract_first()
		if next:
			yield scrapy.Request(next, callback=self.parse_companies)

	def parse_data(self, response):
		"""
		Method parses the data for each individual company page
		:param response:
		:return:
		"""
		item = response.meta['item']
		item['name'] = response.xpath('//*/span[@itemprop="name"]/text()').extract_first()
		item['url'] = response.request.url
		desc = response.xpath('//*/span[@itemprop="description"]/p/text()').extract_first()
		if desc:
			item['desc'] = desc
		telephone = response.xpath('//*/span[@itemprop="tel"]/text()').extract_first()
		if telephone:
			item['telephone'] = telephone
		fax = response.xpath('//*/span[@itemprop="faxNumber"]/text()').extract_first()
		if fax:
			item['fax'] = fax
		website = response.xpath('//*/a[@itemprop="url"]/@href').extract_first()
		if website:
			item['website'] = website
		categories = response.xpath('//*/a[@rel="tag"]/text()').extract()
		if categories:
			item['categories'] = categories
		yield item


