# email-scraper
A general-purpose utility written in Python (v3.0+) for crawling websites to extract email addresses.

## Overview
I implemented this using the popular python web crawling framework **scrapy**. I had never used it before so this is probably not the most elegant implementation of a scrapy-based email scraper (say that three times fast!). The project consists  of a single spider ***ThoroughSpider*** which takes 'domain' as an argument and begins crawling there. Two optional arguments add further tuning capability:
* subdomain_exclusions - optional list of subdomains to exclude from the crawl
* crawl_js - optional boolean [default=False], whether or not to follow links to javascript files and also search them for urls

The **crawl_js** parameter is needed only when a "perfect storm" of conditions exist:

1. there is no sitemap.xml available

2. there are clickable menu items that are **not** contained in ```<a>``` tags

3. those menu items execute javascript code that loads pages but the urls are in the .js file itself

Normally such links would not be followed and scraped for further urls, however if a single-page AngularJS-based site with no sitemap is crawled, and the menu links are in ```<span>``` elements, the pages will not be discovered unless the ng-app is crawled as well to extract the destinations of the menu items.

A possible workaround to parsing the js files would be to use Selenium Web Driver to automate the crawl. I decided against this because Selenium needs to know how to find the menu using CSS selector, class name, etc. and these are specific to the site itself. A Selenium-based solution would not be as general-purpose, but for an AngularJS-based menu, something like the following would work in Selenium:
```
from selenium import webdriver
driver = webdriver.Firefox()
driver.get("http://angularjs-site.com")
menuElement = driver.find_element_by_class_name("trigger")
menuElement.click()
driver.find_elements_by_xpath('//li')[3].click() # for example, click the third item off the discovered menu list
```

For this solution I opted to design the crawler ***without*** Selenium, which means occasionally crawling JS files to root out further links.

### Implemented classes:
* ```ThoroughSpider```: the spider itself
* ```DeDupePipeline```: simple de-duplicator so that email addresses are only printed out once even if they are discovered multiple times
* ```SubdomainBlockerMiddleware```: blocks subdomains in case crawl needs to exclude them
* ```EmailAddressItem```: holds the email addresses as scrapy.Items. Allows the scrapy framework to output items into a number of 
convenient formats (csv, json, etc.) without additional dev work on my end

### Required Modules
This project is dependent on the following python modules:
* scrapy
* urlparse

### How to Run
Since it is scrapy based, it must be invoked via the standard "scrapy way":
 ```
 scrapy crawl spider -a domain="your.domain.name" -o emails-found.csv
 ```
Or with optional command line arguments like:
```
scrapy crawl spider -a domain="your.domain.name" -a subdomain_exclusions="['blog', 'technology']" -a crawl_js=True -o emails-found.csv
```


## Testing
I tested this mainly against my own ***incomplete*** blog www.quackquaponics.com and personal website www.tpetz.com, where I hid email addresses around the sites and also hid links to various JS files to test how well the parsing worked. There is also a simple unit test for the  ThoroughMiddleware.parse method in test_spider.py. It utilizes a static file, html-test.html, which can be extended with various hard-to-find email addresses to see if they can be discovered. To run the unit test, do
```
python3 test_spider.py
```


## Known Issues
1. The email regex utilized to find addresses is not RFC 822 compliant. That is easily fixed if needed, but in practice, most real-world validators are not RFC 822 compliant either, and the regex I used is *much* simpler than a fully compliant one.

## Future Work
* Add PDF-parsing support via PDF -> Text transform library to extract email addresses from PDFs (e.g. whitepapers, resumes, etc.)