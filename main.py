#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import urllib
import sys
import os
import jinja2

sys.path.insert(0, 'libs')
from bs4 import BeautifulSoup
from stop_words import get_stop_words
from urlparse import urlparse, urljoin
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(45)


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)



template_dir=os.path.join(os.path.dirname("_file_"),'templates')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),autoescape=True)

stop_words = get_stop_words('english')



def get_page(page):
	return BeautifulSoup(urllib.urlopen(page).read())

def get_all_links(page,url):     #GETTING LINKS PRESENT IN EACH CRAWLED PAGE
	links=[]
	urls=[]
	page_url=urlparse(url)
	if page_url[0]:
		base = page_url[0] + '://' + page_url[1]
	else:
		base= "https://" + page_url[1]
	# soup=BeautifulSoup(page,'html.parser')
	for link in page.find_all('a'):
	 	link_url=link.get('href')
	 	print "[get_all_links()] Found a link: ", link_url
	 	if link_url == None or "javascript" in link_url or "mailto" in link_url or "tel" in link_url: 
			pass
		elif urlparse(link_url)[5] and not urlparse(link_url)[2]: 
			pass
	 	elif urlparse(link_url)[1]:
			links.append(link_url)
		else:
			newlink = urljoin(base, link_url)
			links.append(newlink)
	return links	

def union(p,q):   
	for e in q:
		if e not in p:
			p.append(e)

def crawl_web(seed):    #CRAWLING ALL WEB PAGES FROM A GIVEN SEED PAGE
	tocrawl=[seed]
	crawled=[]
	i=0
	while tocrawl:
		page=tocrawl.pop()
		if page not in crawled and i<=2:
			content=get_page(page)
			add_page_to_index(index,page,content)
			union(tocrawl,get_all_links(content,page))
			crawled.append(page)
			i=i+1
			


	# return index

index = {}


def add_to_index(index,keyword,url):  #CREATING AN INDEX OF KEYWORDS AND THE URL'S THEY ARE LINKED TO
    # for entry in index:
    #     if entry[0] == keyword:
    #         if url not in entry[1]:
    #             entry[1].append(url)
    #             return
    #     elif keyword in entry[0] and url in entry[1]:
    #         return

    if keyword in index:
    	if url not in index[keyword]:
    		index[keyword].append(url)


    else:
    	index[keyword]=[url]

def add_page_to_index(index,url,content): #SPLITTING EACH WORD PRESENT IN THE TEXT AND REMOVING STOP WORDS AND PUNCTUATIONS
    words=[]
    try:
        text = content.body.get_text()
    except AttributeError:
        return
   

	

    words=text.split()
    punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    for word in words:
		word = word.lstrip(punctuation)
		word = word.rstrip(punctuation)
		word = word.lower()
		if word not in stop_words:
			add_to_index(index, word, url)
    return index 



def lookup(index,keyword): #LOOKING UP THE INDEX TO FIND THE WORDS QUERIED
    urls=[]
    words=[]
    # for key in keyword:
    # 	keyword.replace(key,key.lower())
    keyword=keyword.lower()
    words=keyword.split()
    
    for word in words:
    	if word in index:
    		for url in index[word]:
    			if url not in urls:
    				urls.append(url)
    return urls        




	     
	





# def get_next_target(page):
#     start_link = page.find('<a href=')
#     if start_link == -1: 
#         return None, 0
#     start_quote = page.find('"', start_link)
#     end_quote = page.find('"', start_quote + 1)
#     url = page[start_quote + 1:end_quote]
#     return url, end_quote

# def get_all_links(page):
#     links = []
#     while True:
#         url,endpos = get_next_target(page)
#         if url:
#             links.append(url)
#             page = page[endpos:]
#         else:
#             break
#     return links	

def union_string(p,q):
	for e in q:
		if e not in p:
			p=p+q
	q=p	
	return q	

		
			

# def crawl_web(seed):
# 	tocrawl=[seed]
# 	crawled=[]
# 	while tocrawl:
# 		page=tocrawl.pop()
# 		if page not in crawled:
# 			if page[:4]=="//":
# 				page=seed+page
# 				union(tocrawl,get_all_links(get_page(page)))
# 				crawled.append(page)
# 			else:
				
# 				union(tocrawl,get_all_links(get_page(page)))
# 				crawled.append(page)	
# 	return crawled



def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
	def write(self,*a,**kw):
		self.response.out.write(*a,**kw)

	def	render_str(self,template,**params):
		t=jinja_env.get_template(template)
		return t.render(params)

	def render(self,template,**kw):
		self.write(self.render_str(template,**kw))

class MainHandler(Handler):
    def get(self):
    	crawl_web("http://www.udacity.com/overview/Course/cs101/")
    	self.render("front-page.html")
    # 	self.write(index)
    	

    def post(self):
    	query=self.request.get("query")
    	urls=[]
    	global index
    	urls=list(lookup(index,query))
    	if urls:
    		self.render("front-page.html",urls=urls,query=query)
    	elif not urls:
    		self.redirect('/')	

        
       
        # self.response.out.write(lookup(index,"good idea get enough"))

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
