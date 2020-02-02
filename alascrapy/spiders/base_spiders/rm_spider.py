from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
from alascrapy.items import ProductIdItem

class RMSpider(AlaSpider):

    def get_rm_urls(self):
        query = """
                SELECT rm.product_id, rm.url
                FROM review.rm_urls rm
                WHERE rm.review_source_id=%s"""

        urls = self.mysql_manager.execute_select(query, self.spider_conf['source_id'])
        return {url['url'].lower(): url['product_id'] for url in urls}

    def __init__(self, *a, **kw):
        super(RMSpider, self).__init__(*a, **kw)
        self.rm_urls = self.get_rm_urls()
        self.start_urls = [url for url in self.rm_urls]

    def get_rm_kidval(self, product, initial_response):
        rm_kidval = ProductIdItem()
        if "source_internal_id" in product:
            rm_kidval['source_internal_id'] = product["source_internal_id"]
        rm_kidval['ProductName'] = product["ProductName"]
        rm_kidval['ID_kind'] = "review_monitor_id"

        redirect_urls=initial_response.meta.get('redirect_urls', [])
        if redirect_urls:
            original_url = redirect_urls[0].lower()
        else:
            original_url=initial_response.url.lower()

        try:
            rm_kidval['ID_value'] = self.rm_urls[original_url]
        except:
            pass
        return rm_kidval
