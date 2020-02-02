# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Thinkcomputers_orgSpider", spider_type = "AlaSpider", allowed_domains = "'thinkcomputers.org'", start_urls = "'http://www.thinkcomputers.org/category/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//link[@rel='next']/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//main//article//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"substring-after(//link[@rel='shortlink']/@href,'p=')", pname_xpath = u"//h1//text()", ocn_xpath = u"//header//div[contains(@class,'entry-categories')]//text()", pic_xpath = u"//main/descendant-or-self::img[1]/@src", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"substring-after(//link[@rel='shortlink']/@href,'p=')", pname_xpath = u"//h1//text()", rating_xpath = u"", date_xpath = u"substring-before(//header//p[@class='entry-meta']//time/@datetime,'T')", pros_xpath = u"", cons_xpath = u"", summary_xpath = u"//meta[@name='description']/@content", verdict_xpath = u"", author_xpath = u"//p[@class='entry-meta']//span[@itemprop='author']//a//text()", title_xpath = u"//h1//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = u"//ul[contains(@class,'pagination')]/li[.//a][last()]//a/@href", test_verdict_xpaths = ['//div[@class="entry-content"]/p[string-length(normalize-space())>1]//text()[normalize-space()][./preceding::text()[normalize-space()][1][contains(translate(.," ",""),"FinalThought")]]'], pros_xpath = u"//p//text()[string-length(normalize-space())>1][./preceding-sibling::*[string-length(normalize-space())>1][1][normalize-space()='Pros:' or normalize-space()='Pros']]", cons_xpath = u"//p//text()[string-length(normalize-space())>1][./preceding-sibling::*[string-length(normalize-space())>1][1][normalize-space()='Cons:' or normalize-space()='Cons']]", rating_xpath = u"substring-before(substring-after(//*[.//img[contains(@alt,'Award')]]/descendant-or-self::img[contains(@src,'rating')]/@src,'rating'),'_')", award_xpath = u"//*[.//img[contains(@alt,'Award')]]/descendant-or-self::img[1]/@alt", award_pic_xpath = u"//*[.//img[contains(@alt,'Award')]]/descendant-or-self::img[1]/@src")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/thinkcomputers_org.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

