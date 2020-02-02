# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Kapselmaschinen_netSpider", spider_type = "AlaSpider", allowed_domains = "'kapselmaschinen.net'", start_urls = "'http://www.kapselmaschinen.net/testberichte/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//ul[@class='pagination']/li[.//a[contains(@class,'next')]]//a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"substring-after(//link[@rel='shortlink']/@href,'p=')", pname_xpath = u"//h1//text()", ocn_xpath = u"//p//a[contains(@rel,'category')]//text()", pic_xpath = u"(//div[@class='post']/descendant-or-self::img[1] | //div[@class='single-image']/img)[1]/@src", manuf_xpath = u"//div[@class='post']/ul/li[contains(.,'Hersteller')]/text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"substring-after(//link[@rel='shortlink']/@href,'p=')", pname_xpath = u"//h1//text()", rating_xpath = u"", date_xpath = u"normalize-space(//div[contains(@class,'stripes')])", pros_xpath = u"//div[contains(@class,'one_half') and contains(.,'Vorteile')]//ul/li//text()", cons_xpath = u"//div[contains(@class,'one_half') and contains(.,'Nachteile')]//ul/li//text()", summary_xpath = u"//div[@class='post']/p[string-length(normalize-space())>1][1]//text()", verdict_xpath = u"normalize-space(//div[@class='post']/*[contains(.,'Bewertung')]/following-sibling::*[string-length(normalize-space())>1][1][name()='p'])", author_xpath = u"//a[@title='Kapselmaschinen.net']//text()", title_xpath = u"//h1//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = u"//div[@class='post']/ul/li[contains(.,'Preis')]/text()", id_kind = "Price")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = u"//div[@class='post']/ul/li[contains(.,'Modellbezeichnung')]/text()", id_kind = "MPN")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d+\.\s.*\s\d{4})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d. %B %Y", languages = "de", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/kapselmaschinen_net.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

