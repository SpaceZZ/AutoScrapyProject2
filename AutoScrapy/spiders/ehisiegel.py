import scrapy
from AutoScrapy.items import EhiSiegelItem

class Ehisigiel(scrapy.Spider):
	"""
	Spider to get the data from the ehi-sigiel
	"""
	count = 0
	name = "ehisiegelspider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False'
		#'JOBDIR': f'/tmp/requests',
	}
	allowed_domains = ['ehi-siegel.de',
					   'zertifikat.ehi-siegel.de']
	start_urls = ["https://ehi-siegel.de/verbraucher/shops-mit-siegel/shops-zertifiziert/es/Shop/"]

	def parse(self, response):
		"""
		Method checks for the shops and passes to extract certificate and then calls itself on the next link
		with pagination
		:param response: the fully downloaded webpagage
		:return: the iterator over the categories links
		"""
		list_of_shops = response.xpath('//*/div[@class="media-body"]')
		#remove all the links with "#top" as they are pointing to the top of the screen
		for shop in list_of_shops:
			item = EhiSiegelItem()
			item['name'] = shop.xpath('.//div[@class="shop-head"]/h4[1]/text()').get().strip('\n').strip()
			item['categories'] = [category.strip('\n').strip() for category in shop.xpath('.//div[@class="shop-head"]/a/text()').getall()]
			item['desc'] = shop.xpath('.//div[@class="shop-description"]/text()').get().strip('\n').strip()
			item['website'] = shop.xpath('.//div[@class="shop-links"]/a[1]/@href').get()
			url = shop.xpath('.//div[@class="shop-links"]/a[2]/@href').get()
			item['url'] = url
			yield scrapy.Request(url, callback=self.parse_certificate, meta={'item': item})
		next_page = response.xpath('//*/a[@class="next"]/@href').get()
		if next_page:
			next_page = "https://ehi-siegel.de" + next_page
			yield scrapy.Request(next_page, callback=self.parse)

	def parse_certificate(self, response):
		"""
		Method get the url of the certificate of the shop
		:param response:
		:return:
		"""
		item = response.meta['item']
		item['street'] = response.xpath('//*/span[@itemprop="streetAddress"]/text()').get()
		item['zip_code'] = response.xpath('//*/span[@itemprop="postalCode"]/text()').get()
		item['city'] = response.xpath('//*/span[@itemprop="addressLocality"]/text()').get().strip('\n').strip()
		item['country'] = response.xpath('//*/span[@itemprop="addressLocality"]/text()').getall()[1].strip('\n').strip()
		item['Vertretungsberechtigter'] = response.xpath('//h5[contains(.,"Vertretungsberechtigter")]/following-sibling::p[1]/text()').get().strip('\n').strip()
		item['Registereintrag'] = response.xpath('//h5[contains(.,"(Handels-) Registereintrag")]/following-sibling::p[1]/text()').get().strip('\n').strip()
		item['UStIdNr'] = response.xpath('//h5[contains(.,"USt-IdNr.")]/following-sibling::p[1]/text()').get().strip('\n').strip()
		yield item





