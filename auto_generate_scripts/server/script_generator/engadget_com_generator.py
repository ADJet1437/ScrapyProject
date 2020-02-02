# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Engadget_comSpider", spider_type = "AlaSpider", allowed_domains = "'engadget.com'", start_urls = "'https://www.engadget.com/reviews/latest/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='container']//div[@class='table']//a[div[contains(text(),'Older')]]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='th-title']//a/@href | //a[contains (@class,'o-hit') and contains(@class,'link')]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//meta[@name='post_id']/@content", pname_xpath = "//meta[@property='og:title']/@content", ocn_xpath = "//div[@class='th-meta']/a[@class='th-topic']//text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "//div[contains(@class,'flush-top') and contains(@class,'flush-bottom')]//div[@class='grid@tl+']//a[@class='th-topic']/text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//meta[@name='post_id']/@content", pname_xpath = "//meta[@property='og:title']/@content", rating_xpath = "//div[contains(@class,'flush-top') and contains(@class,'flush-bottom')]/descendant::div[contains (.,'Engadget Score')][1]//h4[contains (.,'Engadget Score')]/following-sibling::div[1]//div[contains (@class,'t-rating')]/text()", date_xpath = "//div[starts-with(@class,'t-meta-small')]/div[@class='th-meta']/text()[1]", pros_xpath = "//div[contains(@class,'flush-top') and contains(@class,'flush-bottom')]/descendant::div[contains (.,'Engadget Score')][1]//h5[contains (.,'Pros')]/following-sibling::ul[1]/li/text()", cons_xpath = "//div[contains(@class,'flush-top') and contains(@class,'flush-bottom')]/descendant::div[contains (.,'Engadget Score')][1]//h5[contains (.,'Cons')]/following-sibling::ul[1]/li/text()", summary_xpath = "(//meta[@property='og:description']/@content | //*[contains(.,'Summary')]/following-sibling::p[text()]/text())[last()]", verdict_xpath = "//h3[contains (.,'Wrap-up') or contains (.,'Wrapup')]/following::p[2]//text()", author_xpath = "", title_xpath = "//div[starts-with(@class,'grid') and contains(@class,'flex')]//article[@class='c-gray-1']//h1/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "100", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = ['in'], format_string = "%m.%d.%y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/engadget_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

