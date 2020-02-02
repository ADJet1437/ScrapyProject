import alascrapy.lib.dao.categories as category_utils
from alascrapy.pipelines import AlascrapyPipeline

from datetime import datetime

from os.path import join
from os import system, rename


class CategoriesPipeline(AlascrapyPipeline):
    """
    Categories Pipeline.
    Loads the categories for each source to help decide if it should be scraped or not.
    """

    def _set_missing_values(self, item):
        if 'category_path' not in item:
            item['category_path'] = ''

        if 'category_url' not in item:
            item['category_url'] = ''

        if 'category_leaf' not in item:
            item['category_leaf'] = ''

        if 'category_string' not in item:
            item['category_string'] = ''

        if 'do_not_load' not in item:
            item['do_not_load'] = False
        return item

    def open_spider(self, spider):
        spider_conf = spider.spider_conf

        source_id = spider_conf['source_id']
        spider._categories = category_utils.load_current_categories(spider.mysql_manager, source_id)


    def _process_item(self, item, spider):
        project_conf = spider.project_conf
        spider_conf = spider.spider_conf
        add_new_categories = project_conf.getboolean("OUTPUT", 'add_new_categories')
        if item._name != "category":
            return item

        item = self._set_missing_values(item)
        if item['category_path'].lower() not in spider._categories:
            if add_new_categories:
                #TODO: Create a function to determine
                #      if the source is opt_in or opt_out
                is_optin = spider_conf.get('is_optin', False)
                if is_optin:
                    item['do_not_load'] = True

                category_utils.insert_new_category(spider.mysql_manager,
                                                   item)

                spider._categories[item['category_path'].lower()] = {
                    'Category_Leaf': item['category_leaf'],
                    'do_not_load': item['do_not_load'],
                    'Category_Url': item['category_url'],
                    'Category_Path': item['category_path']}
        return item
