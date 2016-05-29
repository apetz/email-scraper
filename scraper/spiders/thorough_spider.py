# implementation of the thorough spider

import re
from urllib.parse import urljoin, urlparse
import scrapy
from scrapy.linkextractors import IGNORED_EXTENSIONS
from scraper.items import EmailAddressItem

# scrapy.linkextractors has a good list of binary extensions, only slight tweaks needed
IGNORED_EXTENSIONS.extend(['ico', 'tgz', 'gz', 'bz2'])


def get_extension_ignore_url_params(url):
    path = urlparse(url).path # conveniently lops off all params leaving just the path
    extension = re.search('\.([a-zA-Z0-9]+$)', path)
    if extension is not None:
        return extension.group(1)
    else:
        return "none"  # don't want to return NoneType, it will break comparisons later


class ThoroughSpider(scrapy.Spider):
    name = "spider"

    def __init__(self, domain=None, subdomain_exclusions=[], crawl_js=False):
        self.allowed_domains = [domain]
        start_url = "http://" + domain

        self.start_urls = [
            start_url
        ]
        self.subdomain_exclusions=subdomain_exclusions
        self.crawl_js = crawl_js
        # boolean command line parameters are not converted from strings automatically
        if str(crawl_js).lower() in ['true', 't', 'yes', 'y', '1']:
            self.crawl_js = True

    def parse(self, response):
        # print("Parsing ", response.url)
        all_urls = set()

        # use xpath selectors to find all the links, this proved to be more effective than using the
        #  scrapy provided LinkExtractor during testing
        selector = scrapy.Selector(response)

        # grab all hrefs from the page
        # print(selector.xpath('//a/@href').extract())
        all_urls.update(selector.xpath('//a/@href').extract())
        # also grab all sources, this will yield a bunch of binary files which we will filter out
        # below, but it has the useful property that it will also grab all javavscript files links
        # as well, we need to scrape these for urls to uncover js code that yields up urls when
        # executed! An alternative here would be to drive the scraper via selenium to execute the js
        # as we go, but this seems slightly simpler
        all_urls.update(selector.xpath('//@src').extract())

        # custom regex that works on javascript files to extract relativel urls hidden in quotes.
        # This is a workaround for sites that need js executed in order to follow links -- aka
        # single-page angularJS type designs that have clickable menu items that are not rendered
        # into <a> elements but rather as clickable span elements - e.g. jana.com
        all_urls.update(selector.re('"(\/[-\w\d\/\._#?]+?)"'))

        for found_address in selector.re('[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}'):
            item = EmailAddressItem()
            item['email_address'] = found_address
            yield item

        for url in all_urls:
            # ignore commonly ignored binary extensions - might want to put PDFs back in list and
            # parse with a pdf->txt extraction library to strip emails from whitepapers, resumes,
            # etc.
            extension = get_extension_ignore_url_params(url)
            if extension in IGNORED_EXTENSIONS:
                continue
            # convert all relative paths to absolute paths
            if 'http' not in url:
                url = urljoin(response.url, url)
            if extension.lower() != 'js' or self.crawl_js is True:
                yield scrapy.Request(url, callback=self.parse)