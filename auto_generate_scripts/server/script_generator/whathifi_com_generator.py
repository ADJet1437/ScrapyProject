# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Whathifi_comSpider", spider_type = "AlaSpider", allowed_domains = "'whathifi.com'", start_urls = "'http://www.whathifi.com/products'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[starts-with(.,'next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h3[@class='title']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//nav/ol/li[last()-2]//text()", category_path_xpath = "//nav/ol/li[position()<last()-1]//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//link[@rel='shortlink']/@href", pname_xpath = "//nav/ol/li[last()-1]//text()", ocn_xpath = "", pic_xpath = "(//meta[@name='thumbnail']/@content | //div[@id='image-wrapper']//img/@src)[last()]", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//link[@rel='shortlink']/@href", pname_xpath = "//nav/ol/li[last()-1]//text()", rating_xpath = "//div[@id='field-rating']//meta[@itemprop='ratingValue']/@content", date_xpath = "//time/@datetime", pros_xpath = "//div[@class='field-label' and starts-with(normalize-space(text()),'For')]/following-sibling::*[1]//*[text()]/text()", cons_xpath = "//div[@class='field-label' and starts-with(normalize-space(text()),'Against')]/following-sibling::*[1]//*[text()]/text()", summary_xpath = "//span[@itemprop='description']//text()", verdict_xpath = "(//div[starts-with(.,'Our') and contains(.,'Verdict')]/following-sibling::div//*[text()]/text() | //div[@itemprop='reviewBody']//*[contains(.,'verdict') or starts-with(.,'Verdict')]/following-sibling::div[1]//p[1]/text())[1]", author_xpath = "//meta[@itemprop='author']/@content", title_xpath = "//*[@id='page-title']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=node\/).*\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=node\/).*\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/whathifi_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

