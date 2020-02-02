# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Arnnet_com_auSpider", spider_type = "AlaSpider", allowed_domains = "'arnnet.com.au'", start_urls = "'http://www.arnnet.com.au/section/products/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//div[@class='pagination']//a[@class='next']/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[@class='article_list']//article//h3[contains(@class,'article_title')]/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"//div[contains(@class,'article_wrap')]/@data-article-id", pname_xpath = u"//h1//text()", ocn_xpath = u"", pic_xpath = u"//div[@itemprop='articleBody']/descendant-or-self::img[1]/@src", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"//div[contains(@class,'article_wrap')]/@data-article-id", pname_xpath = u"//h1//text()", rating_xpath = u"", date_xpath = u"//span[@itemprop='datePublished']//text()", pros_xpath = u"", cons_xpath = u"", summary_xpath = u"//meta[@property='og:description']/@content", verdict_xpath = u"", author_xpath = u"//span[contains(@class,'author')]//a//text()", title_xpath = u"//h1//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d+\s\w+\s\d{4})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "(\w+[\s|\w|\.]*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d %B, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = u"//nav[@class='page_links']//li[.//a[not(normalize-space(@class))]][last()]//a/@href", test_verdict_xpaths = ['normalize-space(//div[@itemprop="articleBody"]//*[contains(translate(.," ",""),"ottomline") or contains(translate(.," ",""),"ottomLine") or contains(.,"onclusion")]/following-sibling::p[string-length(normalize-space())>1][1])'], pros_xpath = u"", cons_xpath = u"", rating_xpath = u"", award_xpath = u"", award_pic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/arnnet_com_au.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

