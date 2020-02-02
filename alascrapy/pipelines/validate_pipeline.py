from scrapy.exceptions import DropItem
from alascrapy.items import CategoryItem, ProductItem, ProductIdItem, ReviewItem
from alascrapy.pipelines import AlascrapyPipeline

class ValidatePipeline(AlascrapyPipeline):
    """ValidatePipeline:
       This pipeline makes sure every item contains the necessary
       data to write the csv file. And should run right before writing
       to the csv file.

       It also logs warnings or errors if for a source we cannot
       find fields our script is set to retrive.
       The expected fields are configured
       in conf/sources_conf/<<source_name.json>>

       A warning message is logged if the missing field is configured
       as optional.An error message if it is required.  If a required field
       for a source is not found but the fields available still meet the
       minimum set for a particular object (review, product, product_id) then
       it will still be inserted in the csv to be loaded."""

    min_item_fields = {"category": ['source_id',
                                    'category_path'],
                       "product": ['source_id',
                                   'ProductName',
                                   'TestUrl'],
                       "review": ['source_id',
                                  'ProductName',
                                  'DBaseCategoryName',
                                  'TestUrl'],
                       "product_id": ['source_id',
                                      'ProductName',
                                      'ID_kind',
                                      'ID_value']
                       }

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def __init__(self, stats):
        self.stats = stats


    def validate_item(self, item, spider):
        spider_conf = spider.spider_conf

        validate_fields = spider_conf["validate_csv_fields"][item._name]

        minimum_set_error = \
            "%s item in spider %s is missing minimum required field: %s: \n %s"
        missing_required_error = \
            "%s item in spider %s is missing required field %s: \n %s"
        empty_review = \
            "Empty review in spider %s: \n %s"

        if item._name == 'review':
            # Do not validate youtube video reviews 
            # since some of them are without summary
            if item.get('source_id', '') == 10004:
                return item
            review_ok = bool(item.get('TestSummary', None) or
                             item.get('TestVerdict', None) or
                             item.get('TestPros', None) or
                             item.get('TestCons', None))
            if not review_ok:
                raise DropItem(empty_review % (spider.name, str(item)))

        for field, validate_rules in validate_fields.iteritems():
            if not item.get(field):
                if field in self.min_item_fields[item._name]:
                    raise DropItem(
                        minimum_set_error % (item._name, spider.name, field, str(item)))
                elif validate_rules["required"]:
                    spider._logger.warning(missing_required_error % (
                        item._name, spider.name, field, str(item)))

        self.add_stats(item, spider)
        return item

    def filter_skip_categories(self, item, spider):
        if item._name=="product":
            ocn = item.get("OriginalCategoryName", None)
            if ocn:
                if ocn.lower() in spider.skip_categories:
                    msg="Category: \"%s\" set to do not scrape." % ocn
                    spider._logger.info(msg)
                    raise DropItem(msg)

    def _process_item(self, item, spider):
        if item._name == "category":
            self.stats.inc_value('items/categories_scraped_count',
                                 spider=spider)
            return item

        spider_conf = spider.spider_conf
        self.filter_skip_categories(item, spider)
        if item._name not in spider_conf["validate_csv_fields"]:
            msg = "PROGRAMMING ERROR: Missing validation fields for item %s, " \
                  "in source file %s" % (item._name, spider.name)
            spider._logger.error(msg)
            raise DropItem(msg)

        if not self.min_item_fields[item._name]:
            msg = "PROGRAMMING ERROR: Unknown item class appeared! %s" % \
                  item._name
            spider._logger.error(msg)
            raise DropItem(msg)

        return self.validate_item(item, spider)

    def add_stats(self, item, spider):
        if isinstance(item, ProductItem):
            self.stats.inc_value('items/products_scraped_count', spider=spider)
        elif isinstance(item, ProductIdItem):
            self.stats.inc_value('items/product_ids_scraped_count', spider=spider)
        elif isinstance(item, ReviewItem):
            self.stats.inc_value('items/reviews_scraped_count', spider=spider)