# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Singleservecoffee_comSpider", spider_type = "AlaSpider", allowed_domains = "'singleservecoffee.com'", start_urls = "'http://www.singleservecoffee.com/archives/cat_reviews.php'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='blogbody']//h1[@class='title']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "concat('archives/',//div[@class='blogbody']//a[contains(text(),'next')]/@href)", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//p[contains(text(),'Read') and contains(text(),'More')]/a[last()]//text()", category_path_xpath = "//p[contains(text(),'Read') and contains(text(),'More')]/a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "string(//node()[contains(.,'dc:title')])", pname_xpath = "", ocn_xpath = "//p[contains(text(),'Read') and contains(text(),'More')]/a//text()", pic_xpath = "//div[@class='blogbody']/p[img][1]/img/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "(//strong | //b)[contains(text(),'Rating: ')]//text()", date_xpath = "//h2[@class='date']//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[@class='blogbody']/p[text()][string-length(text())>5][1]//text()", verdict_xpath = "", author_xpath = "", title_xpath = "//h1[@class='title']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['Review:'])
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=/)\d+(?=.php))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "100", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\d{2,3})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/singleservecoffee_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

