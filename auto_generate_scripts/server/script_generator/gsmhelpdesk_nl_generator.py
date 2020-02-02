# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Gsmhelpdesk_nlSpider", spider_type = "AlaSpider", allowed_domains = "'gsmhelpdesk.nl'", start_urls = "'http://www.gsmhelpdesk.nl/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pagination']/a[contains(@class,'active')]/following-sibling::a[1]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[contains(@class,'main-list')]/div[@class='row']//a[@class='title']/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "substring-before(substring-after(//meta[@property='og:url']/@content,'/reviews/'),'/')", pname_xpath = "//meta[@property='og:title']/@content", ocn_xpath = "//ol[@class='breadcrumb']/li[last()-1]//text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "substring-before(substring-after(//meta[@property='og:url']/@content,'/reviews/'),'/')", pname_xpath = "//meta[@property='og:title']/@content", rating_xpath = "concat(' ',translate(concat(string(number(translate(//div[starts-with(@id,'body')]/descendant-or-self::img[@class='rating'][1]/@title,',','.'))*2),translate(string(//*[contains(.,'Conclusie') and not(//img[@class='rating'])]/following::node()[(contains(.,'eindcijfer') or contains(.,'rapportcijfer') or contains(.,'totaal') or contains(.,'afgerond')) and not(./following::node()[1][name()='b'] or ./preceding::node()[1][name()='b'] or ./b)][last()]),',','.'),translate(//*[contains(.,'Conclusie') and not(//img[@class='rating'])]/following::node()[(contains(.,'eindcijfer') or contains(.,'rapportcijfer') or contains(.,'totaal') or contains(.,'afgerond')) and (./following::node()[1][name()='b'] or ./preceding::node()[1][name()='b'] or ./b)][last()]/descendant-or-self::b[1]/text(),',','.')),'NaN',''))", date_xpath = "//body/descendant-or-self::h1[1]/following::div[starts-with(@class,'date')][1]//text()", pros_xpath = "//div[starts-with(@id,'body')]/descendant-or-self::h2[contains(.,'Plus') and contains(.,'minpunten')][1]/following::p[.//*[starts-with(.,'+')]][1]//text()[string-length(normalize-space())>1] | //li[./preceding::b[starts-with(.,'Voordelen') or starts-with(.,'Pluspunten')] and ./following::b[starts-with(.,'Nadelen') or starts-with(.,'Minpunten')]]/descendant-or-self::*[last()]/text()", cons_xpath = "//div[starts-with(@id,'body')]/descendant-or-self::h2[contains(.,'Plus') and contains(.,'minpunten')][1]/following::p[.//*[starts-with(.,'-')]][1]//text()[string-length(normalize-space())>1] | //li[./preceding::b[starts-with(.,'Nadelen') or starts-with(.,'Minpunten')]/preceding::b[starts-with(.,'Voordelen') or starts-with(.,'Pluspunten')]]/b[not(./ancestor::div[@id='comment-area'])]/text()", summary_xpath = "//body/descendant-or-self::h1[1]/following::p[string-length(normalize-space())>1][1]//text()", verdict_xpath = "//div[starts-with(@id,'body')]/descendant-or-self::*[(name()='h2' or name()='h1' or (name()='div' and @class='title')) and contains(.,'Conclusie') and count(//tbody[contains(.,'Conclusie')])<2][1]/following::node()[(name()='p' or (name()='div' and @class='content')) and string-length(normalize-space())>1][1]//text()[not(./preceding-sibling::br/preceding-sibling::node()[normalize-space()]) and not(../preceding-sibling::br/preceding-sibling::node()[normalize-space()]) and not(../preceding-sibling::img)] | //div[starts-with(@id,'body')]/descendant-or-self::*[(name()='h2' or name()='h1' or (name()='div' and @class='title')) and contains(.,'Conclusie') and count(//tbody[contains(.,'Conclusie')])<2][1]/following::node()[not(name()) and string-length(normalize-space())>1 and not(./preceding-sibling::br/preceding-sibling::node()[normalize-space()])][1] | //body/descendant-or-self::tbody[contains(.,'Conclusie') and count(//tbody[contains(.,'Conclusie')])>1][last()]/following::node()[string-length(normalize-space())>1][1]", author_xpath = "//body/descendant-or-self::h1[1]/following::div[starts-with(@class,'date')][1]//text()", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d{2}\-\d{2}\-\d{4})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "((?<=\|)\D*\w)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "(\D*(?=\|))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "(\w.*\w)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "((?<=\s)\d{1}\.\d{2}(?=(\s|\.)))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "((?<=\s)\d{1}\.\d{1}(?=(\s|\.)))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "((?<=\s)\d{1}(?=(\s|\.)))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\b\d\.\d(?=\s|\.))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\b\d\.\d{2}(?=\s|\.))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\b\d(?=\s|\.))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\s)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d-%m-%Y", languages = "nl", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/gsmhelpdesk_nl.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

