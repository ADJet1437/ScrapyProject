# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Ereviews_dkSpider", spider_type = "AlaSpider", allowed_domains = "'ereviews.dk'", start_urls = "'http://www.ereviews.dk/category/nyheder/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//div[@id='pagination']//li[@class='active']/following-sibling::li[1]//a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[@id='items-wrapper']//h3/a[contains(@href,'test-')]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"substring-after(//link[@rel='shortlink']/@href,'p=')", pname_xpath = u"//div[@id='post-header']//h1//text()", ocn_xpath = u"//span[@class='category']//a//text()", pic_xpath = u"//meta[@property='og:image'][last()]/@content", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"substring-after(//link[@rel='shortlink']/@href,'p=')", pname_xpath = u"//div[@id='post-header']//h1//text()", rating_xpath = u"substring-before(substring-after(//div[@class='overall-score']//img/@src,'_'),'.png')", date_xpath = u"substring-before(//meta[contains(@name,'published_time')]/@content,'T')", pros_xpath = u"//ul[@class='checklist']/li//text()", cons_xpath = u"//ul[@class='badlist']/li//text()", summary_xpath = u"normalize-space(//div[@class='post-content']/p[string-length(normalize-space())>1][1])", verdict_xpath = u"normalize-space(//div[@class='post-content']/p[string-length(normalize-space())>1 and ./preceding-sibling::*[string-length(normalize-space())>1][1][contains(.,'onklusion') and ./following-sibling::p[string-length(normalize-space())>1]]][1])", author_xpath = u"//span[@class='author']//text()", title_xpath = u"//div[@id='post-header']//h1//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/ereviews_dk.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

