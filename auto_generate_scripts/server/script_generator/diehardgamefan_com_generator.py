# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Diehardgamefan_comSpider", spider_type = "AlaSpider", allowed_domains = "'diehardgamefan.com'", start_urls = "'http://diehardgamefan.com/category/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h2[@class='title']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//li[contains(.//text(),'Next')]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='post-info']/span[@class='thecategory']/a[last()-1]//text()", category_path_xpath = "//div[@class='post-info']/span[@class='thecategory']/a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "//div[@class='post-info']/span[@class='thecategory']/a//text()", pic_xpath = "//header/following::img[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "", date_xpath = "//div[@class='post-info']/span[@class='thetime']//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//center/following::p[position()>1][string-length(.//text())>2][1]//text()", verdict_xpath = "(//p[count(.//node())>4][contains(.//text(),'Attention') and contains(.//text(),'Summary')] | //p[count(.//node())<=4][contains(.//text(),'Attention') and contains(.//text(),'Summary')]/following::p[string-length(.//text())>2][1])//text()", author_xpath = "//div[@class='post-info']/span[@class='theauthor']//text()", title_xpath = "//header//h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [])
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestVerdict", regex = "((?<=Short Attention Span Summary).*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/diehardgamefan_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

