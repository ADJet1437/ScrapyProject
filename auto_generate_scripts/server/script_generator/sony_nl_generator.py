import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Sony_nlSpider", spider_type = "AlaSpider", allowed_domains = "'sony.nl'", start_urls = "'http://www.sony.nl/all-electronics'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//li[@class='products-li']/a/@href", level_index = "2", url_regex = ".+/electronics/.+", include_original_url = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//button[@class='tab']/@data-tab-url", level_index = "3", url_regex = "", include_original_url = "yes")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[contains(@class, 'products')]/a/@href", level_index = "4", url_regex = "", include_original_url = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "4", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[@itemprop='name']/text()", ocn_xpath = "//meta[contains(@name, 'category1')]/@content", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "//meta[@property='og:site_name']/@content")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = "//span[@itemprop='model']/text()", id_kind = "sku")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//span[contains(@class, 'reviews-text')]/a[@class='primary-link ']/@href", level_index = "5", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "5", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_containers_review(containers_xpath = ".//div[@itemprop='review']", button_next_javascript = "yes", button_next_xpath = "//button[contains(@class, 'loadmore')]", sii_xpath = "", pname_xpath = "//a[contains(@class, 'breadcrumb-link')]/@title", rating_xpath = ".//meta[@itemprop='ratingValue']/@content", date_xpath = ".//span[contains(@class, 'review-date')]//text()", pros_xpath = "", cons_xpath = "", summary_xpath = ".//p[@itemprop='description']/text()", verdict_xpath = "", author_xpath = ".//span[contains(@class, 'user-nickname')]/text()", title_xpath = ".//h4[@itemprop='name']/text()", award_xpath = "", awpic_xpath = "")

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "user")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "user")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d-%m-%Y", languages = "en", review_type = "user")

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "user")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/sony_nl.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

