# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Arstechnica_comSpider", spider_type = "AlaSpider", allowed_domains = "'arstechnica.com'", start_urls = "'http://arstechnica.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='prev-next-links']/a[1]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div/article/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//body/@class", pname_xpath = "//meta[@property='og:title']/@content", ocn_xpath = "arstechnica", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//body/@class", pname_xpath = "//meta[@property='og:title']/@content", rating_xpath = "", date_xpath = "//time[@class='date']/@datetime", pros_xpath = "", cons_xpath = "", summary_xpath = "//h2[@itemprop='description']/text()", verdict_xpath = "", author_xpath = "//a[@rel='author']//text()", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=postid-)\d*(?=\s))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=postid-)\d*(?=\s))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d[^\s]*(?=T))", review_type = "")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//nav/span/a[last()-1]/@href", test_verdict_xpaths = ['//div[@itemprop="articleBody"]/h2[not(./following-sibling::h2) and not(./following-sibling::*[.//img])]/following-sibling::p[1]//text()'], pros_xpath = "//h3[contains(.,'Good')]/following-sibling::ul[1]/li/text()", cons_xpath = "//h3[contains(.,'Bad')]/following-sibling::ul[1]/li/text()", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/arstechnica_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

