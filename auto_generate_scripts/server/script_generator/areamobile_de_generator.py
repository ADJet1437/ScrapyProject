# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Areamobile_deSpider", spider_type = "AlaSpider", allowed_domains = "'areamobile.de'", start_urls = "'http://www.areamobile.de/testberichte','http://www.areamobile.de/tablets/tablet-testberichte'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//ul[contains(@class,'handyList')]/li/div[@class='data']/span[contains(@class,'ml')]/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "(//div[contains(@class,'pagination') and contains(@class,'txtR')])[last()]/span[@class='p-next']/a[@class='arrowr']/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@id='breadcrumb']/span[not(.//text()='Testbericht')][last()]//text()", category_path_xpath = "//div[@id='breadcrumb']/span//text()[not(.='Testbericht')]")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//*[@class='h1']//text()", ocn_xpath = "//div[@id='breadcrumb']/span//text()[not(.='Testbericht')]", pic_xpath = "(//div[@id='informerLogo']//img)[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//*[@class='h1']//text()", rating_xpath = "//span[@id='canvasRatingValue'][count(//div[@class='rating-result-entry']/div[contains(@class,'mbs')]/text())=0]//text()[not(.='0')] | (//div[@class='rating-result-entry']/div[contains(@class,'mbs')]/text())[1] | //div[contains(@class,'testRating') and contains(@class,'rate3')][count(//span[@id='canvasRatingValue'][count(//div[@class='rating-result-entry']/div[contains(@class,'mbs')]/text())=0]//text()[not(.='0')] | (//div[@class='rating-result-entry']/div[contains(@class,'mbs')]/text())[1])=0]/div[@class='percent']//text()", date_xpath = "(//a[@rel='author']/following::text()[string-length(.)>2][1] | //time[@datetime]//text())[1] | //text()[contains(.,'Autor')][count((//a[@rel='author']/following::text()[string-length(.)>2][1] | //time[@datetime]//text())[1])=0]/following-sibling::text()[1]", pros_xpath = "//ul[@class='topflop'][.//li[contains(.//text(),'Tops')]]/li[position()>1]//text()", cons_xpath = "//ul[@class='topflop'][.//li[contains(.//text(),'Flops')]]/li[position()>1]//text()", summary_xpath = "//p[@itemprop='description']/text()", verdict_xpath = "//h2[contains(.//text(),'Fazit')]/following::p[string-length(.//text())>2][1]//text()", author_xpath = "//text()[contains(.,'Autor')]/following::a[1]//text() | //span[@itemprop='reviewer'][count(//text()[contains(.,'Autor')]/following::a[1])=0]//text()", title_xpath = "(//h1//text()[not(translate(.,' ','')='Testbericht')])[1]", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "100", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\d*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d{2}\.\d{2}\.\d{4})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d.%b.%Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/areamobile_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

