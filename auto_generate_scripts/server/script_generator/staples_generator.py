import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "StaplesSpider", spider_type = "AlaSpider", allowed_domains = "'staples.com'", start_urls = "'http://www.staples.com/office/supplies/home'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//span[@class='scTrack scNavLink']/@data-href", level_index = "2", url_regex = "/.+/cat_.+")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='cat_gallery']//a/@href", level_index = "3", url_regex = "/.+/cat_.+")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='cat_gallery']//a/@href", level_index = "4", url_regex = "/.+/cat_.+")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "4")
code_fragments.append(return_code)

return_code = spa.click_continuous(target_xpath = "//button[@id='load-more-results']", wait_for_xpath = "", wait_type = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='product-info']/a/@href", level_index = "5", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "5")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//li[@typeof='v:Breadcrumb'][last()]/a//text()", category_path_xpath = "//li[@typeof='v:Breadcrumb']/a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//span[@ng-bind='product.metadata.partnumber']/text()", pname_xpath = "//div[@class='stp--grid']//*[@ng-bind-html='product.metadata.name']/text()", ocn_xpath = "", pic_xpath = "//div[@id='STP--Product-Image']//img/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = "//span[@ng-bind='product.metadata.partnumber']/text()", id_kind = "sku")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.gen_containers_review(containers_xpath = "//div[@data-review-id]", button_next_javascript = "yes", button_next_xpath = "//span[contains(@class, 'yotpo_next')]", sii_xpath = "//span[@ng-bind='product.metadata.partnumber']/text()", pname_xpath = "//div[@class='stp--grid']//*[@ng-bind-html='product.metadata.name']/text()", rating_xpath = "count(.//span[contains(@class, 'yotpo-icon-star')])", date_xpath = ".//div[contains(@class, 'yotpo-header-element')]//label[contains(@class, 'yotpo-review-date')]/text()", pros_xpath = "", cons_xpath = "", summary_xpath = ".//div[@class='content-review']/text()", verdict_xpath = "", author_xpath = ".//div[contains(@class, 'yotpo-header-element')]//label[contains(@class, 'yotpo-user-name')]/text()", title_xpath = ".//div[contains(@class, 'content-title')]/text()", award_xpath = "", awpic_xpath = "")

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "user")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%m/%d/%y", languages = "en", review_type = "user")

code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "user")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "user")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/staples.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

