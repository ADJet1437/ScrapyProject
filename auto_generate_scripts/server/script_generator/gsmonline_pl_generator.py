# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Gsmonline_plSpider", spider_type = "AlaSpider", allowed_domains = "'gsmonline.pl'", start_urls = "'http://gsmonline.pl/testy?page=1'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "concat('/testy',//div[@class='pagination']/a[last()]/@href)", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='column_left_wide']//ul[contains(@id,'article_list')]/li//h4/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//*[@*='comment_commentable_id']/@value", pname_xpath = "//meta[@property='og:title']/@content", ocn_xpath = "//meta[@property='og:type']/@content", pic_xpath = "(//table[1]//td[//img][1]//a[@class='fancybox']/img/@src | //meta[@property='og:image']/@content)[last()]", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//*[@*='comment_commentable_id']/@value", pname_xpath = "//meta[@property='og:title']/@content", rating_xpath = "", date_xpath = "substring-before(normalize-space(//span[@class='article_date']//text()),' ')", pros_xpath = "//*[starts-with(normalize-space(),'Zalety') or .//text()[starts-with(normalize-space(),'Zalety')]]/following::*[string-length(normalize-space())>1][1][name()='ul']/li//text() | //*[starts-with(normalize-space(),'Zalety')]/following::*[string-length(normalize-space())>1][1][name()='p' and starts-with(normalize-space(),'+')]//text()", cons_xpath = "//*[starts-with(normalize-space(),'Wady') or .//text()[starts-with(normalize-space(),'Wady')]]/following::*[string-length(normalize-space())>1][1][name()='ul']/li//text() | //*[starts-with(normalize-space(),'Wady')]/following::*[string-length(normalize-space())>1][1][name()='p' and starts-with(normalize-space(),'-')]//text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "//*[contains(.,'Podsumowanie')]/following-sibling::p[string-length(normalize-space())>1][1]//text()", author_xpath = "//span[contains(.,'autor:')]//a//text()", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/gsmonline_pl.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

