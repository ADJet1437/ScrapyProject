# -*- coding: utf8 -*-

from datetime import datetime
from scrapy.http import Request
from alascrapy.spiders.base_spiders.ala_spider import AlaSpider
import alascrapy.lib.dao.incremental_scraping as incremental_utils
from alascrapy.items import ProductItem, ReviewItem


class Aselabs_comSpider(AlaSpider):
    name = 'aselabs_com'
    allowed_domains = ['aselabs.com']

    start_urls = ['http://aselabs.com/articles.php']

    def __init__(self, *args, **kwargs):
        super(Aselabs_comSpider, self).__init__(self, *args, **kwargs)
        self.stored_last_date = incremental_utils.get_latest_pro_review_date(
            self.mysql_manager, self.spider_conf["source_id"])

        # In order to test another stored_last_date
        # self.stored_last_date = datetime(2000, 2, 8)

    def parse(self, response):
        # print "     ...PARSE: " + response.url
        # print " --self.stored_last_date: " + str(self.stored_last_date)

        post_divs_xpath = '//div[@id="articleblock"]/div[contains'\
                          '(@class, "row")]'
        post_divs = response.xpath(post_divs_xpath)

        date = None
        for p_div in post_divs:
            post_type_xpath = './div[@class="info"]/a[2]//text()'
            post_type = p_div.xpath(post_type_xpath).get()

            if post_type == 'Reviews':
                date_xpath = './/span[@class="date"]//text()'
                date = p_div.xpath(date_xpath).get()
                # date looks like this: March 10, 2016
                date = datetime.strptime(date, '%B %d, %Y')

                if date > self.stored_last_date:
                    review_url_xpath = './a[@class="image"]/@href'
                    review_url = p_div.xpath(review_url_xpath).get()

                    yield response.follow(url=review_url,
                                          callback=self.parse_product_review,
                                          meta={'date': date.strftime('%Y-%m-'
                                                                      '%d')})

        # Checking next page
        if date and (date > self.stored_last_date):
            next_page_url_xpath = '//span[@class="curpage"]/following-'\
                                  'sibling::a[1]/@href'
            next_page_url = response.xpath(next_page_url_xpath).get()
            if next_page_url:
                yield response.follow(url=next_page_url,
                                      callback=self.parse)

    def get_product_name_based_on_title(self, title):
        ''' This function will 'clean' the title of the review
            in order to get the product name '''
        p_name = title

        # Removing certain words
        words_to_remove = ['Gaming Headset',
                           'Beginner Drones',
                           'Over-Ear Headset']

        for w in words_to_remove:
            if w in title:
                p_name = p_name.replace(w, '')

        # Removing unnecessary spaces:
        p_name = p_name.replace('  ', ' ')
        p_name = p_name.strip()

        return p_name

    def parse_product_review(self, response):
        # print "     ...PARSE_PRODUCT_REVIEW: " + response.url

        # Checking the category
        cats_xpath = '//div[@class="tags"]/a//text()'
        cats = response.xpath(cats_xpath).getall()

        cats_to_scrape_dic = {'Drone': ['Drone', 'Drones'],
                              'Headphone': ['Headset', 'Headphones',
                                            'Earbuds'],
                              'Smartphone': ['Smartphone'],
                              'Camera': ['Camera']}

        review_cat = None
        found_cat = False
        for cat in cats_to_scrape_dic:
            if not found_cat:
                for c_name in cats_to_scrape_dic[cat]:
                    if c_name in cats:
                        review_cat = cat
                        found_cat = True
                        break

        if review_cat and (review_cat in cats_to_scrape_dic.keys()):

            # REVIEW ITEM ------------------------------------------------
            review_xpaths = {
                'TestTitle': '//div[@id="Partview"]/h1[1]//span//text()',
                'Author': '//div[@id="information"]/dl[1]/dd/a//text()',
            }

            # Create the review
            review = self.init_item_by_xpaths(response, "review",
                                              review_xpaths)

            # 'ProductName'
            p_name = self.get_product_name_based_on_title(review['TestTitle'])
            review['ProductName'] = p_name

            # 'TestSummary'
            summary_xpath = '//div[@id="summary"]//div//text()'
            summary = response.xpath(summary_xpath).get()
            if summary:
                summary = " ".join(summary.split())
                review['TestSummary'] = summary

            # 'TestVerdict'
            verdict_xpath = '//div[@id="text"]//a[text()="Final Verdict"]/'\
                            'following-sibling::text()'
            try:
                verdict = response.xpath(verdict_xpath).getall()
            except:
                pass
            else:
                if u'\nASE Publishing would like to thank ' in verdict:
                    verdict.remove(u'\nASE Publishing would like to thank ')

                if u' for making this review possible.' in verdict:
                    verdict.remove(u' for making this review possible.')

                verdict = " ".join(verdict)
                verdict = " ".join(verdict.split())

                if 'The retails' in verdict:
                    verdict = verdict.replace('The retails',
                                              'The {} retails'.format(
                                               review['ProductName']))

                if '( )' in verdict:
                    verdict = verdict.replace('( )', '')

                review['TestVerdict'] = verdict

            # 'TestDateText'
            review['TestDateText'] = response.meta.get('date')

            # 'DBaseCategoryName'
            review['DBaseCategoryName'] = 'PRO'

            # 'source_internal_id'
            sid_xpath = '//input[@name="redirextra"]/@value'
            # value="id|~|61753"
            sid = response.xpath(sid_xpath).get()
            sid = sid.split('id|~|')[-1]
            review['source_internal_id'] = sid
            # ------------------------------------------------------------

            # PRODUCT ITEM ------------------------------------------------
            product = ProductItem()
            product['source_internal_id'] = review['source_internal_id']
            product['OriginalCategoryName'] = review_cat
            product['ProductName'] = review['ProductName']

            pic_url_xpath = '//div[@id="summary"]/img/@src'
            pic_url = response.xpath(pic_url_xpath).get()
            if pic_url:
                product['PicURL'] = pic_url

            product['TestUrl'] = response.url

            info_blocks_xpath = '//div[@id="information"]/dl'
            info_blocks = response.xpath(info_blocks_xpath)
            for i_block in info_blocks:
                if i_block.xpath('./dt//text()').get() == 'Manufacturer':
                    manuf_xpath = '/dd//text()'
                    manuf = response.xpath(manuf_xpath).get()
                    if manuf:
                        product['ProductManufacturer'] = manuf
            # ------------------------------------------------------------

            yield review
            yield product
