import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import TietoaItem
from itemloaders.processors import TakeFirst
import json

pattern = r'(\xa0)?'

class TietoaSpider(scrapy.Spider):
	name = 'tietoa'
	start_urls = ['https://www.sttinfo.fi/public-website-api/pressroom/4300/releases/20/0']
	base = 'https://www.sttinfo.fi'

	def parse(self, response):
		data = json.loads(response.text)

		for element in range(len(data['releases'])):
			url =data['releases'][element]['url']
			post_links = self.base + url
	# 		post_links = post_links.replace('release', 'tiedote')
			yield response.follow(post_links,self.parse_post)

		pages= data['paging']['count']//data['paging']['itemsPerPage'] + (data['paging']['count'] % data['paging']['itemsPerPage'] >0)
		for page in range(pages):
			yield response.follow(f'https://www.sttinfo.fi/public-website-api/pressroom/4300/releases/20/{page}', self.parse)

	def parse_post(self, response):
		date = response.xpath('//p[@class="release__Byline-sc-6son67-1 hnaWCN"]/text()').get().split(' ')[0]
		title = response.xpath('//h1[@class="text-elements__Title-sc-1il5uxg-0 iYhqHy"]/span/text()').get()
		content = response.xpath('//p[@class="text-elements__Leadtext-sc-1il5uxg-2 fnUQeV"]//text()').getall() + response.xpath('//div[@class="release__PublicationContent-sc-6son67-0 liWhHr"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=TietoaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
