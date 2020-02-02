# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Avforums_enSpider", spider_type = "AlaSpider", allowed_domains = "'avforums.com'", start_urls = "'https://www.avforums.com/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.click_continuous(target_xpath = "//li[@class='navigation']//a[*[contains(text(),'More')]]", wait_for_xpath = "", wait_type = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='jscroll-inner']//a[img]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//span[last()-1]/a/span[@itemprop='title']/text()", category_path_xpath = "//div[@class='breadBoxTop']//fieldset//span[@class='crust']/a/span/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1/text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(.*)Review", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1/text()", rating_xpath = "//span[@class='score']/text()", date_xpath = "//span/span[@class='DateTime']/text() | //span[@class='reviewDate']/*/@data-datestring", pros_xpath = "//p[contains(text(),'Pros') or contains(text(),'Good')]/following-sibling::ul[1]/li/span/text()", cons_xpath = "//p[contains(text(),'Cons') or contains(text(),'Bad')]/following-sibling::ul[1]/li/span/text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "//div[h2[contains(text(),'Conclusion')]]//div[contains(@class,'blockLayer')]/text() | //div[h2[contains(text(),'Verdict')]]//div[contains(@class,'blockLayer')]//text()", author_xpath = "//span[@class='reviewer']/text()", title_xpath = "//h1/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%b %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/avforums_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

