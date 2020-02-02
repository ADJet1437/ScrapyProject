# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Gaminglives_comSpider", spider_type = "AlaSpider", allowed_domains = "'gaminglives.com'", start_urls = "'http://www.gaminglives.com/category/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='post-inner']//h3/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pagination']/a[last()-1]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "'gaminglives.com'", category_path_xpath = "'gaminglives.com'")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//tr[@class='reviewtxt'][.//text()='Title']/td[last()]//text()", ocn_xpath = "'gaminglives.com'", pic_xpath = "(//div[@class='entry_author_image']/img/@src | //div[@class='post-date']/following::img[1]/@src)[1]", manuf_xpath = "//tr[@class='reviewtxt'][.//text()='Publisher']/td[last()]//text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//tr[@class='reviewtxt'][.//text()='Title']/td[last()]//text()", rating_xpath = "//img[contains(@title, 'review') and contains(@title, 'policy')]/@src", date_xpath = "//div[@class='post-date']/text()", pros_xpath = "//span[text()='Pros']/following-sibling::ul[1]//text()", cons_xpath = "//span[text()='Cons']/following-sibling::ul[1]//text()", summary_xpath = "(//span[text()='Summary']/following-sibling::p[string-length(text())>5][1] | //div[@class='post-date']/following::p[string-length(text())>5][1])[(position()>count(//span[text()='Summary']/following-sibling::p[string-length(text())>5][1]) and count(//span[text()='Summary']/following-sibling::p[string-length(text())>5][1]) > 0) or count(//span[text()='Summary']/following-sibling::p[string-length(text())>5][1]) = 0]//text()", verdict_xpath = "", author_xpath = "//a[@rel='author']//text()", title_xpath = "//div[@class='post']//h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "((?<=-)\d+(?=.gif))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/gaminglives_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

