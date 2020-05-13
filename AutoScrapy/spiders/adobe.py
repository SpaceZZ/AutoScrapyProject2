import scrapy
from AutoScrapy.items import AdobeItem
import requests

class Adobe(scrapy.Spider):
	"""
	Spider to get the data from the online.marketing
	"""
	count = 0
	name = "adobespider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False',
		'FEED_URI': 'resultsAdobe.csv'
	}
	start_urls = ["https://www.adobe.com/summit/sponsors.html"]

	def parse(self, response):
		"""
		Method checks for the shops and passes to extract certificate and then calls itself on the next link
		with pagination
		:param response: the fully downloaded webpagage
		:return: the iterator over the categories links
		"""
		list_of_links = response.xpath('//*/div[@class="image parbase"]/div/a/@href').extract()
		#remove all the links with "#top" as they are pointing to the top of the screen
		for link in list_of_links:
			yield scrapy.Request(link, callback=self.parse_data)

	def parse_data(self, response):
		"""
		Method get the the data of the shop
		:param response:
		:return:
		"""
		item = AdobeItem()

		#get name of the webpage
		name = response.xpath('//*/title/text()').extract_first()
		if name:
			n = name.split()[0]
			if n.strip(':') in response.request.url:
				item['name'] = n.strip(':')
			else:
				url = response.request.url.split('/')[2]
				if len(url.split('.')) > 2:
					name = url.split('.')[1]
					item['name'] = name
				else:
					name = url.split('.')[0]
					item['name'] = name
		else:
			url = response.request.url.split('/')[2]
			if len(url.split('.')) > 2:
				name = url.split('.')[1]
				item['name'] = name
			else:
				name = url.split('.')[0]
				item['name'] = name

		item['website'] = response.request.url

		desc = response.xpath('//*/meta[@itemprop="description"]/@content').extract_first()
		desc1 = response.xpath('//*/meta[@name="description"]/@content').extract_first()
		if desc1:
			item['desc'] = desc1
		else:
			if desc:
				item['desc'] = desc
			else:
				desc = response.xpath('//*/meta[@property="description"]/@content').extract_first()
				if desc:
					item['desc'] = desc
				else:
					if name:
						item['desc'] = name

		tags = response.xpath('//*/meta[@property="keywords"]/@content').extract_first()
		tags1 = response.xpath('//*/meta[@name="keywords"]/@content').extract_first()
		if tags:
			item['tags'] = tags
		elif tags1:
			item['tags'] = tags1
		else:
			tags = response.xpath('//*/meta[@itemprop="keywords"]/@content').extract_first()
			if tags:
				item['tags'] = tags

		yield item





