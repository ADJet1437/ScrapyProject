# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Avhub_com_auSpider", spider_type = "AlaSpider", allowed_domains = "'avhub.com.au'", start_urls = "'http://www.avhub.com.au/product-reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='blog']//div[@class='contentintro']//a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//ul[@class='pagination']//img[@alt='next']/../@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "'avhub.com.au'", category_path_xpath = "'avhub.com.au'")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//div[@id='review-info']/strong[contains(text(),'Name')]/following::text()[1]", ocn_xpath = "", pic_xpath = "", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//div[@id='review-info']/strong[contains(text(),'Name')]/following::text()[1]", rating_xpath = "", date_xpath = "", pros_xpath = "//div[@id='maincontent']/p[position()>(count(//div[@id='maincontent']/p[strong[text()='PROS']]/preceding-sibling::p)+1) and position()<=count(//div[@id='maincontent']/p[strong[text()='CONS']]/preceding-sibling::p)]//text()", cons_xpath = "//div[@id='maincontent']/p[position()>(count(//div[@id='maincontent']/p[strong[text()='CONS']]/preceding-sibling::p)+1) and position()<=count(//div[@id='maincontent']/p[strong[text()='CONTACT']]/preceding-sibling::p)]//text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "((//p[text()='Conclusion']|//strong[text()='Conclusion'])[1]/following::p[1]//text()|//strong[text()='CONCLUSION']/../text())[1]", author_xpath = "//strong[contains(text(),'By:')]/following::text()[1]", title_xpath = "//div[@id='review-box']//h1[@class='title']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/avhub_com_au.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

