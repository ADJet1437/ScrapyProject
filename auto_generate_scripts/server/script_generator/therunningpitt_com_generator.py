# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Therunningpitt_comSpider", spider_type = "AlaSpider", allowed_domains = "'therunningpitt.com'", start_urls = "'http://therunningpitt.com/category/recensioni'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//div[@class='pagination']//a[contains(.,'Next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//h3/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"substring-after(//link[@rel='shortlink']/@href,'p=')", pname_xpath = u"//div[@class='inner_wrapper']/descendant-or-self::*[contains(name(),'h')][1]//text()[normalize-space()]", ocn_xpath = u"//meta[@property='article:section']/@content", pic_xpath = u"//meta[@property='og:image']/@content", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"substring-after(//link[@rel='shortlink']/@href,'p=')", pname_xpath = u"//div[@class='inner_wrapper']/descendant-or-self::*[contains(name(),'h')][1]//text()[normalize-space()]", rating_xpath = u"", date_xpath = u"substring-before(//meta[@property='article:published_time']/@content,'T')", pros_xpath = u"", cons_xpath = u"", summary_xpath = u"//div[@class='post_inner_wrapper']/p[string-length(normalize-space())>1][1]//text()", verdict_xpath = u"//div[@class='post_inner_wrapper']/descendant-or-self::p[.//strong[contains(.,'onclusi')]][1]/text()", author_xpath = u"//div[@class='post_detail']//text()[./preceding-sibling::*[contains(@src,'author')]]", title_xpath = u"//div[@class='inner_wrapper']/descendant-or-self::*[contains(name(),'h')][1]//text()[normalize-space()]", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "((?<=Scritto\sda).*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/therunningpitt_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

