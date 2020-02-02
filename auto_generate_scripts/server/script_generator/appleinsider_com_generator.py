# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Appleinsider_comSpider", spider_type = "AlaSpider", allowed_domains = "'appleinsider.com'", start_urls = "'http://appleinsider.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@id='mp-nav']/ul/li[last()]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[starts-with(@class,'post')]/h1/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//title/text()", ocn_xpath = "//span[@class='reviews']/text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//title/text()", rating_xpath = "string(concat(substring-before(concat(normalize-space(substring-after(//*[starts-with(normalize-space(),'Score:')]/text(),'Score:')),' '),' '), substring-before(//*[starts-with(normalize-space(),'Rating') and not (//*[starts-with(normalize-space(),'Score:')])]/following::img[1]/@alt,' ')))", date_xpath = "substring-before(substring-after(//script[@type='application/ld+json']/text(),'datePublished'),',')", pros_xpath = "//node()[normalize-space()='Pro' or normalize-space()='Pros' or normalize-space()='Pro:' or normalize-space()='Pros:' or contains(translate(.,' ',''),'TheGood')]/following-sibling::ul[1]//text() | //node()[normalize-space()='Pro' or normalize-space()='Pros' or normalize-space()='Pro:' or normalize-space()='Pros:' or contains(translate(.,' ',''),'TheGood')]/following-sibling::node()[not(name()) and not(./preceding::strong/preceding::strong[normalize-space()='Pro' or normalize-space()='Pros' or normalize-space()='Pro:' or normalize-space()='Pros:' or contains(translate(.,' ',''),'TheGood')])]", cons_xpath = "//node()[normalize-space()='Cons' or normalize-space()='Con' or normalize-space()='Con:'  or normalize-space()='Cons:' or contains(translate(.,' ',''),'TheBad')]/following-sibling::ul[1]//text() | //node()[normalize-space()='Cons' or normalize-space()='Con' or normalize-space()='Con:'  or normalize-space()='Cons:' or contains(translate(.,' ',''),'TheBad')]/following-sibling::node()[not(name()) and not(./preceding::strong/preceding::strong[normalize-space()='Cons' or normalize-space()='Con' or normalize-space()='Con:'  or normalize-space()='Cons:' or contains(translate(.,' ',''),'TheBad')])]", summary_xpath = "(//meta[@name='description' and string-length(normalize-space(./@content))>1]/@content | //span[@class='article-leader']//text())[1]", verdict_xpath = "", author_xpath = "//p[contains(@class,'byline')]/a/text()", title_xpath = "//title/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d{4}\-\d{2}\-\d{2})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[@id='mp-nav']/ul/li[last()-1]/a/@href", test_verdict_xpaths = ['//*[(name()="h1" or name()="h2" or name()="strong") and (contains(.,"Conclusion") or contains(translate(.," ",""),"Theverdict") or contains(.,"Verdict"))]/following-sibling::node()[not(name()) and string-length(normalize-space())>1 and not(./preceding-sibling::br/preceding-sibling::node()[string-length(normalize-space())>1]/preceding-sibling::*[(name()="h1" or name()="h2" or name()="strong") and (contains(.,"Conclusion") or contains(translate(.," ",""),"Theverdict") or contains(.,"Verdict"))])]'], pros_xpath = "//node()[normalize-space()='Pro' or normalize-space()='Pros' or normalize-space()='Pro:' or normalize-space()='Pros:' or contains(translate(.,' ',''),'TheGood')]/following-sibling::ul[1]//text() | //node()[normalize-space()='Pro' or normalize-space()='Pros' or normalize-space()='Pro:' or normalize-space()='Pros:' or contains(translate(.,' ',''),'TheGood')]/following-sibling::node()[not(name()) and not(./preceding::strong/preceding::strong[normalize-space()='Pro' or normalize-space()='Pros' or normalize-space()='Pro:' or normalize-space()='Pros:' or contains(translate(.,' ',''),'TheGood')])]", cons_xpath = "//node()[normalize-space()='Cons' or normalize-space()='Con' or normalize-space()='Con:'  or normalize-space()='Cons:' or contains(translate(.,' ',''),'TheBad')]/following-sibling::ul[1]//text() | //node()[normalize-space()='Cons' or normalize-space()='Con' or normalize-space()='Con:'  or normalize-space()='Cons:' or contains(translate(.,' ',''),'TheBad')]/following-sibling::node()[not(name()) and not(./preceding::strong/preceding::strong[normalize-space()='Cons' or normalize-space()='Con' or normalize-space()='Con:'  or normalize-space()='Cons:' or contains(translate(.,' ',''),'TheBad')])]", rating_xpath = "string(concat(substring-before(concat(normalize-space(substring-after(//*[starts-with(normalize-space(),'Score:')]/text(),'Score:')),' '),' '), substring-before(//*[starts-with(normalize-space(),'Rating') and not (//*[starts-with(normalize-space(),'Score:')])]/following::img[1]/@alt,' ')))", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/appleinsider_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

