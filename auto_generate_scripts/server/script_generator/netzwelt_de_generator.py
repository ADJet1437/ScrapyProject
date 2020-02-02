# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Netzwelt_deSpider", spider_type = "AlaSpider", allowed_domains = "'netzwelt.de'", start_urls = "'http://www.netzwelt.de/testberichte/index.html'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//nav/ul/li[last()]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//li[starts-with(@class,'tlr')]//a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//ul/li[last()-1]/a[@itemprop='item']//text()", ocn_xpath = "//ul/li[last()-2]/a[@itemprop='item']//text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//ul/li[last()-1]/a[@itemprop='item']//text()", rating_xpath = "//div[@itemprop='review']/div/@data-rating", date_xpath = "//meta[@name='date']/@content", pros_xpath = "//div[starts-with(normalize-space(),'Vorteile')]/following-sibling::ul[1]/li/text()", cons_xpath = "//div[starts-with(normalize-space(),'Nachteile')]/following-sibling::ul[1]/li/text()", summary_xpath = "//p[@class='rs1bp' or @class='ns1bp']/strong[@class='teaser']/text()", verdict_xpath = "", author_xpath = "(//b/time/following::b[1]/text() | //a[starts-with(@rel,'author')]/text() | //dl/dd[not(./a) and position()=1]/text())[1]", title_xpath = "//h1/strong/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d[^\s]*(?=T))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[starts-with(@class,'cblb')]/ul/li[last()]/a/@href", test_verdict_xpaths = ['//*[@id="fazit" or @class="rs1wbs"]/following-sibling::p[1]/text()'], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/netzwelt_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

