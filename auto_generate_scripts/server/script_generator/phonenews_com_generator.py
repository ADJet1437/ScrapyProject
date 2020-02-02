# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Phonenews_comSpider", spider_type = "AlaSpider", allowed_domains = "'phonenews.com'", start_urls = "'http://www.phonenews.com/category/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h2[@class='entry-title']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='navigation-links']//span[@class='next']/../@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='breadcrumb-trail']/*[position()=last()]//text()", category_path_xpath = "//div[@class='breadcrumb-trail']/*[position()>1 and position()!=last()-1]//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//link[@rel='canonical']/@href", pname_xpath = "", ocn_xpath = "//div[@class='breadcrumb-trail']/*[position()>1 and position()!=last()-1]//text()", pic_xpath = "//p[@class='byline']/following::img[1]/@src", manuf_xpath = "//span[@class='category']/a[contains(@href,'manufacture') or contains(@href,'conglomerates')]//text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//link[@rel='canonical']/@href", pname_xpath = "", rating_xpath = "//span[@class='rating']//text()", date_xpath = "//p[@class='byline']/abbr[@class='published']//text()", pros_xpath = "//strong[starts-with(text(),'Pros:')]/following-sibling::text()[1]", cons_xpath = "//strong[starts-with(text(),'Cons:')]/following-sibling::text()[1]", summary_xpath = "//div[@class='entry-content']//p[string-length(text())>5][1]//text()", verdict_xpath = "//*[starts-with(text(),'Conclusion')]/following::p[string-length(text())>5][1]//text()", author_xpath = "//p[@class='byline']//span[contains(@class,'author')]//text()", title_xpath = "//h1[contains(@class,'entry-title')]//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['Review:'])
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=-)\d+(?=/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=-)\d+(?=/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/phonenews_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

