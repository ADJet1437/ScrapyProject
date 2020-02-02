# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Gottabemobile_comSpider", spider_type = "AlaSpider", allowed_domains = "'gottabemobile.com'", start_urls = "'http://www.gottabemobile.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//ul[starts-with(@class,'page')]/li/a[starts-with(@class,'next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//article//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "substring-after(//article/@id,'-')", pname_xpath = "", ocn_xpath = "", pic_xpath = "//head/meta[contains(@name,'image')][1]/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "substring-after(//article/@id,'-')", pname_xpath = "", rating_xpath = "//span[contains(@class,'rating') and contains(@class,'result')]//text()", date_xpath = "//span/time/@datetime", pros_xpath = "//h3[contains(translate(.,' ',''),'WhatWeLike')]/following::ul[1]/li/text() | //p[contains(translate(.//text(),' ',''),'Whatwelike')]/text()", cons_xpath = "//h3[contains(translate(.,' ',''),'WhatWeDo')]/following::ul[1]/li/text() | //p[contains(translate(.//text(),' ',''),'Whatwedo')]/text()", summary_xpath = "//article/descendant-or-self::*[(name()='section' and starts-with(@class,'cb-entry-content') and ./p) or (name()='div' and contains(@class,'summary'))][1]/p[string-length(normalize-space())>1][1]//text()", verdict_xpath = "//article/descendant-or-self::*[(name()='section' and starts-with(@class,'cb-entry') and ./p) or @itemprop='reviewBody'][last()]/p[string-length(normalize-space())>1 and (not(./preceding::h2) or ./preceding::*[string-length(normalize-space())>1][1][name()='h2']) and not(contains(.,'check') and contains(.,'later')) and not(contains(@onclick,'Amazon') and contains(@onclick,'$')) and not(./em)][last()]//text()", author_xpath = "//span[@class='cb-author']/a//text()", title_xpath = "//title//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [])
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/gottabemobile_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

