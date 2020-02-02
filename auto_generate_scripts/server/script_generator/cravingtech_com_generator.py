# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Cravingtech_comSpider", spider_type = "AlaSpider", allowed_domains = "'cravingtech.com'", start_urls = "'http://www.cravingtech.com/category/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.scroll(wait_for_xpath = "", wait_type = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h3[contains(@class,'entry-title')]/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='entry-crumbs']/span[last()]//text()", category_path_xpath = "//div[@class='entry-crumbs']/span//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "//div[@class='entry-crumbs']/span//text()", pic_xpath = "(//div[@itemprop='reviewBody']/p[img][1]/img/@src|//div[contains(@class,'main-content')]//p[descendant-or-self::img][1]//img/@src)[1]", manuf_xpath = "//span[contains(text(),'Manufacturer')]/../text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "//div[@itemprop='reviewRating']/div[@class='result']//text()", date_xpath = "//header/div[@class='meta-info']//time[contains(@class,'entry-date')]//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "(//div[contains(@class,'summary')]|//article//div[p][1]/p[text()][1])[1]//text()", verdict_xpath = "//h2[contains(text(),'Conclusion')]/following::p[text()][1]//text()", author_xpath = "//div[@class='meta-info']/div[contains(@class,'author-name')]/a//text()", title_xpath = "//header/h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['Review'])
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%b %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/cravingtech_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

