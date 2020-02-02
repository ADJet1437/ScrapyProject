# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Sotovik_ruSpider", spider_type = "AlaSpider", allowed_domains = "'sotovik.ru'", start_urls = "'http://www.sotovik.ru/catalog/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//ul[@class='pagination']/li[@class='active']/following-sibling::li[1]//a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[contains(@class,'list')]//h4/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = u"//ol[@class='breadcrumb']/li[position()=last()-1]//text()", category_path_xpath = u"//ol[@class='breadcrumb']/li[position()<last()]//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"normalize-space(substring-after(substring-before(//*[contains(./text(),'newsID')],';'),'='))", pname_xpath = u"//h1//text()", ocn_xpath = u"//ol[@class='breadcrumb']/li[position()<last()]//text()", pic_xpath = u"//div[@class='article__content']/descendant-or-self::img[1]/@src", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"normalize-space(substring-after(substring-before(//*[contains(./text(),'newsID')],';'),'='))", pname_xpath = u"//h1//text()", rating_xpath = u"", date_xpath = u"substring-before(//div[contains(@class,'header')]//time/@datetime,'T')", pros_xpath = u"", cons_xpath = u"", summary_xpath = u"(//article/p[1]//text() | //meta[@name='description']/@content)[last()]", verdict_xpath = u"normalize-space(//h2[contains(.,'Выводы') or contains(.,'выводы') or contains(.,'Итоги')]/following-sibling::p[string-length(normalize-space())>1][1])", author_xpath = u"//div[@class='sub-header']//span[contains(.,'Автор') and normalize-space(substring-after(.,':'))]//text() | //div[@class='sub-header']//span[contains(.,'Автор') and not(normalize-space(substring-after(.,':')))]/preceding-sibling::span[1]//a//text()", title_xpath = u"//h1//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "((?<=\:\s).*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/sotovik_ru.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

