# scrapy-kuntavaalit2021-yle

Fetch all from [YLE Kuntavaalit 2021](https://vaalikone.yle.fi/kuntavaalit2021/) site

    scrapy crawl kaikki

Fetch single municipality (57=Jyväskylä): 

    scrapy crawl kunta -a id=57

## Requirements

* Python
* [Scrapy](https://scrapy.org/)
