#! python3

import requests
from bs4 import BeautifulSoup
from pprint import pprint

# usuario define o termo da busca
search_string = input('Digite o termo de busca: ')

# obter codigo html da pagina que vamos ler
search_url = 'https://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords='+search_string
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}
response_object = requests.get(search_url, headers=headers)

# selecionar os elementos referentes aos produtos
search_soup = BeautifulSoup(response_object.text, features='html.parser')
product_elems = search_soup.select('div.'+'.'.join('sg-col-20-of-24 s-result-item sg-col-0-of-12 sg-col-28-of-32 sg-col-16-of-20 sg-col sg-col-32-of-36 sg-col-12-of-16 sg-col-24-of-28'.split()))
# product_elems = search_soup.select('div.'+'.'.join('s-card-container s-overflow-hidden aok-relative puis-expand-height puis-include-content-margin s-latency-cf-section s-card-border'.split()))
print(search_soup)

print('Foram obtidos {} produtos.'.format(len(product_elems)))

product_list = []
# retirar os dados de cada produto e armazenar no dicionario
for product in product_elems:
	product_soup = BeautifulSoup(str(product), features='html.parser')

	description_elem = product_soup.select_one('span.'+'.'.join('a-size-medium a-color-base a-text-normal'.split()))
	description_text = description_elem.text

	price_whole_elem = product_soup.select_one('span.a-price-whole')
	if price_whole_elem:
		price_whole_text = price_whole_elem.text
	else:
		price_whole_text = '0'
	
	price_fraction_elem = product_soup.select_one('span.a-price-fraction')
	if price_fraction_elem:
		price_fraction_text = price_fraction_elem.text
	else:
		price_fraction_text = '.0'

	image_elem = product_soup.select_one('img.s-image')
	image_src = image_elem.get('src')

	url_elem = product_soup.select_one('a.a-link-normal')
	url_href = 'https://www.amazon.com' + url_elem.get('href')


	product_dict = {'description': description_text, 
					'price'      : float(price_whole_text + price_fraction_text), 
					'image'      : image_src, 
					'url'        : url_href}
	
	product_list.append(product_dict)

pprint(product_list)
