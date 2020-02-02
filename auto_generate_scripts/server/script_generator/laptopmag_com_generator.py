# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Laptopmag_comSpider", spider_type = "AlaSpider", allowed_domains = "'laptopmag.com'", start_urls = "'http://www.laptopmag.com/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[@rel='next']/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[starts-with(@class,'h1')]/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//meta[@property='og:title'][not(contains(//meta[@property='og:url']/@content,'tomsguide'))]/@content", ocn_xpath = "//meta[@property='og:url']/@content", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//meta[@property='og:title'][not(contains(//meta[@property='og:url']/@content,'tomsguide'))]/@content", rating_xpath = "//div[@itemprop='itemReviewed']/following::meta[@itemprop='ratingValue'][1]/@content", date_xpath = "//time/@datetime", pros_xpath = "//div[@itemprop='itemReviewed']/following::*[translate(translate(.,'/',''),' ','')='Pros' or translate(translate(.,'/',''),' ','')='ThePros'][1]/following::p[1]//text()", cons_xpath = "//div[@itemprop='itemReviewed']/following::*[translate(translate(.,'/',''),' ','')='Cons' or translate(translate(.,'/',''),' ','')='TheCons'][1]/following::p[1]//text()", summary_xpath = "//*[(name()='div' and starts-with(@class,'tabContent')) or (name()='section' and @class='otm-content')]/descendant::p[string-length(normalize-space())>1][1]//text()", verdict_xpath = "//div[@itemprop='itemReviewed']/following::*[translate(translate(.,'/',''),' ','')='Verdict'][1]/following::p[1]//text()", author_xpath = "//span[@itemprop='author']/text()", title_xpath = "//meta[@property='og:title'][not(contains(//meta[@property='og:url']/@content,'tomsguide'))]/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = "//meta[contains(@content,'Price')]/following-sibling::meta[1]/@content", id_kind = "price")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "OriginalCategoryName", regex = "((?<=\/reviews\/)\w*-*\w*(?=\/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%b %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/laptopmag_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

