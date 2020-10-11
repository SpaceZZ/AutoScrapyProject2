import scrapy
from AutoScrapy.items import HandlerListItem
import urllib.parse
import requests

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
	'Accept-Language': 'en-US,en;q=0.9,pl-PL;q=0.8,pl;q=0.7,nl-NL;q=0.6,nl;q=0.5',
	'content-type': 'application/json',
}


class HandlerList(scrapy.Spider):
	"""
	Spider to get the data from the eurocis
	"""
	name = "HandlerListSpider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False',
		'FEED_URI': 'handler_list.csv',
		'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
	}
	allowed_domains = ['geizhals.de']
	start_urls = ["https://geizhals.de/?keywords=hlist"]

	def parse(self, response):
		"""
		Method looks for the indexes

		:param response: the fully downloaded webpage
		:return: the iterator over the categories links
		"""
		list_of_links_selector = response.xpath('.//*/div[@class="steel_list_container hlist_table"]/div[@class="row"]')
		for link_selector in list_of_links_selector:
			item = HandlerListItem()

			if "pg=" in response.url:
				position_begin = response.url.find("pg=") + 3
				item['page'] = response.url[position_begin:]
			else:
				item['page'] = 1

			item['name'] = link_selector.xpath('./div[1]/a/text()').extract_first()
			redirect_url = link_selector.xpath('./div[1]/a/@href').extract_first()
			item['url'] = "https://" + HandlerList.allowed_domains[0] + "/" + redirect_url
			address_unstructured = link_selector.xpath('./div[3]//text()').extract()
			# unpack address
			item['name_long'], item['street'], item['zip_code'], item['city'] = self.deconstruct_address(
				address_unstructured)
			# go to next link and pass already filled item
			print("Link", item['url'])
			yield scrapy.Request(item['url'], callback=self.parse_data, meta={'item': item})

		next = response.xpath('//a[@aria-label="Gehe eine Seite vor"]/@href').extract_first()
		if next:
			next = next[1:]
			link = "http://geizhals.de" + next
			print("Next page", link)
			yield scrapy.Request(link, callback=self.parse)

	def deconstruct_address(self, address_unstructured):
		"""
		Method to deconstruct address from unorganized list
		:param self:
		:type self:
		:param address_unstructured:
		:type address_unstructured:
		:return: return a tuple with address
		:rtype:
		"""
		long_name = ''
		street = ''
		zip_code = ''
		city = ''

		# remove all line breaks or other white spaces
		processed_list = [item for item in address_unstructured if not item.isspace()]

		# if 3 elements in the list = long name, address
		if len(processed_list) == 2:
			long_name = processed_list[0]
			address_part = processed_list[1].split(",")
			street = address_part[0]
			rest_of_address = address_part[1].split()
			# get the zipcode
			if rest_of_address:
				zip_code = rest_of_address.pop(0)
				# get city
				city = " ".join(rest_of_address)
		# no long name, only address
		else:
			address_part = processed_list[0].split(",")
			street = address_part[0]
			rest_of_address = address_part[1].split()
			# get the zipcode
			zip_code = rest_of_address.pop(0)
			# get city
			city = " ".join(rest_of_address)

		return long_name, street, zip_code, city

	def parse_data(self, response):
		"""
		Method parses the data for each individual company page
		:param response:
		:return:
		"""
		item = response.meta['item']

		email = response.xpath('//a[contains(string(),"@")]//text()').extract()
		if email:
			item['email'] = ",".join(email)

		phones = response.xpath('//div[@class="tblitem"]/span[@class="notrans"]/text()').extract()
		if len(phones) >= 2:
			item['phone'] = phones[0]
			item['fax'] = phones[1]
		else:
			if phones:
				item['phone'] = phones[0]

		# get the stars rating if exists
		stars_rating = response.xpath('//span[@class="gh_stars"]/@title').extract_first()
		if stars_rating:
			item['stars_rating'] = stars_rating.split()[0]

		raw_website = response.xpath('//div[@class="top_icons"]/span/a/@href').extract()[1]

		# do some finding in the url
		if raw_website:
			end = raw_website.find("&key")
			beginning = raw_website.find("2F%2F") + 5
			item['website'] = "http://" + raw_website[beginning:end]

		# something went wrong with website
		if len(item['website']) > 50:
			request = requests.get("http://" + HandlerList.allowed_domains[0] + raw_website, headers=headers)
			if request.history:
				raw_url = request.url
				# take only schema and network, leave rest
				schema, network, *_ = urllib.parse.urlparse(raw_url)
				item['website'] = schema + "://" + network
				print("Constructed link from schema", item['website'])

		# webpages = re.findall(r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", raw_website)
		# if len(webpages) > 1:
		# 	item['website'] = webpages[1]
		# else:
		# 	if webpages:
		# 		item['website'] = webpages[0]
		yield item
