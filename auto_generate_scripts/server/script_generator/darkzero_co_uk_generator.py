# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Darkzero_co_ukSpider", spider_type = "AlaSpider", allowed_domains = "'darkzero.co.uk'", start_urls = "'http://darkzero.co.uk/game-reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='header']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//ul[@class='pager']/li[@class='next']/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[@class='title']/text()", ocn_xpath = "//p[starts-with(text(),'Genre:')]/span//text()", pic_xpath = "//div[@class='header']/img/@src", manuf_xpath = "//p[starts-with(text(),'Publisher:')]/span//text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1[@class='title']/text()", rating_xpath = "//img[contains(@src,'scores')]/@src", date_xpath = "//time[@datetime]//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[@itemprop='reviewBody']/p[string-length(.//text())>2][1]//text()", verdict_xpath = "//div[@itemprop='reviewBody']/p[string-length(.//text())>2][last()]//text()", author_xpath = "//a[@rel='author']//text()", title_xpath = "//h1[@class='title']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "((?<=scores/).*(?=.png))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/darkzero_co_uk.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

