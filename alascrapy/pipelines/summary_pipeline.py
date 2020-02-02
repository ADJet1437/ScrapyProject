"""
This pipeline is used for summary the spider log, the mainly information 
include missed items, dropped reviews.
"""

from datetime import datetime, timedelta
import os
import json
import re

from alascrapy.pipelines import AlascrapyPipeline


class SummayLogPipeline(AlascrapyPipeline):

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def get_summary_data(self, log_file):
        with open(log_file, 'r') as f:
            rating_count = 0
            date_count = 0
            summary_count = 0
            drop_count = 0
            for line in f.readlines():
                if 'missing required field SourceTestRating' in line:
                    rating_count += 1
                if 'missing required field TestDateText' in line:
                    date_count += 1
                if 'missing required field TestDateText' in line:
                    date_count += 1
                if 'missing required field TestSummary' in line:
                    summary_count += 1
                if 'Dropped' in line:
                    drop_count += 1

            return "Missed SourceTestRating: " + str(rating_count) + '\n', \
                "Missed TestDateText: " + str(date_count) + '\n', \
                "Missed TestSummary:" + str(summary_count) + '\n', \
                "Droped review: " + str(drop_count) + '\n'

    def _process_item(self, item, spider):
        pass

    def close_spider(self, spider):
        self.spider = spider
        log_dir = self.spider.get_spider_log_dir()

        log_file = '{}/{}'.format(log_dir, '{}.log'.format(self.spider.name))

        sum_filename = '{}_summary.txt'.format(self.spider.name)

        data = self.get_summary_data(log_file)

        stats = self.stats.get_stats()
        start_time = stats.get('start_time', '')
        products_scraped_count = stats.get('items/products_scraped_count', '')
        reviews_scraped_count = stats.get('items/reviews_scraped_count', '')

        with open(os.path.join(log_dir, sum_filename), 'w+') as sum_file:
            for i in data:
                sum_file.write(str(i).lstrip())

            sum_file.write("Total scraped product:" +
                           str(products_scraped_count) + '\n')
            sum_file.write("Total scraped review: " +
                           str(reviews_scraped_count) + '\n')

            if re.search(r'product_ids_scraped_count', str(stats)):
                product_id_scraped_count = stats.get(
                    'items/product_ids_scraped_count', '')
                sum_file.write("Total scraped product_id:" +
                               str(product_id_scraped_count) + '\n')
            # scrapy time is 2 hour late than here
            finish_time = datetime.now() - timedelta(hours=2)
            total_time = finish_time - start_time

            sum_file.write('Process time:' + str(total_time) + '\n')
