# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Itpro_co_ukSpider", spider_type = "AlaSpider", allowed_domains = "'itpro.co.uk'", start_urls = "'http://www.itpro.co.uk/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//ul[@class='pager']/li[starts-with(@class,'pager-next')]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//main[contains(@id,'group-content')]//ul[@class='view-rows']//h5//a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//nav[starts-with(@class,'breadcrumb')]/ol/li[position()=last()-2]//text()", category_path_xpath = "//nav[starts-with(@class,'breadcrumb')]/ol/li[position()<last()]//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//link[@rel='canonical']/@href", pname_xpath = "//h1/text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//link[@rel='canonical']/@href", pname_xpath = "//h1/text()", rating_xpath = "//div[@id='content']//div[@class='fivestar-default']//text()", date_xpath = "substring-before(//span[contains(@datatype,'dateTime')]/@content,'T')", pros_xpath = "//div[@class='field-label' and starts-with(normalize-space(),'Pros')]/following::div[1]/*/text()", cons_xpath = "//div[@class='field-label' and starts-with(normalize-space(),'Cons')]/following::div[1]/*/text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "//div[@class='field-label' and starts-with(normalize-space(),'Verdict')]/following::div[1]/*/text()", author_xpath = "//div[@class='content']/descendant-or-self::span[contains(@property,'reviewer') or contains(@class,'field-author')][1]//span//text()", title_xpath = "//h1/text()", award_xpath = "//img[@class='award_logo']/@title", awpic_xpath = "//img[@class='award_logo']/@src")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = "substring-before(concat(normalize-space(//div[@class='field-label' and starts-with(normalize-space(),'Price')]/following::div[1]/*[string(number(substring(normalize-space(),1,1)))='NaN']/text()),' '),' ')", id_kind = "price")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=\/)\d*\d(?=\/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=\/)\d*\d(?=\/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/itpro_co_uk.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

