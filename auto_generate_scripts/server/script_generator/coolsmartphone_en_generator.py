# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Coolsmartphone_enSpider", spider_type = "AlaSpider", allowed_domains = "'coolsmartphone.com'", start_urls = "'http://www.coolsmartphone.com/category/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.click_continuous(target_xpath = "//div[@id='load-posts']/a[contains(text(),'Load More')]", wait_for_xpath = "", wait_type = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@id='content_box']//a[div[img]]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@itemprop='breadcrumb']/a[2]/text()", category_path_xpath = "//div[@itemprop='breadcrumb']/a/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//meta[@property='og:title'][2]/@content", ocn_xpath = "", pic_xpath = "//meta[@property='og:image'][1]/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//meta[@property='og:title'][2]/@content", rating_xpath = "//span[@itemprop='reviewRating']/text()", date_xpath = "//meta[@property='article:published_time']/@content", pros_xpath = "", cons_xpath = "", summary_xpath = "(//div[@itemprop='description']/p/text() | //meta[@property='og:description'][1]/@content)[last()]", verdict_xpath = "//p[contains(.,'Overall') or contains(.,'Final Thoughts') or contains(.,'Conclusion')]/following-sibling::p[1]//text()| //p[contains(.,'Conclusion')]/text()", author_xpath = "//span[@class='theauthor']//a/text()", title_xpath = "//meta[@property='og:title'][2]/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "100", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%Y-%m-%dT%H:%M:%S%z", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/coolsmartphone_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

