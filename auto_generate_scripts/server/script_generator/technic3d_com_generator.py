# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Technic3d_comSpider", spider_type = "AlaSpider", allowed_domains = "'technic3d.com'", start_urls = "'https://www.technic3d.com/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//ul/li/a[contains(@href,'review')]/../div/div[@class='subnavBox']/div/a[contains(@href,'review')]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pagination']/a/i[contains(@class,'fa-chevron-right')]/../@href", level_index = "2", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[contains(@class,'excerpt')]/div/a/@href", level_index = "3", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//li[@itemprop='itemListElement'][last()]//span//text()", category_path_xpath = "//li[@itemprop='itemListElement']//span//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "//li[@itemprop='itemListElement']//span//text()", pic_xpath = "(//div[@class='rcolumn']/figure/img/@src | //div[@itemprop='reviewBody']/div/img/@src)[1]", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "//span[@itemprop='reviewRating']/meta[@itemprop='ratingValue']/@content", date_xpath = "//div[@class='rcolumn']/time[@itemprop='datePublished']//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "", author_xpath = "//span[@itemprop='author']//span[@itemprop='name']//text()", title_xpath = "//div[@class='headline']//h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "100", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [''])
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d.%m.%Y", languages = "de", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/technic3d_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

