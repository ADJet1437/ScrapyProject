# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Gamingillustrated_comSpider", spider_type = "AlaSpider", allowed_domains = "'gamingillustrated.com'", start_urls = "'http://gamingillustrated.com/tag/review/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//section[@class='middle']//h5/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='nav']//a[contains(@class,'next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//ul[@class='post-categories']/li[last()]//text()", category_path_xpath = "//ul[@class='post-categories']/li/a[not(contains(text(),'Featured'))]//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "//ul[@class='post-categories']/li[position()>1]//text()", pic_xpath = "//p[@class='linebtn']/following::img[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "//section[@class='ratingtop-rt']//span//text()", date_xpath = "//p[@class='linebtn']/text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//p[@class='linebtn']/following::p[string-length(text())>50][1]//text()", verdict_xpath = "//h3[starts-with(text(),'Overall')]/following::p[string-length(text())>5][1]//text()", author_xpath = "//p[@class='linebtn']/span[@class='green']/a[@rel='author']//text()", title_xpath = "//section[@class='postinmiddle']//h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['Review'])
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "100", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\d*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/gamingillustrated_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

