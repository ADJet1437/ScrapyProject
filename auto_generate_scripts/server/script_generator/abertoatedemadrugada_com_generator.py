# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Abertoatedemadrugada_comSpider", spider_type = "AlaSpider", allowed_domains = "'abertoatedemadrugada.com'", start_urls = "'http://abertoatedemadrugada.com/search/label/An%C3%A1lises'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//div[@class='blog-pager']//a[contains(@class,'older')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[contains(@class,'blog-posts')]//h3/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"", pname_xpath = u"//meta[@property='og:title'][1]/@content", ocn_xpath = u"//span[@class='post-labels']//a//text()", pic_xpath = u"//meta[@property='og:image']/@content", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"", pname_xpath = u"//meta[@property='og:title'][1]/@content", rating_xpath = u"substring-before(substring-after(//div[contains(@class,'entry-content')]//div[.//img[contains(./@src,'_badge')]]//img/@src,'_badge'),'.')", date_xpath = u"substring-before(//*[@class='published']/@title,'T')", pros_xpath = u"//ul[./preceding-sibling::*[normalize-space()][1][normalize-space()='Prós' or normalize-space()='Prós:' or normalize-space()='Pros' or normalize-space()='Pros:']]/li//text()", cons_xpath = u"//ul[./preceding-sibling::*[normalize-space()][1][normalize-space()='Contras' or normalize-space()='Contras:' or normalize-space()='Contra' or normalize-space()='Contra:']]/li//text()", summary_xpath = u"//meta[@property='og:description']/@content", verdict_xpath = u"//div[contains(@class,'entry-content')]/*[name()='h3' or name()='b'][contains(.,'final') or contains(.,'Final') or contains(.,'finais') or contains(.,'Finais')]/following-sibling::text()[string-length(normalize-space())>1 and not(./preceding-sibling::br[1]/preceding-sibling::text()[string-length(normalize-space())>1]/preceding-sibling::*[name()='h3' or name()='b'][contains(.,'final') or contains(.,'Final') or contains(.,'finais') or contains(.,'Finais')])]", author_xpath = u"//span[contains(@class,'post-author')]//span//text()", title_xpath = u"//meta[@property='og:title'][1]/@content", award_xpath = u"//div[contains(@class,'entry-content')]//div[.//img[contains(./@src,'_badge')]]/following-sibling::*[string-length(normalize-space())>1][1]//text()", awpic_xpath = u"//div[contains(@class,'entry-content')]//div[.//img[contains(./@src,'_badge')]]//img[contains(./@src,'_badge')]/@src")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/abertoatedemadrugada_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

