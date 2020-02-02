import sys
sys.path.append(".")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "BhphotovideoSpider", spider_type = "AlaSpider", allowed_domains = "'bhphotovideo.com'", start_urls = "'http://www.bhphotovideo.com/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//section[@class='main-nav']//li[contains(@id, 'cat')]/a/@href", level_index = "2", url_regex = "http://.+/N/\d+")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//li[@class='clp-category']/a/@href", level_index = "3", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[contains(@class, 'bottom')]//a[@data-selenium='pn-next']/@href", level_index = "3", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@data-selenium='itemInfo-zone']//a[@data-selenium='itemHeadingLink']/@href", level_index = "4", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "4")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//ul[@id='breadcrumbs']//li[last()]//a/text()", category_path_xpath = "//ul[@id='breadcrumbs']//a/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//div[@class='pProductNameContainer']//meta[@itemprop='productID'][1]/@content", pname_xpath = "//span[@itemprop='name']/text()", ocn_xpath = "//ul[@id='breadcrumbs']//text()", pic_xpath = "//img[@id='mainImage']/@src", manuf_xpath = "//div[@class='pProductNameContainer']//span[@itemprop='brand']/text()")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "sku:(.+)", review_type = "user")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = "", id_kind = "sku")
code_fragments.append(return_code)

return_code = spa.click(target_xpath = "//li[@id='navCustomerReviews']/a", wait_for_xpath = "//div[@class='pr-review-wrap']", wait_type = "presence_of_all_elements_located")
code_fragments.append(return_code)

return_code = spa.gen_containers_review(containers_xpath = "//div[@class='pr-review-wrap']", button_next_javascript = "yes", button_next_xpath = "//div[@class='pr-pagination-bottom']//span[@class='pr-page-next']/a", sii_xpath = "//div[@class='pProductNameContainer']//meta[@itemprop='productID'][1]/@content", pname_xpath = "//span[@itemprop='name']/text()", rating_xpath = ".//div[contains(@class, 'pr-stars')]/@class", date_xpath = ".//div[contains(@class, 'pr-review-author-date')]/text()", pros_xpath = "", cons_xpath = "", summary_xpath = ".//p[@class='pr-comments']/text()", verdict_xpath = "", author_xpath = ".//p[@class='pr-review-author-name']/span/text()", title_xpath = ".//p[@class='pr-review-rating-headline']//text()", award_xpath = "", awpic_xpath = "")

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "user")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "user")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "", languages = "", review_type = "user")

code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = ".+-stars-(\d)-.+", review_type = "user")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "sku:(.+)", review_type = "user")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "user")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/bhphotovideo.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

