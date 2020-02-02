# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Chip_deSpider", spider_type = "AlaSpider", allowed_domains = "'chip.de'", start_urls = "'http://www.chip.de/Test_12430122.html'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[contains(@class,'next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//ol//div/a[@title]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//*[contains(@*,'crumb')]/*[contains(@itemtype,'crumb')][last()]/a/span/text()", category_path_xpath = "//*[contains(@*,'crumb')]/*[contains(@itemtype,'crumb')]/a/span/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//meta[@property='og:url']/@content", pname_xpath = "(//span[@class='fn'] | //span[contains(@class,'ProductName')]/text())[1]", ocn_xpath = "//*[contains(@*,'crumb')]/*[contains(@itemtype,'crumb')][last()]/a/span/text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//meta[@property='og:url']/@content", pname_xpath = "(//span[@class='fn'] | //span[contains(@class,'ProductName')]/text())[1]", rating_xpath = "//li[contains(@class,'rating')]/span[@class='value']/text()", date_xpath = "//meta[@name='date']/@content", pros_xpath = "//ul[contains(@class,'Pros')]/li/text()", cons_xpath = "//ul[contains(@class,'Cons')]/li/text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "//*[(contains(@class,'Chapter') or contains(@class,'description')) and descendant-or-self::*[starts-with(normalize-space(),'Fazit')]]/descendant-or-self::*[not(descendant::*[contains(@*,'Widget')]) and not(ancestor::*[contains(@*,'Widget')])]//text()", author_xpath = "//*[@itemprop='name' or @class='reviewer' or starts-with(normalize-space(),'Von')]/text()", title_xpath = "//*[starts-with(@*,'headline') or @itemprop='headline']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=_)\d.*(?=\.html))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=_)\d.*(?=\.html))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\d.*\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\w[^\s]*(?=\s\w))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "((?<=Von\s)[^\,]*(?=\,))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [])
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "100", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/chip_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

