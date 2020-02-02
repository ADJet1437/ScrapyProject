# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Techenet_comSpider", spider_type = "AlaSpider", allowed_domains = "'techenet.com'", start_urls = "'http://www.techenet.com/category/analise/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='page-nav']/*[contains(@class,'current')]/following-sibling::a[1]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//article//h1/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//ul[@class='breadcrumb']/li[contains(@*,'crumb')][last()]//text()", category_path_xpath = "//ul[@class='breadcrumb']/li[contains(@*,'crumb')]//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "substring-after(//link[@rel='shortlink']/@href,'p=')", pname_xpath = "//h1[contains(@class,'entry-title')]//text()", ocn_xpath = "//ul[@class='breadcrumb']/li[contains(@*,'crumb')]//text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "substring-after(//link[@rel='shortlink']/@href,'p=')", pname_xpath = "//h1[contains(@class,'entry-title')]//text()", rating_xpath = "//span[@itemprop='reviewRating']//span[@itemprop='ratingValue']//text()", date_xpath = "substring-before(//time[@class='entry-date']/@datetime,'T')", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[@class='entry-content']/p[not(./preceding-sibling::*[not(name()='p')]/preceding-sibling::p[string-length(normalize-space(./text()))>1])][string-length(normalize-space(./text()))>1][last()]//text()", verdict_xpath = "//div[@class='rw-summary']/*[name()='p' or name()='h4']//text()", author_xpath = "//span[contains(@class,'author')]//a//text()", title_xpath = "//h1[contains(@class,'entry-title')]//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/techenet_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

