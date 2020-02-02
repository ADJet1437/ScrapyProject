import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Vmall_nlSpider", spider_type = "AlaSpider", allowed_domains = "'vmall.eu'", start_urls = "'https://www.vmall.eu/nl/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//a[@class='nav__primary-link']/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//a[@class='listing__item-link']/@href", level_index = "3", url_regex = "", include_original_url = "", params_xpath = {'OriginalCategoryName':'//h1[@class="title-h1"]/text()'}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//div[@class='product__head']/@data-initial-sku", pname_xpath = "//div[@class='product__core']//span[@class='js-product-title']/text()", ocn_xpath = "", pic_xpath = "//div[@class='product__gallery']//li[contains(@class, 'product__gallery-item')][1]/a/@href", manuf_xpath = "HUAWEI")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = "", id_kind = "sku")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.click(target_xpath = "//li[@data-tab='reviews']", wait_for_xpath = "", wait_type = "")
code_fragments.append(return_code)

return_code = spa.gen_containers_review(containers_xpath = "//ul[contains(@class, 'product__review')]", button_next_javascript = "no", button_next_xpath = "", sii_xpath = "//div[@class='product__head']/@data-initial-sku", pname_xpath = "//div[@class='product__core']//span[@class='js-product-title']/text()", rating_xpath = ".//div[contains(@class, 'review-avg-stars')]/@class", date_xpath = ".//span[contains(@class, 'review-published')]/text()", pros_xpath = "", cons_xpath = "", summary_xpath = ".//li[contains(@class, 'review-body')]//text()", verdict_xpath = "", author_xpath = ".//span[contains(@class, 'review-author')]/text()", title_xpath = ".//li[contains(@class, 'review-title')]/text()", award_xpath = "", awpic_xpath = "")

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "user")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "100", review_type = "user")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = ".+--pc(.+)", review_type = "user")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d-%m-%Y", languages = "en", review_type = "user")

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "%s")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/vmall_nl.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

