# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Ljudochbild_seSpider", spider_type = "AlaSpider", allowed_domains = "'ljudochbild.se'", start_urls = "'http://www.ljudochbild.se/test'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='navigation']//li[*[contains(@class,'page current')]]/following-sibling::li[1]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//*[@class='test-title']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h3[@class='text-brand']/text()", ocn_xpath = "//link[@rel='canonical']/@href", pic_xpath = "(//div[@class='single-thumbnail']/img/@src | //div[@class='entry-content']/div[contains (@id,'attachment')][1]/a/@href)[last()]", manuf_xpath = "//dd[@class='manufacturer']//text()")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "OriginalCategoryName", regex = "((?<=test\/)[^\/]+(?=\/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h3[@class='text-brand']/text()", rating_xpath = "//dd[@class='rate_total']/span[contains (@class,'filled')][1]/@title", date_xpath = "//p[@class='date']//meta/@content", pros_xpath = "//div[contains (@class,'infobox')]/*[contains (.,'Plus')]/following-sibling::p[1]//text()", cons_xpath = "//div[contains (@class,'infobox')]/*[contains (.,'Minus')]/following-sibling::p[1]//text()", summary_xpath = "//*[@itemprop='description']//text()", verdict_xpath = "//strong[contains (.,'Slutsats')]/../following-sibling::*[1]/text()", author_xpath = "//a[@itemprop='author']/text()", title_xpath = "//h3[@class='text-brand']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\d(?=\s))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['test','av'])
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "6", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/ljudochbild_se.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

