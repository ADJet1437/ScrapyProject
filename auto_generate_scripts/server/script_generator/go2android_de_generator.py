# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Go2android_deSpider", spider_type = "AlaSpider", allowed_domains = "'go2android.de'", start_urls = "'http://www.go2android.de/test/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='navigation']/a[contains(@class,'next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[starts-with(@id,'recent-post')]/div[starts-with(@id,'post')]//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "substring-before(substring-after(//body/@class,'postid-'),' ')", pname_xpath = "//h1//text()", ocn_xpath = "//ul[./preceding-sibling::a[1][normalize-space(./text())='Tests']]//li[contains(//div[starts-with(@id,'post-')]/@class,substring-before(substring-after(./a/@href,'/test/'),'/'))]/a[contains(@href,'test')]/text() | //li/a[normalize-space(./text())='Tests']/text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "substring-before(substring-after(//body/@class,'postid-'),' ')", pname_xpath = "//h1//text()", rating_xpath = "substring-before(substring-after(//table[contains(.,'Wertung')]/following::img[1]/@src,'rating_'),'.jpg')", date_xpath = "substring-before(//meta[contains(@property,'published_time')]/@content,'T')", pros_xpath = "//div[@class='entry']/descendant-or-self::*[normalize-space()='Positiv'][1]/following::ul[1]/li//text()", cons_xpath = "//div[@class='entry']/descendant-or-self::*[normalize-space()='Negativ'][1]/following::ul[1]/li//text()", summary_xpath = "//div[@class='entry']/p[string-length(normalize-space())>1][1]//text()", verdict_xpath = "//*[(name()='h2' or name()='h3') and contains(.,'Fazit')]/following::p[string-length(normalize-space(./text()))>1][1]//text()[1]", author_xpath = "//div[@class='meta-author']/a/text()", title_xpath = "//h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "((?<=\[Test\]).*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "((?<=\[Test\]).*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/go2android_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

