import scrapy
from AutoScrapy.items import HandlerListItem

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
	'Accept-Language': 'en-US,en;q=0.9,pl-PL;q=0.8,pl;q=0.7,nl-NL;q=0.6,nl;q=0.5',
	'content-type': 'application/json',
	}


class HandlerList(scrapy.Spider):
	"""
	Spider to get the data from the eurocis
	"""
	count = 0
	name = "HandlerListSpider"

	custom_settings = {
		'DOWNLOAD_DELAY': 1.5,
		'RANDOMIZE_DOWNLOAD_DELAY': 'False',
		'FEED_URI': 'handler_list.csv'
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
			item['name'] = link_selector.xpath('/div[1]/a/@text()').extract()
			redirect_url = link_selector.xpath('/div[1]/a/@href').extract()
			item['url'] = response.urljoin(redirect_url)
			address_unstructured = link_selector.xpath('/div[3]//text()').extract()
			# unpack address
			item['name_long'], item['street'], item['zip_code'], item['city'] = self.deconstruct_address(
				address_unstructured)
			# go to next link and pass already filled item
			yield scrapy.Request(item['url'], callback=self.parse_data, meta=item)
		next = response.xpath('//a[@aria-label="Gehe eine Seite vor"]').extract_first()
		if next:
			yield scrapy.Request(response.urljoin(next), callback=self.parse)

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
			rest_of_addres = address_part[1].split()
			# get the zipcode
			zip_code = rest_of_addres.pop(0)
			# get city
			city = " ".join(rest_of_addres)
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
		item['email'] = email

	phones = response.xpath('//div[@class="tblitem"]/span[@class="notrans"]').extract()
	if len(phones) >= 2:
		item['phone'] = phones[0]
		item['fax'] = phones[1]
	else:
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

	yield item
