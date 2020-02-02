# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Av_tribune_ruSpider", spider_type = "AlaSpider", allowed_domains = "'av-tribune.ru'", start_urls = "'http://www.av-tribune.ru/test-equipment.html'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//div[@class='pagination']//li[@class='pagination-next']/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[@class='page-header']/h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = u"//ul[@class='breadcrumb']/li[.//a][last()]//a//text()", category_path_xpath = u"//ul[@class='breadcrumb']/li[.//a]//a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"//base/@href", pname_xpath = u"//title//text()", ocn_xpath = u"//ul[@class='breadcrumb']/li[.//a]//a//text()", pic_xpath = u"//div[@itemprop='articleBody']/descendant-or-self::img[1]/@src", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"//base/@href", pname_xpath = u"//title//text()", rating_xpath = u"", date_xpath = u"substring-before(//time[@itemprop='datePublished']/@datetime,'T')", pros_xpath = u"", cons_xpath = u"", summary_xpath = u"//div[@itemprop='articleBody']/descendant-or-self::p[string-length(normalize-space())>1 and (normalize-space(.//strong/../text()) or normalize-space(.//strong/../*[not(name()='strong')]) or not(.//strong)) and (contains(.,'.') or contains(.,'?') or contains(.,'!'))][./preceding-sibling::p[string-length(normalize-space())>1][1][starts-with(normalize-space(),'Вступление')] or not(../p[starts-with(normalize-space(),'Вступление')])][1]//text() | //div[@itemprop='articleBody']/div[string-length(normalize-space())>1 and (normalize-space(.//strong/../text()) or normalize-space(.//strong/../*[not(name()='strong')]) or not(.//strong)) and (contains(.,'.') or contains(.,'?') or contains(.,'!'))][./preceding-sibling::div[string-length(normalize-space())>1][1][starts-with(normalize-space(),'Вступление')] or not(../div[starts-with(normalize-space(),'Вступление')])][1]//text()", verdict_xpath = u"normalize-space(//div[@itemprop='articleBody']/descendant-or-self::p[starts-with(translate(.,' ',''),'Подводимитог')]/following-sibling::p[string-length(normalize-space())>1][1])", author_xpath = u"//div[@itemprop='articleBody']/descendant-or-self::p[starts-with(normalize-space(),'Автор')]//text() | //base[not(//div[@itemprop='articleBody']/descendant-or-self::p[starts-with(normalize-space(),'Автор')])]/@href", title_xpath = u"//title//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=\/)\d+(?=\-))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=\/)\d+(?=\-))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "((?<=\:\s).*(?=\.))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "((?<=\:\s).*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "((?<=www\.)(\w|\.|\-)*(?=\/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/av_tribune_ru.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

