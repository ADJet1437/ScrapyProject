# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Mobizmag_noSpider", spider_type = "AlaSpider", allowed_domains = "'mobizmag.no'", start_urls = "'http://www.mobizmag.no/kategori/tester/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h2[@class='entry-title']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[contains(@class,'masonry-load-more')]/a/@data-link", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "'mobizmag.no'", pic_xpath = "//div[contains(@class,'page-header-image-single')]/img/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "(//text()[contains(.,'Rating:')][last()])[position()=last()]", date_xpath = "//span[@class='posted-on']//time[@itemprop='datePublished']/@datetime", pros_xpath = "//p[strong[contains(text(),'Positivt') or contains(text(),'Pluss')]][(count(following-sibling::ul))>=1]/following::ul[1]//li//text() | //p[strong[contains(text(),'Positivt') or contains(text(),'Pluss')]][(count(following-sibling::ul))=0]/text()", cons_xpath = "//p[strong[contains(text(),'Negativt') or contains(text(),'Minus')]][(count(following-sibling::ul))>=1]/following::ul[1]//li//text() | //p[strong[contains(text(),'Negativt') or contains(text(),'Minus')]][(count(following-sibling::ul))=0]/text()", summary_xpath = "(//h1[@class='entry-title']/following::h3[text()][1] | //h1[@class='entry-title']/following::p[text()][1] | //h1[@class='entry-title']/following::h2[text()][1] | //h1[@class='entry-title']/following::h4[.//text()][1])[1]//text()", verdict_xpath = "//*[starts-with(.//text(),'Konklusjon')][count(//*[starts-with(.//text(),'Konklusjon')][count(node())>1])=0][count(node())=1]/following::p[string-length(.//text())>2][1]//text() | //*[starts-with(.//text(),'Konklusjon')][count(node())>1]/text()", author_xpath = "//span[@class='author-name']//text()", title_xpath = "//h1[@class='entry-title']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "((?<=Rating:).*(?=/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "6", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['TEST:'])
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d{4}-\d{2}-\d{2})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/mobizmag_no.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

