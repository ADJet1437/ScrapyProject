# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Videogamer_enSpider", spider_type = "AlaSpider", allowed_domains = "'videogamer.com'", start_urls = "'http://www.videogamer.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='details']//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//li[@class='next numPaginNext']/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h5[@itemprop='name']/a/text()", ocn_xpath = "game", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "//tr[td[contains(text(),'Publisher')]]/td[last()]/text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h5[@itemprop='name']/a/text()", rating_xpath = "//div[@itemprop='ratingValue']/text()", date_xpath = "//header//time[@class='publishDate']/@datetime", pros_xpath = "//div[@class='reviewSummaryBox clrfix']/ul/li[not(@class='bad')]/text()", cons_xpath = "//ul/li[@class='bad']/text()", summary_xpath = "//h2[@itemprop='description']/text()", verdict_xpath = "//div[@itemprop='reviewBody']/p[last()-1]/text() | //div[@itemprop='reviewBody']/p[last()-2]/text()", author_xpath = "//a[@rel='author']/text()", title_xpath = "//h1[@itemprop='name']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/videogamer_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

