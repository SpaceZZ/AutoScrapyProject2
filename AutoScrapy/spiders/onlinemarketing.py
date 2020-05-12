import scrapy
from AutoScrapy.items import OnlineMarketingItem
import requests

class OnlineMarketing(scrapy.Spider):
	"""
	Spider to get the data from the online.marketing
	"""
	count = 0
	name = "onlinemarketingspider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False',
		'FEED_URI': 'resultsOnlinemarketing.csv'
	}
	allowed_domains = ['online.marketing']
	start_urls = ["https://online.marketing/tools"]

	def parse(self, response):
		"""
		Method checks for the shops and passes to extract certificate and then calls itself on the next link
		with pagination
		:param response: the fully downloaded webpagage
		:return: the iterator over the categories links
		"""
		list_of_links = response.xpath('//*/ul[@class="categories-item__list"]//*/@href').extract()
		#remove all the links with "#top" as they are pointing to the top of the screen
		for link in list_of_links:
			if "https" not in link:
				yield scrapy.Request(response.urljoin(link), callback=self.parse_data)

	def parse_data(self, response):
		"""
		Method get the the data of the tools
		:param response:
		:return:
		"""

		category = response.request.url.split('/')
		data = list(filter(None, category))
		category = data[-1]

		list_of_tools = response.xpath('//*/article[@class="tools-card tools-card"]')
		for tool in list_of_tools:
			item = OnlineMarketingItem()
			name = tool.xpath('./h1/a/text()').extract_first()
			item['name'] = name
			item['category'] = category
			item['url'] = response.request.url
			desc = tool.xpath('./div[@class="tools-card__content-container  "]/div/p/text()').extract_first()
			if desc:
				item['desc'] = desc
			url = tool.xpath('./h1/a/@href').extract_first()
			url = response.urljoin(url)
			req = requests.get(url)
			item['website'] = req.url
			tags = tool.xpath('./div[@class="tools-card__tags"]//*/text()').extract()
			tags = [tag.strip().replace('\n', '').split() for tag in tags]
			tags = list(filter(None, tags))
			item['tags'] = tags
			yield item





