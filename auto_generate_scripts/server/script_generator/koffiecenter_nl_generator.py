# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Koffiecenter_nlSpider", spider_type = "AlaSpider", allowed_domains = "'koffiecenter.nl'", start_urls = "'http://www.koffiecenter.nl/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//li[position()>1 and position()<last()]//a[contains(@class,'nav-action')]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//li[contains(@class,'product-list')]//h2/a/@href", level_index = "3", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='paging-footer']//div[@class='paging-navigation']/a[contains(@class,'next')]/@href", level_index = "2", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[contains(@class,'title-links')]//span[contains(@class,'reviews')]/a/@href", level_index = "4", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "4", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//ol[@class='breadcrumbs']//ol/li[last()]//a//span//text()", category_path_xpath = "//ol[@class='breadcrumbs']//span//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//div[@class='overviewHeaderTitle']//h1/a/@href", pname_xpath = "//div[@class='overviewHeaderTitle']//h1/a//text()", ocn_xpath = "//ol[@class='breadcrumbs']//span//text()", pic_xpath = "//div[@class='headerContent']//img/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=/)\d+(?=/))", review_type = "user")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.gen_containers_review(containers_xpath = "//ul[@class='reviewList']/li[@class='review']", button_next_javascript = "no", button_next_xpath = "//div[contains(@class,'paging-footer')]//a[contains(@class,'next')]/@href", sii_xpath = "//div[@class='overviewHeaderTitle']//h1/a/@href", pname_xpath = "//div[@class='overviewHeaderTitle']//h1/a//text()", rating_xpath = ".//div[@class='reviewAverageRating']//meter/@value", date_xpath = ".//span[@class='writeDate']//time//text()", pros_xpath = ".//div[@class='pros']//ul/li//text()", cons_xpath = ".//div[@class='cons']//ul/li//text()", summary_xpath = ".//div[contains(@class,'reviewText')]//p[count(br)=0]/text() | .//div[contains(@class,'reviewText')]//br[position()=1]/preceding-sibling::text()[1]", verdict_xpath = "", author_xpath = ".//div[@class='reviewWriter']/strong//text()", title_xpath = ".//div[@class='reviewContent']/h3/a//text()", award_xpath = "", awpic_xpath = "")

code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=/)\d+(?=/))", review_type = "user")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "user")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d %B %Y", languages = "nl", review_type = "user")

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "user")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "user")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/koffiecenter_nl.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

