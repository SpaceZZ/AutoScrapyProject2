import scrapy
from AutoScrapy.items import TrustPilotItem
import json
import requests

headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
			'Accept-Language': 'en-US,en;q=0.9,pl-PL;q=0.8,pl;q=0.7,nl-NL;q=0.6,nl;q=0.5',
			'content-type': 'application/json',
			}


class TrustPilot(scrapy.Spider):
	"""
	Spider to get the data from the eurocis
	"""
	count = 0
	name = "trustpilotspider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False',
		'FEED_URI': 'resulttrustpilot.csv'
	}
	allowed_domains = ['www.trustpilot.com']
	start_urls = ["https://www.trustpilot.com/categories"]

	def parse(self, response):
		"""
		Method looks for the indexes

		:param response: the fully downloaded webpage
		:return: the iterator over the categories links
		"""
		list_of_indexes = response.xpath('//*/div[@class="subCategoryItem___3ksKz"]/a/@href').extract()
		for index in list_of_indexes:
			index = "https://www.trustpilot.com/" + index
			yield scrapy.Request(index, callback=self.parse_companies)

	def parse_companies(self, response):
		"""
		Method get the list of the companies on the webpage and calls itself with the next page
		:param response:
		:return:
		"""
		list_of_companies = response.xpath('//*/div[@class="businessUnitCardsContainer___Qhix1"]/a/@href').extract()
		list_of_companies = list(set(list_of_companies))
		for company in list_of_companies:
			link = "https://www.trustpilot.com/" + company
			yield scrapy.Request(link, callback=self.parse_data)
		next = response.xpath('//*/a[@aria-label="Next page"]/@href').extract_first()
		if next:
			next = "https://www.trustpilot.com/" + next
			yield scrapy.Request(next, callback=self.parse_companies)

	def parse_data(self, response):
		"""
		Method parses the data for each individual company page
		:param response:
		:return:
		"""
		item = TrustPilotItem()
		item['name'] = response.xpath('//*/span[@class="multi-size-header__big"]/text()').extract_first()
		item['url'] = response.request.url
		script = response.xpath('//*/script[@data-initial-state="business-unit-info""]/text()').extract()
		data = json.loads(script[0])
		identifier = data.get('businessUnitId', '')
		url = "https://www.trustpilot.com/businessunit/" + str(identifier) + "/companyinfobox"
		r = requests.get(url, headers=headers)
		data = json.loads(r.text)
		item['website'] = data.get('businessUnitWebsiteUrl', '')
		item['rating'] = data.get('trustScore', '')
		item['desc'] = data.get('descriptionText', '')
		contact = data.get('contact', '')
		if contact:
			item['email'] = contact.get('email', '')
			item['telephone'] = contact.get('phone', '')
			item['street'] = contact.get('address', '')
			item['zip_code'] = contact.get('zipCode', '')
			item['city'] = contact.get('city', '')
			item['country'] = contact.get('country', '')
		categories =  data.get('categories', '')
		cat = []
		if categories:
			for category in categories:
				cat.append(category.get('id', ''))
		cat = [category for category in cat if category]
		item['categories'] = cat
		yield item


