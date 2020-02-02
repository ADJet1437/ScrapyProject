from alascrapy.spiders.base_spiders.amazon import AmazonCSV
from alascrapy.items import CategoryItem, AmazonProduct, AmazonCollection
from alascrapy.lib.log import log_exception
from scrapy.exceptions import DropItem
from copy import deepcopy

SALESRANK_LIMIT = 100000

class AmazonReviewPipeline(object):
    """

    """
    def process_item(self, item, spider):
        if not isinstance(spider, AmazonCSV):
            return item

        if isinstance(item, CategoryItem):
            return item
        elif isinstance(item, AmazonProduct):
            asin = item['asin']["ID_value"]
            salesrank = item.get('salesrank', {}).get('ID_value', None)
            if salesrank<=SALESRANK_LIMIT:
                spider._amazon_check_reviews[asin] = item
        else:
            raise DropItem("AmazonCSV yielded invalid item. Valid items"
                            "are CategoryItem and dict")

        if len(spider._amazon_check_reviews)>=10:
            amazon_collection = AmazonCollection()
            amazon_collection['collection'] = {}

            asins = spider._amazon_check_reviews.keys()[:10]
            try:
                have_reviews = spider.amazon_api.have_reviews(asins)
            except Exception,e:
                log_exception(spider.logger, e)
                raise DropItem("Could not verify reviews")

            errors = have_reviews['errors']
            if errors:
                raise DropItem(str(errors))

            have_reviews_asins = have_reviews['asins']
            return_dict = {}
            for asin in have_reviews['invalid_asins']:
                spider._amazon_check_reviews.pop(asin)

            for asin in have_reviews_asins:
                if have_reviews_asins[asin]['has_reviews']:
                    amazon_group = spider._amazon_check_reviews[asin].get('amazon_group', None)
                    parent_asin = have_reviews_asins[asin].get('parent_asin', None)
                    if parent_asin and not amazon_group:
                        amazon_group = spider.product_id(spider._amazon_check_reviews[asin]['product'])
                        amazon_group['ID_kind'] = 'amazon_group_id'
                        amazon_group['ID_value'] = parent_asin
                        spider._amazon_check_reviews[asin]['amazon_group'] = amazon_group

                    return_dict[asin] =  deepcopy(spider._amazon_check_reviews[asin])
                    sales_rank = int(spider._amazon_check_reviews[asin].get(
                        'salesrank', {}).get('ID_value', None))

                    _scrape_key = spider._amazon_check_reviews[asin].get('amazon_group', {}).get('ID_value', None)
                    if not _scrape_key:
                        _scrape_key = asin

                    spider._review_scrape[_scrape_key] = {'sales_rank': sales_rank,
                                                          'asin': _scrape_key}

                spider._amazon_check_reviews.pop(asin)
            amazon_collection['collection'] = return_dict
            return amazon_collection

    def close_spider(self, spider):
        if isinstance(spider, AmazonCSV):
            spider.publish_reviews()