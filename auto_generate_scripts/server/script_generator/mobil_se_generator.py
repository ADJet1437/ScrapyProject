# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Mobil_seSpider", spider_type = "AlaSpider", allowed_domains = "'mobil.se'", start_urls = "'http://www.mobil.se/tester','http://www.mobil.se/appar'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@id='mini-panel-main_teasers']//h2[@class='field-content']/a[1]/@href | //div[@class='kol1']//h2/a[1]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//ul[@class='pager']//li[@class='pager-next']/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//span[contains(@class,'views-label')][contains(text(),'Namn:')]/following::span[1][@class='field-content']//text()", ocn_xpath = "//link[@rel='canonical']/@href", pic_xpath = "//ul[@class='fancybox-gallery']//img/@src | //div[@class='pane-content']/h2[count(//ul[@class='fancybox-gallery']//img)=0]/following::img[1]/@src", manuf_xpath = "//span[contains(@class,'views-label')][contains(text(),'Utvecklare:')]/following::div[@class='field-content'][1]//text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//div[@class='pane-content']/h2//text()", rating_xpath = "//span[contains(@class,'views-label')][contains(text(),'Betyg')]/following::span[1][@class='grade-text']//text()", date_xpath = "//h2[contains(.//text(),'Publicerad')]/following::div[1][@class='pane-content']//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[@id='col-1']/div[contains(@class,'lead')]//div[contains(@class, 'field-item')]/text()", verdict_xpath = "(//div[@property='content:encoded']//p[string-length(.//text())>2][last()])[last()]//text()", author_xpath = "//span[@class='author-name']//text()", title_xpath = "//div[@class='pane-content']/h2//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "OriginalCategoryName", regex = "((?<=mobil.se/).*?(?=/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(.*(?=/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [])
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(.*(?=-))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d %b %Y", languages = "nl", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/mobil_se.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

