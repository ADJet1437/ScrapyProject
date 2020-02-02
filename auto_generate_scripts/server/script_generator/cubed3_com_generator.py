# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Cubed3_comSpider", spider_type = "AlaSpider", allowed_domains = "'cubed3.com'", start_urls = "'http://www.cubed3.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='blurb']/h3/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[contains(@class,'pagination')]/a[contains(text(),'next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "game", category_path_xpath = "game")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "game", pic_xpath = "//div[@class='newstext']/div[contains(@class,'intro_box')]/img/@src", manuf_xpath = "//p[@itemprop='manufacturer']/a//text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "//span[@itemprop='ratingValue']/strong//text()", date_xpath = "//h2[contains(@class,'extratop')]/span[@class='clearfix']/p/img[contains(@src,'read-posts')]/../text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[contains(@class,'intro_box')]/span[@itemprop='about']/p//text()", verdict_xpath = "", author_xpath = "//h2[contains(@class,'extratop')]/a[@itemprop='name']//text()", title_xpath = "//h1[@itemprop='itemreviewed']//text()", award_xpath = "//div[contains(@id,'score')]/h4[contains(@class,'extratop')]//text()", awpic_xpath = "//div[@itemprop='reviewRating']/div[@id='final_score_box_right']/img/@src")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [' Review'])
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = " %m.%b.%Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/cubed3_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

