#!/usr/bin/env python
# coding: utf-8

# In[1]:


## import some libraries
import time
import requests,re
from bs4 import BeautifulSoup
import pandas as pd
import json
import numpy as np
import requests
import os
import glob
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv


# # Get the URLs of starbuck lists in 10 cities

# In[2]:


## top 10 cities with the most starbucks
city_list = pd.Series(["New York","Chicago","Houston","San Diego","Los Angeles",
             "Seattle","Las Vegas","Portland","Phoenix","San Francisco"])


# In[3]:


## get city url
driver = webdriver.Chrome('chromedriver')
def get_url(city):
    time.sleep(5)
    driver.get("https://www.yelp.com/")
    element1 = driver.find_element_by_id("find_desc")
    element1.clear()
    element1.send_keys("Starbucks")

    element2 = driver.find_element_by_id("dropperText_Mast")
    element2.clear()
    element2.send_keys("%s" % city)

    element3 = driver.find_element_by_id("header-search-submit")
    element3.click()
    return(driver.current_url)

url_list = city_list.apply(lambda x: get_url(x))

## save the urls to csv
url_list = pd.DataFrame(url_list)
df.to_csv(r'url_list.csv')


# In[2]:


## open the urls from csv
url_list = pd.read_csv("url_list.csv")['0']


# In[3]:


## change the URLs so that all starbucks stores will show up
url_main_search =url_list.apply(lambda x: re.sub(r'(https://www.yelp.com/search[?])(find_desc=.+)',r'\1choq=1&\2',x))
list(url_main_search)


# # Get the URLs of all starbucks stores

# In[6]:


starbuck_list = list()

kv={'user-agent':'Mozilla/5.0'}
for j in range(len(url_main_search)):
    for i in range(46):
        result = requests.get(url_main_search[j]+"&start="+str(i*10), headers=kv)
        ## parse the content into a BeautifulSoup object
        soup = BeautifulSoup(result.content, 'html.parser')   
        ## find all search items
        search_items = soup.find_all('a', class_="lemon--a__373c0__IEZFH link__373c0__1G70M link-color--inherit__373c0__3dzpk link-size--inherit__373c0__1VFlE")
        ## loop through each item, check if sponsored
        for search_item in search_items:
            link = search_item.get('href')
            if re.match('/biz/starbucks-new-york.*',str(link)):
                starbuck_list.append('https://www.yelp.com'+link)
            elif re.match('/biz/starbucks-chicago.*',str(link)):
                starbuck_list.append('https://www.yelp.com'+link) 
            elif re.match('/biz/starbucks-houston.*',str(link)):
                starbuck_list.append('https://www.yelp.com'+link)
            elif re.match('/biz/starbucks-san-diego.*',str(link)):
                starbuck_list.append('https://www.yelp.com'+link) 
            elif re.match('/biz/starbucks-los-angeles.*',str(link)):
                starbuck_list.append('https://www.yelp.com'+link)
            elif re.match('/biz/starbucks-phoenix.*',str(link)): 
                starbuck_list.append('https://www.yelp.com'+link) 
            elif re.match('/biz/starbucks-seattle.*',str(link)): 
                starbuck_list.append('https://www.yelp.com'+link) 
            elif re.match('/biz/starbucks-las-vegas.*',str(link)): 
                starbuck_list.append('https://www.yelp.com'+link)
            elif re.match('/biz/starbucks-portland.*',str(link)): 
                starbuck_list.append('https://www.yelp.com'+link)
            elif re.match('/biz/starbucks-san-francisco.*',str(link)): 
                starbuck_list.append('https://www.yelp.com'+link)
        time.sleep(2)


# In[7]:


## filter out the closed stores
open_starbuck_list = list()

kv={'user-agent':'Mozilla/5.0'}
for i in range(len(starbuck_list)):
    url = starbuck_list[i]
    result = requests.get(url, headers=kv)
    soup = BeautifulSoup(result.content, 'html.parser') 
    ## whether the store has been closed
    search_closed = soup.find('span', {"class":"lemon--span__373c0__3997G text__373c0__2pB8f text-color--normal__373c0__K_MKN text-align--left__373c0__2pnx_ text-weight--bold__373c0__3HYJa text-size--large__373c0__1568g"})
    if search_closed is None:
        open_starbuck_list.append(url)


# In[9]:


## save the urls to csv
starbuck_list = pd.DataFrame(starbuck_list)
starbuck_list.columns = ['url']
starbuck_list.to_csv(r'starbuck_list.csv')

open_starbuck_list = pd.DataFrame(open_starbuck_list)
open_starbuck_list.columns = ['url']
open_starbuck_list.to_csv(r'open_starbuck_list.csv')


# In[10]:


## open the urls from csv
open_starbuck_list = pd.read_csv("open_starbuck_list.csv")['url']


# # Get the information1 of all starbucks stores
# ### information1: url, name, location, city, zip_code, price, category, score, num_of_review

# In[20]:


def get_info1(opening_stores):
    info1_list = list()
    kv = {'user-agent':'Mozilla/5.0'}
    for i in range(len(opening_stores)):
        url = opening_stores[i]
        result = requests.get(url, headers=kv)
        soup = BeautifulSoup(result.content, 'html.parser') 
        
        ## get store name
        try:
            name = soup.find('h1', {"class":"lemon--h1__373c0__2ZHSL heading--h1__373c0__1VUMO heading--no-spacing__373c0__1PzQP heading--inline__373c0__1F-Z6"}).getText()
        except: 
            name = None
            
        ## get store location,city and zip_code
        try:
            search_location = soup.find_all('p', {"class":"lemon--p__373c0__3Qnnj text__373c0__2pB8f text-color--normal__373c0__K_MKN text-align--left__373c0__2pnx_ text-weight--bold__373c0__3HYJa"})
            if len(search_location)==9:
                location =search_location[0].find("span").getText()
                city_zip = search_location[1].find("span").getText()
            elif len(search_location)==10:
                location =search_location[0].find("span").getText()+' '+search_location[1].find("span").getText()
                city_zip = search_location[2].find("span").getText()
            elif len(search_location)==11:
                location =search_location[0].find("span").getText()+' '+search_location[1].find("span").getText()+' '+search_location[2].find("span").getText()
                city_zip = search_location[3].find("span").getText()
            city = re.sub(r'(.+)(,.+)',r'\1',city_zip)
            zip_code = re.sub(r'(.+)(,.+)(\s)(\d+)',r'\4',city_zip)
        except: 
            location=None
            city = None
            zip_code = None
            
        ## get store price
        try:
            search_price = soup.find('span', {"class":"lemon--span__373c0__3997G text__373c0__2pB8f text-color--normal__373c0__K_MKN text-align--left__373c0__2pnx_ text-bullet--after__373c0__1ZHaA text-size--large__373c0__1568g"})
            price = search_price.getText()[:-1]
        except: price = None
            
        ## get store catrgory
        try:
            search_category = soup.find_all('a', {"class":"lemon--a__373c0__IEZFH link__373c0__29943 link-color--inherit__373c0__15ymx link-size--inherit__373c0__2JXk5"})
            category = search_category[0].getText()
        except: category = None
            
        ## get store score
        try:
            search_score = soup.find('span', {"class":"lemon--span__373c0__3997G display--inline__373c0__1DbOG border-color--default__373c0__2oFDT"})
            score = re.findall(r'\S+',search_score.findChild().get('aria-label'))[0]
        except: score = None
            
        ## get the num of reviews
        try:
            search_num_of_review = soup.find('p', {"class":"lemon--p__373c0__3Qnnj text__373c0__2pB8f text-color--mid__373c0__3G312 text-align--left__373c0__2pnx_ text-size--large__373c0__1568g"})
            num_of_review = re.findall(r'\S+',search_num_of_review.getText())[0]
        except: num_of_review = None
            
        ## combine information of all stores
        time.sleep(1)
        info1_list.append([url, name, location, city, zip_code, price, category, score, num_of_review])
    return(info1_list)


# In[21]:


info1 = get_info1(open_starbuck_list)


# In[23]:


information1 = pd.DataFrame(info1)
information1.columns = ['url','name','location','city','zip_code', 'price', 'category','score', 'num_of_review']


# # Get the information2 of all starbucks stores
# ### information2: url,reviews, review scores, review time, image1, image2, image3

# In[24]:


info2 = list()
kv = {'user-agent':'Mozilla/5.0'}
for i in range(len(open_starbuck_list)):
    url = open_starbuck_list[i]
    result = requests.get(url, headers=kv)
    soup = BeautifulSoup(result.content, 'html.parser') 
    chunks = soup.find_all('div', {"class":"lemon--div__373c0__1mboc arrange-unit__373c0__1piwO arrange-unit-grid-column--8__373c0__2yTAx border-color--default__373c0__2oFDT"})[1:21]
    for chunk in chunks:
        
        ## get the url
        url = url
        
        ## get the review score
        try:
            review_score = re.findall(r'\S+',chunk.find('div',{"role":"img"}).get("aria-label"))[0]
        except: review_score = None
        
        ## get the review time
        try:
            review_time = chunk.find('span', {"class":"lemon--span__373c0__3997G text__373c0__2pB8f text-color--mid__373c0__3G312 text-align--left__373c0__2pnx_"}).getText()
        except: review_time = None
        
        ## get the review content
        try:
            review = chunk.find('span', {"lang":"en"}).getText()
        except: review = None
        
        ## get the top 3 images
        try:
            image1 = chunk.find_all('img',{"class":"lemon--img__373c0__3GQUb photo-box-img__373c0__O0tbt"})[0].get("src")
        except: image1 = None
        try:
            image2 = chunk.find_all('img',{"class":"lemon--img__373c0__3GQUb photo-box-img__373c0__O0tbt"})[1].get("src")
        except: image2 = None
        try:
            image3 = chunk.find_all('img',{"class":"lemon--img__373c0__3GQUb photo-box-img__373c0__O0tbt"})[2].get("src")
        except: image3 = None
        
        ## combine all information
        info2.append([url, review_score, review_time, review, image1, image2, image3])


# In[25]:


information2 = pd.DataFrame(info2)
information2.columns = ['url','review_score','review_time','review_text','image1', 'image2', 'image3']


# In[38]:


## use "city-number" as store_id
for i in range(len(information1)):
    information1['url'][i] = re.sub(r'.*starbucks-(.*)\?.*',r'\1', information1['url'][i])

for i in range(len(information2)):
    information2['url'][i] = re.sub(r'.*starbucks-(.*)\?.*',r'\1', information2['url'][i])

## rename the "url" column to "store_id"
information1 = information1.rename(columns = {'url': 'store_id'})
information1.head()


# In[39]:


information2 = information2.rename(columns = {'url': 'store_id'})
information2.head()


# In[41]:


## transform price levels to numbers
for i in range(len(information1)):
    if information1['price'][i] == '$':
        information1['price'][i] = 1
    elif information1['price'][i] == '$$':
        information1['price'][i] = 2
    elif information1['price'][i] == '$$$':
        information1['price'][i] = 3
    elif information1['price'][i] == '$$$$':
        information1['price'][i] = 4
    else:
        continue

information1.head()


# In[42]:


## add review_id
ids = pd.DataFrame(data = {'review_id': range(1, len(information2)+1)})
information2 = pd.concat([ids, information2], axis = 1)
information2.head()


# In[43]:


## save two tables
information1.to_csv(r'information1.csv')
information2.to_csv(r'information2.csv')


# # Import final table to MongoDB

# In[44]:


import pymongo
import json
from bson.code import Code


# In[47]:


myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["starbucks"]

mycol1 = mydb["store"]
mycol2 = mydb["review"]


# In[48]:


## save two tables as json files
information1.to_json('starbucks_info1.json', orient = 'records', lines = True)
information2.to_json('starbucks_info2.json', orient = 'records', lines = True)


# In[49]:


## insert store data
store_data = []
with open('starbucks_info1.json', 'r') as f:
    for line in f:
        store_data.append(json.loads(line))

mycol1.insert_many(store_data)


# In[50]:


## insert review data
review_data = []
with open('starbucks_info2.json', 'r') as f:
    for line in f:
        review_data.append(json.loads(line))

mycol2.insert_many(review_data)


# In[51]:


for x in mycol1.find().limit(25):
    print(x)


# In[52]:


for x in mycol2.find().limit(25):
    print(x)


# In[ ]:




