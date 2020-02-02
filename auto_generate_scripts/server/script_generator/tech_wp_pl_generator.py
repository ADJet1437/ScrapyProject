# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Tech_wp_plSpider", spider_type = "AlaSpider", allowed_domains = "'tech.wp.pl'", start_urls = "'http://tech.wp.pl/kat,111804,name,testy,kategoria.html'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pgs']/a[last()]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@id='stgMain']/div[starts-with(@id,'stgCol')][1]//div[@class='bx']//h3/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//meta[@property='og:url']/@content", level_index = "3", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//ul[@class='lsPath']/li[last()]//text()", category_path_xpath = "//ul[@class='lsPath']/li//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//*[@name='entry']/@value", pname_xpath = "//meta[@property='og:title']/@content", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//*[@name='entry']/@value", pname_xpath = "//meta[@property='og:title']/@content", rating_xpath = "", date_xpath = "//meta[contains(@property,'time')]/@content", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[@class='art']/descendant-or-self::p[string-length(normalize-space())>0][1]//text()", verdict_xpath = "", author_xpath = "//meta[@name='author']/@content", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d[^\s]*(?=\s))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[@class='pgs']/a[last()-1]/@href", test_verdict_xpaths = ['//*[starts-with(.//text(),"OG") or contains(.//text(),"Podsumowanie")]/preceding::*[1]/following::p[contains(.,".") or contains(.,",") or contains(.,";") or contains(normalize-space()," ")][1]//text()'], pros_xpath = "//node()[starts-with(normalize-space(),'Zalety')]/following-sibling::node()[not(name()) and string-length(normalize-space())>0] | //node()[starts-with(normalize-space(),'Zalety')]/following::*[1]//text() | //*[starts-with(.,'PLUSY')]/preceding::*[1]/following::*[1]/text()", cons_xpath = "//node()[starts-with(normalize-space(),'Wady')]/following-sibling::node()[not(name()) and string-length(normalize-space())>0 and not(preceding::*[starts-with(.,'Zalety')])] | //node()[starts-with(normalize-space(),'Wady')]/following::*[not(./descendant-or-self::i)][1]//text() | //*[starts-with(.,'MINUSY')]/preceding::*[1]/following::*[1]/text()", rating_xpath = "translate(normalize-space(concat(substring(substring-before(//div[@class='content']//p[contains(.,'/10')]/descendant-or-self::text()[contains(.,'/10') and substring(translate(translate(concat(substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.,'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,':')],':')),'/'),substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.//text(),'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,'to') and not(contains(.,':'))],'to')),'/'),string(number(//p[contains(.,'ocena') or contains(.,'Ocena') or contains(.,'OCENA')]/descendant-or-self::text()[contains(.,'5') and not(contains(.,'10')) and not(contains(.,'/'))][last()]) * 2)),'NaN',''),',','.'),string-length(translate(translate(concat(substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.,'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,':')],':')),'/'),substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.//text(),'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,'to') and not(contains(.,':'))],'to')),'/'),string(number(//p[contains(.,'ocena') or contains(.,'Ocena') or contains(.,'OCENA')]/descendant-or-self::text()[contains(.,'5') and not(contains(.,'10')) and not(contains(.,'/'))][last()]) * 2)),'NaN',''),',','.'))-1,1)='.'],'/'),string-length(translate(translate(concat(substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.,'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,':')],':')),'/'),substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.//text(),'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,'to') and not(contains(.,':'))],'to')),'/'),string(number(//p[contains(.,'ocena') or contains(.,'Ocena') or contains(.,'OCENA')]/descendant-or-self::text()[contains(.,'5') and not(contains(.,'10')) and not(contains(.,'/'))][last()]) * 2)),'NaN',''),',','.'))-2,1),' ',substring(translate(translate(concat(substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.,'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,':')],':')),'/'),substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.//text(),'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,'to') and not(contains(.,':'))],'to')),'/'),string(number(//p[contains(.,'ocena') or contains(.,'Ocena') or contains(.,'OCENA')]/descendant-or-self::text()[contains(.,'5') and not(contains(.,'10')) and not(contains(.,'/'))][last()]) * 2)),'NaN',''),',','.'),string-length(translate(translate(concat(substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.,'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,':')],':')),'/'),substring-before(normalize-space(substring-after(//div[@class='content']//p[contains(.//text(),'/10')]/descendant-or-self::text()[contains(.,'/10') and contains(.,'to') and not(contains(.,':'))],'to')),'/'),string(number(//p[contains(.,'ocena') or contains(.,'Ocena') or contains(.,'OCENA')]/descendant-or-self::text()[contains(.,'5') and not(contains(.,'10')) and not(contains(.,'/'))][last()]) * 2)),'NaN',''),',','.'))))),' ','.')", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "((?<=\s)\d\.*\d*(?!\D))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/tech_wp_pl.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

