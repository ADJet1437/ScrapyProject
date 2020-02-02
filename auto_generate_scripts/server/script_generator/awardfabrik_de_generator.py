# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Awardfabrik_deSpider", spider_type = "AlaSpider", allowed_domains = "'awardfabrik.de'", start_urls = "'http://awardfabrik.de/category/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//div[@class='full-nav']//li[contains(@class,'next')]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[@class='rt-grid-8']//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"substring-after(//link[@rel='shortlink']/@href,'p=')", pname_xpath = u"//div[starts-with(@id,'post-')]/h2//text()", ocn_xpath = u"//div[normalize-space(@class)='post-footer']//a[contains(@rel,'category')]//text()", pic_xpath = u"//div[starts-with(@id,'post-')]/descendant-or-self::img[1]/@src", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"substring-after(//link[@rel='shortlink']/@href,'p=')", pname_xpath = u"//div[starts-with(@id,'post-')]/h2//text()", rating_xpath = u"", date_xpath = u"//dl[@class='article-info']//dd[normalize-space(@class)='create']//text()", pros_xpath = u"", cons_xpath = u"", summary_xpath = u"//div[starts-with(@id,'post-')]/p[string-length(normalize-space())>1 and not(string-length(normalize-space())=string-length(normalize-space(substring-before(.,':')))+1)][1]//text() | //div[starts-with(@id,'post-')][not(./p[string-length(normalize-space())>1])]/text()[string-length(normalize-space())>1][1] | //div[starts-with(@id,'post-')]/span[not(../p[string-length(normalize-space())>1] or ../text()[string-length(normalize-space())>1])][string-length(normalize-space())>1][1]//text()", verdict_xpath = u"", author_xpath = u"//dl[@class='article-info']//dd[@class='createdby']//text()", title_xpath = u"//div[starts-with(@id,'post-')]/h2//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d+\s.+\s\d{4})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d %B %Y", languages = "de", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = u"//div[@class='pagination']//a[last()]/@href", test_verdict_xpaths = ['//div[contains(@class,"post-")]/p[./preceding-sibling::*[string-length(normalize-space())>1][contains(.,"Fazit")] or ./preceding-sibling::text()[string-length(normalize-space())>1][contains(.,"Fazit")] or not(./following-sibling::*[contains(.,"Fazit")] or ./following-sibling::text()[contains(.,"Fazit")]) and not(contains(.,"Fazit")) and not(./preceding-sibling::text()[string-length(normalize-space())>1])][not(string-length(normalize-space())=string-length(normalize-space(substring-before(.,":")))+1) and not(./*)][1]//text() | //div[contains(@class,"post-")]/text()[string-length(normalize-space())>1 and not(normalize-space()="Fazit" or normalize-space()="Fazit:")][1]'], pros_xpath = u"//div[starts-with(@id,'post-')]/p[contains(.,'Pro:') or contains(.,'Pros:')][1][string-length(normalize-space(substring-after(.,'Pro')))>2]/text() | //div[starts-with(@id,'post-')]/p[contains(.,'Pro:') or contains(.,'Pros:')][1][string-length(normalize-space(substring-after(.,'Pro')))<3]/following-sibling::*[string-length(normalize-space())>1][1]//text()", cons_xpath = u"//div[starts-with(@id,'post-')]/p[contains(normalize-space(),'ontra:')][1][string-length(normalize-space(substring-after(.,'ontra')))>1]/text() | //div[starts-with(@id,'post-')]/p[contains(normalize-space(),'ontra:')][1][string-length(normalize-space(substring-after(.,'ontra')))<2]/following-sibling::*[string-length(normalize-space())>1][1]//text()", rating_xpath = u"", award_xpath = u"", award_pic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/awardfabrik_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

