# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Computershopper_enSpider", spider_type = "AlaSpider", allowed_domains = "'computershopper.com'", start_urls = "'http://www.computershopper.com/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='boxed-content']/ul/li/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//p[@class='breadcrumb']/a[last()-1]/text()", category_path_xpath = "//p[@class='breadcrumb']/a/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//meta[@property='og:title']/@content", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(.*) Review - ComputerShopper.com", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//meta[@property='og:title']/@content", rating_xpath = "//span[@itemprop='ratingValue']/text()", date_xpath = "//span[@class='dtreviewed']/text()", pros_xpath = "//dt[contains(text(),'Liked')]/following-sibling::dd[1]//li/text()", cons_xpath = "//dt[contains(text(),'Didn')]/following-sibling::dd[1]//li/text()", summary_xpath = "(//div[@class='overview']/p[span[contains(text(),'Verdict')]]/text() | //div[@itemprop='reviewBody']/p[text()][1]/text())[1]", verdict_xpath = "", author_xpath = "//a[@rel='author']/text()", title_xpath = "//h1[@itemprop='headline']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[@id='review-body']//ul[@class='nav-collapse']//a[contains(text(),'Conclusion')]/@href", test_verdict_xpaths = ['//h4[contains(./descendant-or-self::*,"Conclusion")][last()]/following-sibling::p[1]//text()' ], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/computershopper_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

