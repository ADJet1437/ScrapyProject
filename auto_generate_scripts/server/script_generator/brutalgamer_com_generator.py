# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Brutalgamer_comSpider", spider_type = "AlaSpider", allowed_domains = "'brutalgamer.com'", start_urls = "'http://brutalgamer.com/category/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h2[@class='post-box-title']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pagination']/span[@id='tie-next-page']/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@id='crumbs']//span[@class='current']//text()", category_path_xpath = "(//div[@id='crumbs']//a | //div[@id='crumbs']//span[@class='current'])//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "(//div[@id='crumbs']//a | //div[@id='crumbs']//span[@class='current'])//text()", pic_xpath = "//h1/following::img[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "//div[@class='review-final-score']/h3/text()", date_xpath = "//span[@class='post-meta-author']/following::span[@class='tie-date'][1]//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//span[@class='post-meta-author']/following::p[string-length(.//text())>2][1]//text()", verdict_xpath = "//*[((starts-with(.//text(),'Final') or starts-with(.//text(),'FINAL')) and (contains(.//text(),'Thoughts') or contains(.//text(),'thoughts') or contains(.//text(),'THOUGHTS'))) or (starts-with(.//text(),'Conclusion'))]/following::p[string-length(.//text())>2][1]//text()", author_xpath = "//span[@class='post-meta-author']//text()", title_xpath = "//h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "100", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['Review'])
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/brutalgamer_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

