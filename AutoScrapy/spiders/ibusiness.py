import scrapy
from AutoScrapy.items import IBusinessItem
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
	name = "ibusinessspider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False',
		'FEED_URI': 'resultibusiness.csv'
	}
	allowed_domains = ['www.ibusiness.de']
	start_urls = ["https://www.ibusiness.de/dienstleister/?aktion=suche&start=0&anzahl=100&order=score&jahrbuch_land=Deutschland&umkreis=0&land=Deutschland"]

	def parse(self, response):
		"""
		Method looks for the indexes

		:param response: the fully downloaded webpage
		:return: the iterator over the categories links
		"""
		list_of_indexes = response.xpath('//*/a[@class="arrowLinkMedium"]/@href').extract()
		for index in list_of_indexes:
			if 'jb' in index:
				yield scrapy.Request(response.urljoin(index), callback=self.parse_data)
		next = response.xpath('//*/div[@class="switchForward"]/a/@href').extract_first()
		if next:
			yield scrapy.Request(response.urljoin(next), callback=self.parse)

	def parse_data(self, response):
		"""
		Method parses the data for each individual company page
		:param response:
		:return:
		"""
		item = IBusinessItem()
		item['name'] = response.xpath('//*/h2[@style="font-size:130%"]/text()').extract_first()
		item['url'] = response.request.url

		address = response.xpath('//*/h2[@style="font-size:130%"]/../text()').extract()
		data = [line.strip().strip('\n').replace('\n', '') for line in address if line]
		data = list(filter(None, data))
		if data:
			if len(data) >= 3:
				d = " ".join(data[1].replace('\r', '').split())
				item['address'] = data[0] + d + " " + data[2]
				for line in data:
					if 'Telefon:' in line:
						item['telephone'] = line.replace('Telefon: ', '')
					if 'Telefax:' in line:
						item['fax'] = line.replace('Telefax: ', '')
			else:
				item['address'] = data[0]

		mail = response.xpath('//*/h2[@style="font-size:130%"]/../a/@href').extract()
		if mail:
			for line in mail:
				if 'http' in line:
					item['website'] = line
				if 'mailto:' in line:
					item['email'] = line.replace('mailto:', '')

		desc = response.xpath('//*/h2[contains(.,"Kurzprofil:")]/../text()').extract()
		if desc:
			lst = [line.strip() for line in desc]
			lst = list(filter(None, lst))
			d = "".join(lst)[0:500]
			item['desc'] = d

		updated = response.xpath('//*[contains(text(),"Aktualisiert am:")]/text()').extract_first()
		if updated:
			item['date_updated'] = updated.split(':')[1].strip()
		yield item


