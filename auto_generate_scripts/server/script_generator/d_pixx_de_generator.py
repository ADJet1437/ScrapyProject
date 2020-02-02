# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "D_pixx_deSpider", spider_type = "AlaSpider", allowed_domains = "'d-pixx.de'", start_urls = "'http://www.d-pixx.de/category/test/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//ul[@class='page-numbers']/li[.//a[contains(@class,'next')]]//a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[@id='main']//article//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"substring-after(//article/@id,'post-')", pname_xpath = u"//h1//text()", ocn_xpath = u"concat(//p[@class='cb-tags']//a[not(normalize-space())],'Test')", pic_xpath = u"//article/descendant-or-self::img[1]/@src", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"substring-after(//article/@id,'post-')", pname_xpath = u"//h1//text()", rating_xpath = u"", date_xpath = u"translate(translate(translate(substring(substring-after(//link[@rel='canonical']/@href,'.de/'),1,10),substring(substring-after(//link[@rel='canonical']/@href,'.de/'),9,1),'0'),substring(substring-after(//link[@rel='canonical']/@href,'.de/'),10,1),'1'),'/','-')", pros_xpath = u"", cons_xpath = u"", summary_xpath = u"normalize-space(//section/p[string-length(normalize-space())>1][1])", verdict_xpath = u"normalize-space(//section/p[string-length(normalize-space())>1 and ./preceding::text()[string-length(normalize-space())>1][1][translate(.,' ','')='Allesinallem']])", author_xpath = u"//div[@itemprop='author']//text()", title_xpath = u"//h1//text()", award_xpath = u"//section/p[.//img[contains(@alt,'test_logo')]][1]/descendant-or-self::img[1]/preceding::strong[1]//text()", awpic_xpath = u"//section/p[.//img[contains(@alt,'test_logo')]][1]/descendant-or-self::img[1]/@src")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/d_pixx_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

