# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# based on the Scrapy Tutorial on item pipelines


class DeDupePipeline(object):
    def __init__(self):
        self.email_addresses_seen = set()

    def process_item(self, item, spider):
        if item['email_address'] in self.email_addresses_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.email_addresses_seen.add(item['email_address'])
            return item