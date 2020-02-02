__author__ = 'graeme'

from alascrapy.items import AmazonCollection, ProductItem, ProductIdItem, ReviewItem

class AlascrapyPipeline(object):
    def process_item(self, item, spider):
        if item is None:
            return

        if isinstance(item, AmazonCollection):
            for asin in item['collection']:
                for item_name in item['collection'][asin]:
                    item['collection'][asin][item_name] = \
                        self._process_item(item['collection'][asin][item_name],
                                               spider)
            return item
        else:
            return self._process_item(item, spider)

    def _process_item(self, item, spider):
        raise NotImplementedError("Not implemented _process_item function")
