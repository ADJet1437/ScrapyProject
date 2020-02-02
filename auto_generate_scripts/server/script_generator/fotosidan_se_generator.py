# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Fotosidan_seSpider", spider_type = "AlaSpider", allowed_domains = "'fotosidan.se'", start_urls = "'http://www.fotosidan.se/articles.htm'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"(//a[@class='pagectl pagectlnext'])[1]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[div[@class='documentdescription'][contains(text(),'Fotosidan testar')]]/div[@class='documentlisttitle']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"", pname_xpath = u"//div[contains(@id,'content')]/h1/text()", ocn_xpath = u"", pic_xpath = u"//div[@id='supersuperingress']/div/img/@src", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"", pname_xpath = u"//div[contains(@id,'content')]/h1/text()", rating_xpath = u"", date_xpath = u"//div[@class='document']//div[@class='docinfo']//br/following::text()[1][normalize-space()]", pros_xpath = u"//h3[contains(.,'PLUS')]/following::p[1]//text()", cons_xpath = u"//h3[contains(.,'MINUS')]/following::p[1]//text()", summary_xpath = u"//meta[@name='description']/@content", verdict_xpath = u"//h2[text()='Slutsats']/following::p[1]//text()", author_xpath = u"//div[@class='document']//div[@class='docinfo']//a[contains(@href,'/member')]/text()", title_xpath = u"//div[contains(@id,'content')]/h1/text()", award_xpath = u"", awpic_xpath = u"(//div[@class='sidebarpart' and @id='sidebar-text']//p//text()[normalize-space()])[last()]/following::a[1]/img[last()-1]/@src")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d{4}-\d{2}-\d{2})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/fotosidan_se.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

