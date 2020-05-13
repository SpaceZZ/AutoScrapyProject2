import scrapy
from AutoScrapy.items import ShopTalkItem
import requests

class OnlineMarketing(scrapy.Spider):
	"""
	Spider to get the data from the online.marketing
	"""
	count = 0
	name = "shoptalkspider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False',
		'FEED_URI': 'resultsShopTalk.csv'
	}
	allowed_domains = ['shoptalk.com']
	start_urls = ["https://shoptalk.com/sponsors"]

	def parse(self, response):
		"""
		Method checks for the shops and passes to extract certificate and then calls itself on the next link
		with pagination
		:param response: the fully downloaded webpagage
		:return: the iterator over the categories links
		"""
		list_of_links = response.xpath('//*/div[@class="info"]/following-sibling::a/@href').extract()
		#remove all the links with "#top" as they are pointing to the top of the screen
		for link in list_of_links:
			yield scrapy.Request(link, callback=self.parse_data)

	def parse_data(self, response):
		"""
		Method get the the data of the shop
		:param response:
		:return:
		"""

		item = ShopTalkItem()
		item['name'] = response.xpath('//*/h3[@class="subsection-title title"]/text()').extract_first().strip()
		item['category'] = response.xpath('//*/h4[@class="level"]/text()').extract()[1].strip()
		item['url'] = response.request.url
		desc = response.xpath('//*/h4[@class="level"]/following-sibling::p/text()').extract_first().strip()
		if desc:
			item['desc'] = desc
		else:
			d = response.xpath('//*/h4[@class="level"]/following-sibling::p/span/text()').extract_first().strip()
			if d:
				item['desc'] = d
		item['website'] = response.xpath('//*/div[@class="link"]/a/@href').extract_first()
		yield item





