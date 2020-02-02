# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Diisign_comSpider", spider_type = "AlaSpider", allowed_domains = "'diisign.com'", start_urls = "'http://www.diisign.com/category/test/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//div[contains(@class,'pagination')]//div[contains(@class,'left')]//a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//article//h2/a[contains(@href,'test')]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"substring-after(//article/@id,'post-')", pname_xpath = u"//h1//text()", ocn_xpath = u"//p[@class='post-meta']//a[contains(@rel,'category')]//text()", pic_xpath = u"//meta[@property='og:image']/@content", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"substring-after(//article/@id,'post-')", pname_xpath = u"//h1//text()", rating_xpath = u"", date_xpath = u"normalize-space(//p[@class='post-meta'])", pros_xpath = u"//p[contains(translate(.,' ',''),'Les+')]/text()[./preceding::text()[contains(translate(.,' ',''),'Les+')]]", cons_xpath = u"//p[contains(translate(.,' ',''),'Les–')]/text()[./preceding::text()[contains(translate(.,' ',''),'Les–')]]", summary_xpath = u"//div[@class='entry-content']/p[string-length(normalize-space())>1 and ./text()[contains(translate(.,',?!','.'),'.')]][1]//text()[normalize-space() and (name(..)='p' or name(..)='a')][not(./preceding-sibling::br/preceding-sibling::text()[normalize-space()] or (../preceding-sibling::br/preceding-sibling::text()[normalize-space()] and name(..)='a'))]", verdict_xpath = u"//div[@class='entry-content']/p[./*[contains(.,'onclusion')]][last()]/text()[normalize-space() and ./preceding::text()[contains(.,'onclusion')]][1]", author_xpath = u"//p[@class='post-meta']//a[contains(@rel,'author')]//text()", title_xpath = u"//h1//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d+\s\d+\s\d{4})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d %m %Y", languages = "fr", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/diisign_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

