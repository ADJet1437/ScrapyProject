# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Photoxels_comSpider", spider_type = "AlaSpider", allowed_domains = "'photoxels.com'", start_urls = "'http://www.photoxels.com/category/news/reviews_on_the_web/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//header[@class='entry-header']/h2[@class='entry-title']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//nav[@id='vce-pagination']/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1//text()", ocn_xpath = "//main//header[@class='entry-header']/span[@class='meta-category']/a[1]//text()", pic_xpath = "//h1/following::img[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1//text()", rating_xpath = "", date_xpath = "//main//header[@class='entry-header']//div[@class='entry-meta']//span[@class='updated']//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "", author_xpath = "//main//header[@class='entry-header']//div[@class='entry-meta']//span[contains(@class,'author')]//a//text()", title_xpath = "//h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "(.*(?= Review))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(.*(?= Review))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[@class='entry-content']//node()[contains(.,'Read') and contains(.,'more')]/following::a[1]/@href", test_verdict_xpaths = ['//p[contains(text(),"See") and contains(text(),"if") and contains(text(),"you")]/preceding::p[string-length(.//text())>2][1]//text()'], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/photoxels_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

