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
import urllib2
import sys
import os
import jinja2
import re
reload(sys)
sys.setdefaultencoding('utf-8')


sys.path.insert(0, 'libs')
from bs4 import BeautifulSoup
from stop_words import get_stop_words
from urlparse import urlparse, urljoin
from google.appengine.api import urlfetch
import robotexclusionrulesparser as rerp
urlfetch.set_default_fetch_deadline(45)


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)



template_dir=os.path.join(os.path.dirname("_file_"),'templates')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),autoescape=True)

stop_words = get_stop_words('english')

import ssl
context = ssl._create_unverified_context()

def get_page(page):

	page_url = urlparse(page)
	if page_url[0]:
		base = page_url[0] + '://' + page_url[1]
		robots_url=urljoin(base,'/robots.txt')
	else:
		base= "https" + page_url[2]
		robots_url=urljoin(base,'/robots.txt')
	rp=rerp.RobotFileParserLookalike()
	rp.set_url(robots_url)
	try:
		rp.read()
	except:
		pass
	if not rp.can_fetch('*', page):
		print "[get_page()] Page off limits!"
		return BeautifulSoup(""), ""

	if page in cache:
		return cache[page],page
	else:
		try:
			return BeautifulSoup(urllib2.urlopen(page,context=context).read()),page
		except:
			return BeautifulSoup("",features="html.parser"),""

	

def get_all_links(page,url):     #GETTING LINKS PRESENT IN EACH CRAWLED PAGE
	links=[]
	urls=[]
	page_url=urlparse(url)
	try:
		page_data=urllib2.urlopen(url)
	except:
		pass
	# if page_data.getheader('Content-Type')=="text/html":
	if page_url[0]:
		base = page_url[0] + '://' + page_url[1]
		robots_url=urljoin(base,'/robots.txt')
	else:
		base= "https" + page_url[2]
		robots_url=urljoin(base,'/robots.txt')
	rp=rerp.RobotFileParserLookalike()
	try:
		rp.read()
	except:
		pass
	# soup=BeautifulSoup(page,'html.parser')
	for link in page.find_all('a'):
	 	link_url=link.get('href')
	 	
	 	print "[get_all_links()] Found a link: ", link_url
		try:
		 	if link_url == None or "javascript" in link_url or "mailto" in link_url or "tel" in link_url: 
				pass
			elif urlparse(link_url)[5] and not urlparse(link_url)[2]: 
				pass
		 	elif urlparse(link_url)[1]:
		 		if is_youtube(link_url):
					links.append(link_url)
			else:
				newlink = urljoin(base, link_url)
				if is_youtube(newlink):
					links.append(newlink) 
		except ValueError as e:
			print e
	return links	

def union(p,q):   
	for e in q:
		if e not in p:
			if is_youtube(e):
				p.append(e)

def crawl_web(seed):   #CRAWLING ALL WEB PAGES FROM A GIVEN SEED PAGE
	tocrawl=[]  
	for urls in seed:
		if is_youtube(urls):
			tocrawl.append(urls)

	crawled=[]
	i=5
	while len(tocrawl)>0:
		i-=1
		if i>0:
			for pg in range(len(tocrawl)):
				# print(len())
				page=tocrawl.pop(0)
				if page not in crawled and len(crawled)<50 and is_youtube(page):
					print("Crawling: ",page)
					content,page=get_page(page)
					cache[page] = content
					get_page_data(content, page, pagedata)
					add_page_to_index(index,page,content)
					outlinks=get_all_links(content,page)
					graph[page]=outlinks
					union(tocrawl,outlinks)
					crawled.append(page)
		else:
			break

				# i=i+1
			
			
def get_page_data(page, url, dict):
	try:
		title = page.title.string
	except:
		title = url
	try:
		page.body.style.decompose()
		page.body.script.decompose()
		text = page.article.get_text()
	except:
		text = ''
	dict[url] = [title, text]

	# return index

index ={}
graph={}
cache={}
pagedata={}

def add_to_index(index,keyword,url):  #CREATING AN INDEX OF KEYWORDS AND THE URL'S THEY ARE LINKED TO
   

    if keyword in index:
    	if url not in index[keyword]:
    		index[keyword].append(url)


    else:
    	index[keyword]=[url]

def add_page_to_index(index,url,content): #SPLITTING EACH WORD PRESENT IN THE TEXT AND REMOVING STOP WORDS AND PUNCTUATIONS
    words=[]
    try:
        text = content.body.get_text().encode('utf-8')
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




def compute_ranks(graph): ## Page ranking algorithm
    d = 0.8 # damping factor
    numloops = 20
    
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for nodes in graph:
                if page in graph[nodes]:
                    newrank=newrank + (d*ranks[nodes])/len(graph[nodes])
            newranks[page] = newrank
        ranks = newranks
    return ranks



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



def is_youtube(page):
	parsed_url=urlparse(page)
	if parsed_url[1]=="in.news.yahoo.com":
		return True
	else:
		False



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

# def union_string(p,q):
# 	for e in q:
# 		if e not in p:
# 			if is_youtube(e):
# 				p=p+q
# 	q=p	
# 	return q	


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


seed=["https://in.news.yahoo.com/"]
crawl_web(seed)

class MainHandler(Handler):
    def get(self):
    	
    	self.render("front-page.html")
    	# self.write(index)
    	

    def post(self):
    	
    	query=self.request.get("query")
        page_num = self.request.get("pageno")
        start = int(page_num) * 5
        end = (int(page_num) + 1) * 5
    	urls=[]
    	global index
    	urls=list(lookup(index,query))
        if end < len(urls):
            urls = urls[start:end]
        elif start < len(urls):
            urls = urls[start:(len(urls)-1)]
    	if urls:
    		self.render("front-page.html",urls=urls,query=query,pagedata=pagedata)
    	elif not urls:
    		self.render("front-page.html",urls=urls,query=query,error="Sorry, No Results Found!")


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)

def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='8080')

if __name__ == '__main__':
    main()

