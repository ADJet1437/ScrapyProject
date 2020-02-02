# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Exler_ruSpider", spider_type = "AlaSpider", allowed_domains = "'exler.ru'", start_urls = "'https://www.exler.ru/expromt/byyears/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//td[@id='TopicRightText']//td/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//table[./preceding-sibling::*[normalize-space()='Обзоры']]//tr//a/@href", level_index = "3", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"", pname_xpath = u"//title//text()", ocn_xpath = u"//div[@class='Topic']//text()", pic_xpath = u"//div[@id='article']/descendant-or-self::img[1]/@src", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"", pname_xpath = u"//title//text()", rating_xpath = u"", date_xpath = u"//p[starts-with(.,'Дата')]//text()", pros_xpath = u"//ul[./preceding-sibling::*[string-length(normalize-space())>1][1][normalize-space()='Плюсы:' or normalize-space()='Плюсы' or normalize-space()='Достоинства' or normalize-space()='Достоинства:']]/li//text()[normalize-space()]", cons_xpath = u"//ul[./preceding-sibling::*[string-length(normalize-space())>1][1][normalize-space()='Минусы:' or normalize-space()='Минусы' or normalize-space()='Недостатки:' or normalize-space()='Недостатки']]/li//text()[normalize-space()]", summary_xpath = u"normalize-space(//div[@id='article']/p[@align='justify' or @align='JUSTIFY' and string-length(normalize-space())>1][1])", verdict_xpath = u"normalize-space(//div[@id='article']/descendant-or-self::p[contains(.,'выводы')]/following-sibling::p[string-length(normalize-space())>1][1])", author_xpath = u"//div[@class='FooterExler']//a//text()", title_xpath = u"//title//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d{2}\.\d{2}\.\d{4})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d.%m.%Y", languages = "ru", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/exler_ru.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

