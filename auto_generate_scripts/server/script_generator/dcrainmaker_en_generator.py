# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Dcrainmaker_enSpider", spider_type = "AlaSpider", allowed_domains = "'dcrainmaker.com'", start_urls = "'https://www.dcrainmaker.com/product-reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h2[@class='entry-title']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='entry-meta']/a[contains(@href, 'product-reviews')][last()]/text()", category_path_xpath = "//div[@class='entry-meta']/a[contains(@href, 'product-reviews')]/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1/text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image'][1]/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1/text()", rating_xpath = "", date_xpath = "//span[@class='entry-date']/text()", pros_xpath = "//p[@id='pros']/following-sibling::p[1]/text()", cons_xpath = "//p[@id='cons']/following-sibling::p[1]/text()", summary_xpath = "//h3[@id='summary']/following-sibling::p[2]/text()[1] | //div[@class='entry-content']/p[text()][1]/text()", verdict_xpath = "", author_xpath = "//a[@rel='author']/text()", title_xpath = "//h1/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%b %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/dcrainmaker_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

