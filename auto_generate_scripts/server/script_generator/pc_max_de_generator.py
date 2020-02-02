# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Pc_max_deSpider", spider_type = "AlaSpider", allowed_domains = "'pc-max.de'", start_urls = "'http://www.pc-max.de/tags/test'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//ul[starts-with(@class,'pag')]/li[contains(@class,'next')]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='view-content']//ul/li/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[contains(@class,'breadcrumb')]/a[last()]//text()", category_path_xpath = "//div[contains(@class,'breadcrumb')]/a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1/text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "//body/descendant-or-self::th[contains(.,'Hersteller')][1]/following::td[1]//text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1/text()", rating_xpath = "", date_xpath = "//div[@class='content']/descendant-or-self::*[starts-with(.,'Datum')]/following-sibling::*[string-length(normalize-space())>1][1]/text()", pros_xpath = "//div[starts-with(@class,'content')]/*[(name()='p' or (name()='div' and not(//div[starts-with(@class,'content')]/p))) and translate(./descendant-or-self::*/text(),' ','')='Pro' or translate(./descendant-or-self::*/text(),' ','')='Pro:' or concat(substring(./descendant-or-self::*[string-length(normalize-space())=3]/text(),1,1),'o',substring(./descendant-or-self::*[string-length(normalize-space())=3]/text(),3,1))='For' or translate(concat(substring(./descendant-or-self::*/text(),1,1),'o',substring(./descendant-or-self::*/text(),3,5)),' ','')='Fordas' or translate(./descendant-or-self::*/text(),' ','')='Positiv'][1]//text()", cons_xpath = "//div[starts-with(@class,'content')]/*[(name()='p' or (name()='div' and not(//div[starts-with(@class,'content')]/p))) and translate(./descendant-or-self::*/text(),' ','')='Contra' or translate(./descendant-or-self::*/text(),' ','')='Contra:' or (starts-with(translate(./descendant-or-self::*/text(),' ',''),'Gegen') and string-length(substring-before(concat(normalize-space(./descendant-or-self::*[starts-with(.,'Gegen')]/text()),' '),' '))<8) or starts-with(translate(./descendant-or-self::*/text(),' ',''),'Gegendas') or starts-with(translate(./descendant-or-self::*/text(),' ',''),'Dagegen') or translate(./descendant-or-self::*/text(),' ','')='Negativ'][1]//text()", summary_xpath = "//meta[@property='og:description' and normalize-space(@content)]/@content", verdict_xpath = "", author_xpath = "//div[@id='autorBox']/h4/a/text()", title_xpath = "//h1/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = "(//body/descendant-or-self::tr[contains(.,'Preis') and not(following-sibling::td)][1]/following-sibling::tr[1]/td[position()=count(//th[starts-with(normalize-space(),'Preis')]/preceding-sibling::*)+1]//text() | //body/descendant-or-self::tr[contains(.,'Preis')][1]/td//text())[1]", id_kind = "price")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d{2}\.\d{2}\.\d{4})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d.%m.%Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//body/descendant-or-self::div[@class='article-navigation'][1]/ol/li[last()]/a/@href", test_verdict_xpaths = ['//div[contains(@class,"center")]/descendant-or-self::div[starts-with(@class,"content")][1]/descendant-or-self::*[(name()="p" or (name()="div" and not(//div[starts-with(@class,"content")]/p))) and string-length(normalize-space(.//text()))>1 and not(.//script) and (contains(//div[@class="content"]//li/a[@class="active"]/text(),"Fazit") or preceding::*[string-length(normalize-space())>1][1][starts-with(.,"Fazit")])][1]//text()'], pros_xpath = "//div[starts-with(@class,'content')]/*[(name()='p' or (name()='div' and not(//div[starts-with(@class,'content')]/p))) and translate(./descendant-or-self::*/text(),' ','')='Pro' or translate(./descendant-or-self::*/text(),' ','')='Pro:' or concat(substring(./descendant-or-self::*[string-length(normalize-space())=3]/text(),1,1),'o',substring(./descendant-or-self::*[string-length(normalize-space())=3]/text(),3,1))='For' or translate(concat(substring(./descendant-or-self::*/text(),1,1),'o',substring(./descendant-or-self::*/text(),3,5)),' ','')='Fordas' or translate(./descendant-or-self::*/text(),' ','')='Positiv'][1]//text()", cons_xpath = "//div[starts-with(@class,'content')]/*[(name()='p' or (name()='div' and not(//div[starts-with(@class,'content')]/p))) and translate(./descendant-or-self::*/text(),' ','')='Contra' or translate(./descendant-or-self::*/text(),' ','')='Contra:' or (starts-with(translate(./descendant-or-self::*/text(),' ',''),'Gegen') and string-length(substring-before(concat(normalize-space(./descendant-or-self::*[starts-with(.,'Gegen')]/text()),' '),' '))<8) or starts-with(translate(./descendant-or-self::*/text(),' ',''),'Gegendas') or starts-with(translate(./descendant-or-self::*/text(),' ',''),'Dagegen') or translate(./descendant-or-self::*/text(),' ','')='Negativ'][1]//text()", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/pc_max_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

