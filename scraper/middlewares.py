# very basic subdomain blocking middleware to intercept requests and drop them if the url is for
# a subdomain that is on the blocked list. This is inspired by the blog.jana.com subdomain which
# if crawled, results in an explosion of urls that are hit due to the many pages and embedded links
# within the blog

import logging
import re
from scrapy.exceptions import IgnoreRequest


class SubdomainBlockerMiddleware:
    name = "SubdomainBlockerMiddleware"

    def process_request(self, request, spider):
        # grab subdomain if it exists and check if it's on the exclusion list
        subdomain = re.match('(?:http[s]*://)*([-\w\d]+)\.', request.url).group(1)
        if subdomain in spider.subdomain_exclusions:
            logging.warning("Dropped request for excluded subdomain {}".format(subdomain))
            raise IgnoreRequest()
        else:
            return None
