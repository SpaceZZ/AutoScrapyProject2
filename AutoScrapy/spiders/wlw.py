import scrapy
import json
from AutoScrapy.items import WLWItem

class t3n(scrapy.Spider):
	"""
	Spider to get the data from the wlw.de
	"""
	count = 0
	name = "wlwspider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False',
		'FEED_URI' : 'resultsWLW.csv'
	}
	allowed_domains = ['wlw.de']
	start_urls = ["https://www.wlw.de/de/firmen/online-shopping-software",
				  "https://www.wlw.de/de/firmen/software-fuer-electronic-business"]


	def parse(self, response):
		"""
		:param response: the fully downloaded webpage
		:return: the iterator over the categories links
		"""
		category = response.url.split('/')[-1].split('?')[0]
		list_of_companies = response.xpath('//*/div[@class="h4 panel__title"]/a/@href').extract()
		#remove all the links with "#top" as they are pointing to the top of the screen
		for company in list_of_companies:
			item = WLWItem()
			item['category'] = category
			yield scrapy.Request(response.urljoin(company), callback=self.parse_data, meta={'item': item})
		next = response.xpath('//*/ul[@class="pagination"]/li')[-1].xpath('.//@href').extract_first()
		if next and next is not '#':
			yield scrapy.Request(response.urljoin(next), callback=self.parse)


	def parse_data(self, response):
		"""
		Method parses the data for each individual company page
		:param response:
		:return:
		"""
		item = response.meta['item']

		script = response.xpath('//*/script[@type="application/ld+json"]/text()').extract()
		data = json.loads(script[0])
		item['name'] = data.get('legalName', '')
		item['url'] = response.request.url
		item['email'] = data.get('email', '').replace('mailto:', '')
		item['telephone'] = data.get('telephone', '')
		item['website'] = data.get('url','')
		#desc
		desc = data.get('description', '')
		if desc:
			item['desc'] = desc.strip().strip('\n')[0:1000]

		cat = response.xpath('//*/div[@class="category__title"]/text()').extract()
		item['categories'] = [cat.strip().strip('\n') for cat in cat]

		address = data.get('address', '')
		if address:
			item['street'] = address.get('streetAddress', '')
			item['zip_code'] = address.get('postalCode', '')
			item['city'] = address.get('addressLocality', '')
			item['country'] = address.get('addressCountry', '')

		employees = data.get('employee','')
		contacts = []
		for employee in employees:
			if employee.get('email', ''):
				contact = employee.get('givenName', '') + " " + employee.get('familyName', '') + " " + employee.get('email', '') + " " + employee.get('telephone', '')
				contacts.append(contact)
		contacts = [contact.strip() for contact in contacts]
		if contacts:
			item['contacts'] = contacts
		else:
			contact = response.xpath('//*/address[@class="location-and-contact__address"]/div[1]/text()').extract_first()
			item['contacts'] = contact
		yield item


