# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Giga_deSpider", spider_type = "AlaSpider", allowed_domains = "'giga.de'", start_urls = "'http://www.giga.de/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//a[starts-with(.,'Tests')]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[@class='next']/@href", level_index = "2", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//hgroup/h1/a/@href", level_index = "3", url_regex = "^((?!news/).)*$", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//img[contains(@src,'post')]/@src", pname_xpath = "", ocn_xpath = "//meta[@property='og:url']/@content", pic_xpath = "//link[@rel='image_src']/@href", manuf_xpath = "//p[@class='article-relations']/a[contains(@href,'unternehmen')]/text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//img[contains(@src,'post')]/@src", pname_xpath = "", rating_xpath = "string(concat(string(translate(string(count(//article//span[@class='fivestars']/i[contains(@class,'star') and not(contains(@class,'-o'))])),'0','')),translate(string(number(string(number(substring(substring-before(substring-after(//p[starts-with(.//text(),'Gesamt')]/*[text()]/text()[count(//article//span[@class='fivestars']/i[contains(@class,'star') and not(contains(@class,'-o'))])=0],' '),'%'),1,2)) div 20))),'NaN','')))", date_xpath = "//body/descendant-or-self::span[@class='meta' and ./time][1]/time/@datetime", pros_xpath = "//div[starts-with(@class,'content')]/descendant-or-self::*[normalize-space()='Pro' or normalize-space()='Pro:' or normalize-space()='PRO:' or normalize-space()='Vorteile' or normalize-space()='Vorteile:'][1]/following-sibling::ul[not(.//img) and not(./preceding-sibling::*[text()][1][not(normalize-space()='Pro' or normalize-space()='Pro:' or normalize-space()='PRO:' or normalize-space()='Vorteile' or normalize-space()='Vorteile:')])][1]/li//text() | //tr[(.//text())='Positiv' or (.//text())='Pro']/following-sibling::tr/td[not(.//*)][1]//text() | //div[starts-with(@class,'content')]/descendant-or-self::*[normalize-space()='Pro' or normalize-space()='Pro:' or normalize-space()='Vorteile' or normalize-space()='Vorteile:'][1]/following-sibling::node()[starts-with(normalize-space(),'+') and not(//*[normalize-space()='Pro' or normalize-space()='Pro:' or normalize-space()='Vorteile' or normalize-space()='Vorteile:']/following-sibling::ul[not(.//img) and not(./preceding-sibling::*[text()][1][not(normalize-space()='Pro' or normalize-space()='Pro:' or normalize-space()='Vorteile' or normalize-space()='Vorteile:')])][1]/li) and not(./ancestor-or-self::*[starts-with(.,'Nachteile')]) and not(./preceding::*[starts-with(.,'Nachteile')]) and not(//tr[(.//text())='Positiv' or (.//text())='Pro'])]", cons_xpath = "//div[starts-with(@class,'content')]/descendant-or-self::*[normalize-space()='Kontra' or normalize-space()='Kontra:' or normalize-space()='KONTRA:' or normalize-space()='Contra' or normalize-space()='Contra:' or normalize-space()='Nachteile' or normalize-space()='Nachteile:'][1]/following-sibling::ul[not(.//img) and not(./preceding-sibling::*[text()][1][not(normalize-space()='Kontra' or normalize-space()='Kontra:' or normalize-space()='KONTRA:' or normalize-space()='Contra' or normalize-space()='Contra:' or normalize-space()='Nachteile' or normalize-space()='Nachteile:')])][1]/li//text() | //tr[(.//text())='Negativ' or (.//text())='Kontra' or (.//text())='Contra']/following-sibling::tr/td[not(.//*)][2]//text() | //div[starts-with(@class,'content')]/descendant-or-self::*[normalize-space()='Kontra' or normalize-space()='Kontra:' or normalize-space()='Contra' or normalize-space()='Contra:' or normalize-space()='Nachteile' or normalize-space()='Nachteile:'][1]/following-sibling::node()[starts-with(normalize-space(),'-') and not(//*[normalize-space()='Kontra' or normalize-space()='Kontra:' or normalize-space()='Contra' or normalize-space()='Contra:' or normalize-space()='Nachteile' or normalize-space()='Nachteile:']/following-sibling::ul[not(.//img) and not(./preceding-sibling::*[text()][1][not(normalize-space()='Kontra' or normalize-space()='Kontra:' or normalize-space()='Contra' or normalize-space()='Contra:' or normalize-space()='Nachteile' or normalize-space()='Nachteile:')])][1]/li) and not(//tr[(.//text())='Negativ' or (.//text())='Kontra' or (.//text())='Contra'])]", summary_xpath = "//article/descendant-or-self::p[string-length(normalize-space())>1][1]//text()", verdict_xpath = "", author_xpath = "//a[@class='author']/text()", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [])
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=id\=).*\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "OriginalCategoryName", regex = "((?<=\.de/)\w*(?=/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=id\=).*\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d.*(?=T))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//section[@class='pagination']//ul/li[last()]/a/@href", test_verdict_xpaths = ['//article[starts-with(@class,"singles")]/descendant-or-self::*[(name()="p" or name()="h2" or name()="hgroup" or name()="h1") and (contains(.,"fazit") or contains(.,"Fazit") or contains(.,"FAZIT")) and not(contains(.,"Video"))][last()]/preceding-sibling::*[1]/following-sibling::node()[((name()="p" and ./text()) or (not(name()) and ./preceding::*[(contains(.,"fazit") or contains(.,"Fazit") or contains(.,"FAZIT")) and not(contains(.,"Video"))])) and string-length(normalize-space())>1 and not(./*)][1]//text()'], pros_xpath = "//div[starts-with(@class,'content')]/descendant-or-self::*[normalize-space()='Pro' or normalize-space()='Pro:' or normalize-space()='PRO:' or normalize-space()='Vorteile' or normalize-space()='Vorteile:'][1]/following-sibling::ul[not(.//img) and not(./preceding-sibling::*[text()][1][not(normalize-space()='Pro' or normalize-space()='Pro:' or normalize-space()='PRO:' or normalize-space()='Vorteile' or normalize-space()='Vorteile:')])][1]/li//text() | //tr[(.//text())='Positiv' or (.//text())='Pro']/following-sibling::tr/td[not(.//*)][1]//text() | //div[starts-with(@class,'content')]/descendant-or-self::*[normalize-space()='Pro' or normalize-space()='Pro:' or normalize-space()='Vorteile' or normalize-space()='Vorteile:'][1]/following-sibling::node()[starts-with(normalize-space(),'+') and not(//*[normalize-space()='Pro' or normalize-space()='Pro:' or normalize-space()='Vorteile' or normalize-space()='Vorteile:']/following-sibling::ul[not(.//img) and not(./preceding-sibling::*[text()][1][not(normalize-space()='Pro' or normalize-space()='Pro:' or normalize-space()='Vorteile' or normalize-space()='Vorteile:')])][1]/li) and not(./ancestor-or-self::*[starts-with(.,'Nachteile')]) and not(./preceding::*[starts-with(.,'Nachteile')]) and not(//tr[(.//text())='Positiv' or (.//text())='Pro'])]", cons_xpath = "//div[starts-with(@class,'content')]/descendant-or-self::*[normalize-space()='Kontra' or normalize-space()='Kontra:' or normalize-space()='KONTRA:' or normalize-space()='Contra' or normalize-space()='Contra:' or normalize-space()='Nachteile' or normalize-space()='Nachteile:'][1]/following-sibling::ul[not(.//img) and not(./preceding-sibling::*[text()][1][not(normalize-space()='Kontra' or normalize-space()='Kontra:' or normalize-space()='KONTRA:' or normalize-space()='Contra' or normalize-space()='Contra:' or normalize-space()='Nachteile' or normalize-space()='Nachteile:')])][1]/li//text() | //tr[(.//text())='Negativ' or (.//text())='Kontra' or (.//text())='Contra']/following-sibling::tr/td[not(.//*)][2]//text() | //div[starts-with(@class,'content')]/descendant-or-self::*[normalize-space()='Kontra' or normalize-space()='Kontra:' or normalize-space()='Contra' or normalize-space()='Contra:' or normalize-space()='Nachteile' or normalize-space()='Nachteile:'][1]/following-sibling::node()[starts-with(normalize-space(),'-') and not(//*[normalize-space()='Kontra' or normalize-space()='Kontra:' or normalize-space()='Contra' or normalize-space()='Contra:' or normalize-space()='Nachteile' or normalize-space()='Nachteile:']/following-sibling::ul[not(.//img) and not(./preceding-sibling::*[text()][1][not(normalize-space()='Kontra' or normalize-space()='Kontra:' or normalize-space()='Contra' or normalize-space()='Contra:' or normalize-space()='Nachteile' or normalize-space()='Nachteile:')])][1]/li) and not(//tr[(.//text())='Negativ' or (.//text())='Kontra' or (.//text())='Contra'])]", rating_xpath = "string(concat(string(translate(string(count(//article//span[@class='fivestars']/i[contains(@class,'star') and not(contains(@class,'-o'))])),'0','')),translate(string(number(string(number(substring(substring-before(substring-after(//p[starts-with(.//text(),'Gesamt')]/*[text()]/text()[count(//article//span[@class='fivestars'])=0],' '),'%'),1,2)) div 20))),'NaN',''),translate(string(number(substring(//div[starts-with(@class,'ratingBox')]//span[contains(@class,'rating')]/b,1,1)) div number(substring-after(//div[starts-with(@class,'ratingBox')]//span[contains(@class,'rating')]/node()[not(name())][count(//article//span[@class='fivestars'])=0 and count(//p[starts-with(.//text(),'Gesamt')]/*[text()])=0],'/')) * 5),'NaN','')))", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/giga_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

