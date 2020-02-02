# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Brighthand_enSpider", spider_type = "AlaSpider", allowed_domains = "'brighthand.com'", start_urls = "'http://www.brighthand.com/review/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//section[@class='contentListContainer']//a[img]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//section/following-sibling::div[contains(@class,'bottomPagination')][1]//a[@rel='next']/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='breadcrumbs']/a[last()]/text()", category_path_xpath = "//div[@class='breadcrumbs']/a/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//meta[@property='og:title']/@content", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//meta[@property='og:title']/@content", rating_xpath = "//li[contains(text(),'Total')]/following-sibling::li[@class='ratingValue']/text()", date_xpath = "//time[@class='publishDate']/@datetime", pros_xpath = "//p[contains(.,'Pro')]/following-sibling::*[1]//li//text() | //section[@class='allowBullets']/*[contains(.,'Pros')]/following-sibling::*[1]//li//text()", cons_xpath = "//p[contains(.,'Cons')]/following-sibling::*[1]//li//text() | //section[@class='allowBullets']/*[contains(.,'Cons')]/following-sibling::*[1]//li//text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "", author_xpath = "//span[@itemprop='name']/a/text() | //span[@itemprop='name']/text()", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//ul[@class='chapters-bar-list']//a[contains(text(),'Conclusion')]/@href", test_verdict_xpaths = ['//*[contains(.,"Conclusion") or contains(.,"CONCLUSION")]/following-sibling::p[text()][1]/text()','//*[*[contains(text(),"Conclusion")]]/text()'], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/brighthand_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

