# treasurehunt
Built a Search Engine from ground up, including **web crawlers**. It uses **Breadth First Search** to crawl the websites, with the depth of the BFS being configurable.

Added features and a very simple User Interface for keyword lookup, with results being served according to the **PageRank** Algorithm.

Have create **Indexes** on the keywords too. For now it supports single keyword lookup only.



## Downloads required
   Some of the modules being used are:
1) Google App Engine
2) Beautiful Soup
3) Webapp2

Can download all the modules using 
```bash
pip install -r requirements.txt
``` 
Also make sure to download the Stop Words Library - https://pypi.python.org/pypi/stop-words


## Run
```bash
python main.py
``` 
