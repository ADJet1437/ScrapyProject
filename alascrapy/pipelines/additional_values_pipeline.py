from alascrapy.pipelines import AlascrapyPipeline

class AdditionalValuesPipeline(AlascrapyPipeline):
    """ AdditionalValues:
        This pipeline sets foreach item the additional values defined
        in conf/sources_conf/<<source_name.json>>
    """
    def add_source_id(self, item, spider):
        spider_conf = spider.spider_conf
        if item._name in ('review', 'category', 'product', 'product_id'):
            item["source_id"] = spider_conf['source_id']

    def add_test_scale(self, item, spider):
        if item._name != "review":
            return
        spider_conf = spider.spider_conf
        additional_values = spider_conf['additional_values']
        if item["DBaseCategoryName"] == "USER" \
           and 'user_test_scale' in additional_values['review']:
                item['SourceTestScale'] = \
                    additional_values['review']['user_test_scale']
        elif item["DBaseCategoryName"] == "PRO" \
             and 'pro_test_scale' in additional_values['review']:
                item['SourceTestScale'] = \
                    additional_values['review']['pro_test_scale']

    def _process_item(self, item, spider):
        spider_conf = spider.spider_conf
        # not to rewrite source_id for item, so we can add items for more,
        # than 1 source
        if not item.get('source_id', None):
            self.add_source_id(item, spider)

        if 'additional_values' not in spider_conf:
            return item

        if item._name not in spider_conf['additional_values']:
            return item

        if item._name == "review":
            self.add_test_scale(item, spider)

        for field in spider_conf['additional_values'][item._name]:
            if field in ['user_test_scale', 'pro_test_scale']:
                continue
            item[field] = spider_conf['additional_values'][item._name][field]

        return item
