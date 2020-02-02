# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Goodhousekeeping_comSpider", spider_type = "AlaSpider", allowed_domains = "'goodhousekeeping.com'", start_urls = "'http://www.goodhousekeeping.com/appliances/','http://www.goodhousekeeping.com/beauty-products/','http://www.goodhousekeeping.com/electronics/','http://www.goodhousekeeping.com/health-products/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.scroll(wait_for_xpath = u"", wait_type = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[contains(@class,'special-article')]//a[contains(@class,'special-title') and not(contains(@href,'/news/'))]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = u"//header//ul[contains(@class,'tags')]/li[last()]//text()[normalize-space()]", category_path_xpath = u"//header//ul[contains(@class,'tags')]/li//text()[normalize-space()]")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"//link[@rel='canonical']/@href", pname_xpath = u"//h1//text()", ocn_xpath = u"//header//ul[contains(@class,'tags')]/li//text()[normalize-space()]", pic_xpath = u"//meta[@property='og:image']/@content", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"//link[@rel='canonical']/@href", pname_xpath = u"//h1//text()", rating_xpath = u"//div[contains(@class,'body-main')]//div[contains(@itemprop,'Rating')]//span[@itemprop='ratingValue']//text()", date_xpath = u"substring-before(//meta[@property='article:published_time']/@content,' ')", pros_xpath = u"//div[contains(@class,'feedback-pros')]//ul/li//text()", cons_xpath = u"//div[contains(@class,'feedback-cons')]//ul/li//text()", summary_xpath = u"//meta[@property='og:description']/@content", verdict_xpath = u"", author_xpath = u"//div[@itemprop='author']//a//text()", title_xpath = u"//h1//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = u"//section[@class='product-container']//span[@itemprop='price']//text()", id_kind = "Price")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=\/)\w\d+(?=\/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=\/)\w\d+(?=\/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/goodhousekeeping_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

