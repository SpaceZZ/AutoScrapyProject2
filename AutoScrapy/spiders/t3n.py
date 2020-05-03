import scrapy
import json
from AutoScrapy.items import t3nItem

class t3n(scrapy.Spider):
	"""
	Spider to get the data from the Baza Firm PL
	"""
	count = 0
	name = "t3nspider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False',
		'FEED_URI' : 'resultst3n.csv'
	}
	allowed_domains = ['t3n.de']
	start_urls = ["https://t3n.de/firmen/kategorie/hosting/",
				  "https://t3n.de/firmen/kategorie/e-commerce/",
				  "https://t3n.de/firmen/kategorie/infrastruktur/",
				  "https://t3n.de/firmen/kategorie/entwicklung-design/",
				  "https://t3n.de/firmen/kategorie/marketing/"]


	def parse(self, response):
		"""
		:param response: the fully downloaded webpage
		:return: the iterator over the categories links
		"""
		list_of_companies = response.xpath('//*/a[@class="company__link"]/@href').extract()
		#remove all the links with "#top" as they are pointing to the top of the screen
		for company in list_of_companies:
			yield scrapy.Request(company, callback=self.parse_data)
		next = response.xpath('//*/a[@rel="next"]/@href').extract_first()
		if next:
			yield scrapy.Request(next, callback=self.parse)


	def parse_data(self, response):
		"""
		Method parses the data for each individual company page
		:param response:
		:return:l-companysingle__description l-section
		"""
		item = t3nItem()

		script = response.xpath('//*/script[@type="application/ld+json"]/text()').extract()
		data = json.loads(script[0])
		item['name'] = data.get('name', '')
		item['url'] = response.request.url

		#desc
		desc = response.xpath('//*/div[@class="l-companysingle__description l-section"]/text()').extract_first()
		if desc:
			lst = [item.strip('\n').strip('\r') for item in desc]
			lst = list(filter(None, lst))
			d = "".join(lst)[0:500]
			item['desc'] = d

		cat = response.xpath('//*/div[@id="js-company-tags"]/ul/li/a/text()').extract()
		item['categories'] = [cat.strip().strip('\n') for cat in cat]

		address = data.get('address', '')
		if address:
			item['street'] = address.get('streetAddress', '')
			item['zip_code'] = address.get('postalCode', '')
			locality = address.get('addressLocality', '')
			if locality:
				address = locality.split(",")
				item['city'] = address[0]
				item['country'] = address[1]
		item['telephone'] = data.get('telephone', '')
		item['email'] = data.get('email', '')
		item['website'] = data.get('url', '')
		links = data.get('sameAs', '')
		for link in links:
			if "twitter" in link:
				item['twitter'] = link
			if "facebook" in link:
				item['facebook'] = link
		linkedin = response.xpath('//*/a[@class="social__item -LINKEDIN tg-social-click"]/@href').extract_first()
		if linkedin:
			item['linkedin'] = linkedin
		yield item


