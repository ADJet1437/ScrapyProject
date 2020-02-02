# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Droid_life_comSpider", spider_type = "AlaSpider", allowed_domains = "'droid-life.com'", start_urls = "'http://www.droid-life.com/category/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='nav-previous']/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//article//h1/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "substring-after(//link[@rel='shortlink']/@href,'?p=')", pname_xpath = "", ocn_xpath = "//span[@class='cat-links']/a[not(contains(.,'News') or contains(.,'Featured'))]/text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "substring-after(//link[@rel='shortlink']/@href,'?p=')", pname_xpath = "", rating_xpath = "", date_xpath = "substring-before(//time/@datetime,'T')", pros_xpath = "//p[(./strong or ./b) and not(./text()) and ./preceding::*[name()='h3' or name()='h4'][contains(translate(.,' ',''),'TheGood') or contains(translate(.,' ',''),'WhatILike')] and (./following::*[name()='h3' or name()='h4'][contains(.,'in-the-Middle') or contains(translate(normalize-space(),' ',''),'intheMiddle')] or ./following::*[name()='h3' or name()='h4'][contains(.,'Not-so-Good') or contains(translate(.,' ',''),'NotSoGood') or contains(translate(.,' ',''),'WhatIDon')]) and not(.//*[contains(.,'in-the-Middle') or contains(translate(normalize-space(),' ',''),'intheMiddle')])]//text() | //ul/li/strong[./preceding::*[contains(translate(.,' ',''),'TheGood')] and ./following::*[contains(.,'Not-so-Good') or contains(translate(.,' ',''),'NotSoGood')]]/text() | //h4[./preceding::h3[contains(translate(.,' ',''),'TheGood')] and (./following::h3[contains(.,'in-the-Middle')] or ./following::h3[contains(translate(.,' ',''),'intheMiddle')] or ./following::h3[(contains(.,'Not-so-Good') or contains(translate(.,' ',''),'NotSoGood')) and not(.//*[contains(.,'in-the-Middle') or contains(translate(normalize-space(),' ',''),'intheMiddle')])])]//text()", cons_xpath = "//p[(./strong or ./b) and not(./text()) and ./preceding::*[name()='h3' or name()='h4'][1][contains(.,'Not-so-Good') or contains(translate(.,' ',''),'NotSoGood') or contains(translate(.,' ',''),'WhatIDon')]]//text() | //ul/li/strong[./preceding::*[contains(.,'Not-so-Good') or contains(translate(.,' ',''),'NotSoGood')] and not(./preceding::*[contains(translate(.,' ',''),'OtherNotes')])]/text() | //h3[contains(.,'Not-so-Good') or contains(translate(.,' ',''),'NotSoGood')]/following::h4[not(preceding::h3[contains(translate(.,' ',''),'OtherNotes')])]/text()", summary_xpath = "//div[@class='entry-content']//*[name()='h4' or name()='h3' or name()='h2'][1]/preceding::p[not((contains(.,'our') or contains(.,'my')) and contains(.,'review.')) and string-length(normalize-space())>1][last()]//text() | //div[@class='entry-content' and not(./descendant::*[name()='h2' or name()='h3' or name()='h4'])]/descendant::p[string-length(normalize-space())>1][1]//text()", verdict_xpath = "//*[contains(translate(.,' ',''),'Verdict') or contains(translate(.,' ',''),'FinalThoughts') or contains(translate(.,' ',''),'Finalthoughts') or contains(translate(.,' ',''),'Shouldyoubuy')]/following-sibling::p[1]//text()", author_xpath = "//span[starts-with(@class,'author')]//text()", title_xpath = "//header/h1[@class='entry-title']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [])
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/droid_life_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

