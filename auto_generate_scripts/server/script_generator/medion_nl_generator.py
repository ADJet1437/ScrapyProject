import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Medion_nlSpider", spider_type = "AlaSpider", allowed_domains = "'medion.com', 'ekomi.de'", start_urls = "'http://www.medion.com/nl/shop/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[contains(@class, 'navigation-main-sub-level')]//a[contains(@class, 'navigation-main-item')]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[contains(@class, 'productTitleLinkTE')]/h2/a/@href", level_index = "3", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[contains(@class, 'pagination-bottom')]//li[last()]/a/@href", level_index = "2", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@id='ariadne']//li[@class='active'][last()]/a/text()", category_path_xpath = "//div[@id='ariadne']//li[@class='active']/a/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//span[contains(@class, 'article-number')]/text()", pname_xpath = "//div[@id='ariadne']//li[last()]/text()", ocn_xpath = "", pic_xpath = "//img[@itemprop='image']/@src", manuf_xpath = "MEDION")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "Art.Nr.[\s\S]* (\d+)", review_type = "user")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//iframe[@id='ekomi_Frame']/@src", level_index = "4", url_regex = "", product_fields = ['ProductName', 'source_internal_id'])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "4", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_containers_review(containers_xpath = "//div[@class='feedback']", button_next_javascript = "no", button_next_xpath = "//div[@id='pager']//a[contains(text(), 'weiter')]/@href", sii_xpath = "", pname_xpath = "", rating_xpath = ".//div[@class='rating_user_inner']/@style", date_xpath = ".//div[contains(@class, 'rating_user_date')]/text()", pros_xpath = "", cons_xpath = "", summary_xpath = ".//div[@class='rating_user_text']//text()", verdict_xpath = "", author_xpath = "", title_xpath = "", award_xpath = "", awpic_xpath = "")

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "user")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "100", review_type = "user")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d.%m.%Y om %H:%M", languages = "nl", review_type = "user")

code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "width:(.+)px", review_type = "user")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "user")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/medion_nl.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

