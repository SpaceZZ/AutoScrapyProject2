import scrapy
from AutoScrapy.items import RetailXItem
import requests


class RetailX(scrapy.Spider):
	"""
	Spider to get the data from the online.marketing
	"""
	count = 0
	name = "retailxspider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False',
		'FEED_URI': 'resultsRetailx.csv'
	}
	allowed_domains = ['retailx.a2zinc.net']
	start_urls = ["https://retailx.a2zinc.net/RetailX2020/Public/Exhibitors.aspx?ID=23735"]

	def parse(self, response):
		"""
		Method checks for the shops
		:param response: the fully downloaded webpagage
		:return:
		"""
		list_of_links = response.xpath('//*/a[@class="exhibitorName"]/@href').extract()
		for link in list_of_links:
			yield scrapy.Request(response.urljoin(link), callback=self.parse_data)

	def parse_data(self, response):
		"""
		Method get the the data of the tools
		:param response:
		:return:
		"""
		url = "https://retailx.a2zinc.net/RetailX2020/Public/Exhibitors.aspx?ID=23735"
		item = RetailXItem()
		item['url'] = url
		name = response.xpath('//*/div[@class="panel-body"]/h1/text()').extract_first()
		if name:
			item['name'] = name.strip('\t').replace('\r', '').replace('\xa0', '').strip(',').strip()
		city = response.xpath('//*/span[@class="BoothContactCity"]/text()').extract_first()
		if city:
			item['city'] = city.strip('\t').replace('\r', '').replace('\xa0', '').strip(',').strip().replace(',', '')
		state = response.xpath('//*/span[@class="BoothContactState"]/text()').extract_first()
		if state:
			item['state'] = state.strip('\t').replace('\r', '').replace('\xa0', '').strip(',').strip()
		country = response.xpath('//*/span[@class="BoothContactCountry"]/text()').extract_first()
		if country:
			item['country'] = country.strip('\t').replace('\r', '').replace('\xa0', '').strip(',').strip()
		website = response.xpath('//*/span[@class="BoothContactUrl"]/a/text()').extract_first()
		if website:
			item['website'] = website
		booth = response.xpath('//*/ul[@class="list-inline eBoothControls"]/li[0]/text()').extract_first()
		if booth:
			item['booth'] = booth.replace('Booth:', '').strip()
		yield item
