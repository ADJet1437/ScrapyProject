# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Thehdroom_enSpider", spider_type = "AlaSpider", allowed_domains = "'thehdroom.com'", start_urls = "'http://www.thehdroom.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='widget-home-wrapper']//a[img]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='nav-links']//a[contains(text(),'Next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//meta[@property='article:section']/@content", category_path_xpath = "//meta[@property='article:section']/@content")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[@itemprop='itemreviewed']/text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image'][1]/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "OriginalCategoryName", regex = "(.*) Reviews", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1[@itemprop='itemreviewed']/text()", rating_xpath = "//span[@itemprop='rating']/text()", date_xpath = "//time[@itemprop='dtreviewed']/@datetime", pros_xpath = "", cons_xpath = "", summary_xpath = "//meta[@property='og:description'][last()]/@content", verdict_xpath = "//meta[@property='og:description'][1]/@content", author_xpath = "//a[@rel='author']/text()", title_xpath = "//h1[@itemprop='itemreviewed']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/thehdroom_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

