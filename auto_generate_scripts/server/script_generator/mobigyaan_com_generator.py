# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Mobigyaan_comSpider", spider_type = "AlaSpider", allowed_domains = "'mobigyaan.com'", start_urls = "'https://www.mobigyaan.com/category/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//article//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='wp-pagenavi']/a[@class='nextpostslink']/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//nav[@class='gk-breadcrumbs']/span[last()]//text()", category_path_xpath = "//nav[@class='gk-breadcrumbs']//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//article/@id", pname_xpath = "//h1//text()", ocn_xpath = "//nav[@class='gk-breadcrumbs']//text()", pic_xpath = "//a[@rel='author']/following::img[1]/@src", manuf_xpath = "(//nav[@class='gk-breadcrumbs']//*[contains(@href,'mobile-phones-tablets')] | //nav[@class='gk-breadcrumbs'][count(//nav[@class='gk-breadcrumbs']//*[contains(@href,'mobile-phones-tablets')])=0]//*[contains(@href,'category')][1])//text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//article/@id", pname_xpath = "//h1//text()", rating_xpath = "", date_xpath = "//time[@class='entry-date']//text()", pros_xpath = "((//h2|//strong)[contains(.//text(),'Strength') or contains(.//text(),'Pros')][1]/following::ul[1]/li | //p[strong[contains(.//text(),'Strength') or contains(.//text(),'Pros')]][count(node())>2][count(following-sibling::ul[1])=0] | //p[strong[contains(.//text(),'Strength') or contains(.//text(),'Pros')]][count(node())=1][count(following-sibling::ul[1])=0]/following::p[string-length(.//text())>2][1])//text()", cons_xpath = "((//h2|//strong)[contains(.//text(),'Weakness') or contains(.//text(),'Cons')][1]/following::ul[1]/li | //p[strong[contains(.//text(),'Weakness') or contains(.//text(),'Cons')]][count(node())>2][count(following-sibling::ul[1])=0] | //p[strong[contains(.//text(),'Weakness') or contains(.//text(),'Cons')]][count(node())=1][count(following-sibling::ul[1])=0]/following::p[string-length(.//text())>2][1])//text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "((//h2|//strong)[contains(.//text(),'Verdict') or contains(.//text(),'Conclusion')][1]/following::p[string-length(.//text())>2][1] | //text()[contains(.,'Final') and contains(.,'Words')][count((//h2|//strong)[contains(.//text(),'Verdict') or contains(.//text(),'Conclusion')])=0]/following::*[name()='span' or name()='p'][1][string-length(.//text())>2][1])//text()", author_xpath = "//a[@rel='author']//text()", title_xpath = "//h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "(\d+)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "(\d+)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(.*(?=Review)|.*(?=review)|.*(?=:)|.*(?=Test Results))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "(.*(?=Review)|.*(?=review)|.*(?=:)|.*(?=Test Results))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/mobigyaan_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

