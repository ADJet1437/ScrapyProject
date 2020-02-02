# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Notebookreview_enSpider", spider_type = "AlaSpider", allowed_domains = "'notebookreview.com'", start_urls = "'http://www.notebookreview.com/notebookreview/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//section[@class='contentListContainer']//a[img]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[1]/div[@class='wp-pagenavi']/a[@rel='next']/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='breadcrumbs']/a[last()]/text()", category_path_xpath = "//div[@class='breadcrumbs']/a/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[@id='headline']/text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(.*)Review", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1[@id='headline']/text()", rating_xpath = "//li[contains(@class,'ratingsTotal')]/ul/li[@class='ratingValue']/text()", date_xpath = "//time[@itemprop='datePublished']/@datetime", pros_xpath = "//h2[contains(text(),'Pros')]/following-sibling::ul[1]//text()", cons_xpath = "//h2[contains(text(),'Cons')]/following-sibling::ul[1]//text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "", author_xpath = "//span[@itemprop='author']/span/text()", title_xpath = "//h1[@id='headline']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//a[contains(text(),'Conclusion')]/@href", test_verdict_xpaths = ['//*[*[contains(text(),"Conclusion")]]/following-sibling::p[1]/text()' ,'//*[contains(text(),"Conclusion")]/following-sibling::p[1]//text()','//*[contains(text(),"Conclusion")]/following-sibling::p[text()][1]//text()'], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/notebookreview_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

