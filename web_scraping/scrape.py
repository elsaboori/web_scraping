from bs4 import BeautifulSoup as bs
from splinter import Browser
import time
import pandas as pd

def scrape():
	executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
	browser = Browser('chrome', **executable_path, headless=False)

	url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
	browser.visit(url)

	html = browser.html
	soup = bs(html, 'html.parser')
	articles = soup.find_all('div', class_='list_text')

	mars_data = {}
	for article in articles:
	    news_title = article.find('a').get_text()
	    news_p = article.find('div', class_= 'article_teaser_body').get_text()
	    mars_data['news_title']=news_title
	    mars_data['news_p']=news_p
	    break


	## JPL Mars Space Images - Featured Image

	jpl_url='https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
	browser.visit(jpl_url)
	jpl_html = browser.html
	jpl_soup = bs(jpl_html, 'html.parser')
	browser.click_link_by_partial_text("FULL IMAGE")
	time.sleep(.5)
	browser.click_link_by_partial_text("more info")
	#get the link to the full size image 
	featured_image_url= browser.find_by_css("img.main_image")['src']
	mars_data['featured_image_url'] = featured_image_url

	#Getting the weather info
	weather_url ='https://twitter.com/marswxreport?lang=en'
	browser.visit(weather_url)
	time.sleep(.5)
	weather_html = browser.html
	weather_soup = bs(weather_html, 'html.parser')
	tweets= weather_soup.find_all('div', class_='js-tweet-text-container')
	for i in range(len(tweets)):
	    if tweets[i].find("p").text.startswith('Sol'):
	        mars_weather=tweets[i].find("p").text
	        break

	 # Mars facts info
	fact_url = 'https://space-facts.com/mars'
	browser.visit(fact_url)
	time.sleep(.5)
	fact_html = browser.html
	fact_soup = bs(fact_html, 'html.parser')
	fact_table = fact_soup.find("table")
	descreption_td = fact_table.find_all("td", class_="column-1")
	value_td = fact_table.find_all("td", class_="column-2")

	#getting the texts out of tags and create a dataframe of the facts
	descreption = []
	value = []
	for i in range(len(descreption_td)):
	    descreption.append(descreption_td[i].text)
	    value.append(value_td[i].text)
	mars_facts=pd.DataFrame({"Descreption":descreption,
	                      "Value": value})

	#Convert the dataframe to html
	mars_data['mars_facts'] = mars_facts.to_html(index=False)

	# Mars Hemisperes
	hemisperes_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
	hemisperes_dicts = []
	for i in range (1,9,2):    
	    hemisperes_dict = {}
	    browser.visit(hemisperes_url)
	    hemisperes_html = browser.html
	    hemisperes_soup = bs(hemisperes_html,'html.parser')
	    hemisperes_name_links = hemisperes_soup.find_all('a', class_ = 'product-item')
	    hemisperes_name = hemisperes_name_links[i].text.strip('Enhanced')
	    detail_links = browser.find_by_css('a.product-item')
	    detail_links[i].click()
	    time.sleep(.5)
	    browser.find_link_by_text('Sample').first.click()
	    time.sleep(.5)
	    browser.windows.current = browser.windows[-1]
	    hemisperes_img_html = browser.html
	    browser.windows.current = browser.windows[0]
	    browser.windows[-1].close()
	    hemisperes_img_soup = bs(hemisperes_img_html,'html.parser')
	    hemisperes_img_path = hemisperes_img_soup.find('img')['src']
	    hemisperes_dict['title'] = hemisperes_name.strip() 
	    hemisperes_dict['img_url'] = hemisperes_img_path
	    hemisperes_dicts.append(hemisperes_dict)
	mars_data['hemisphere_images']=hemisperes_dicts
	return mars_data
