# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Mobilegeeks_deSpider", spider_type = "AlaSpider", allowed_domains = "'mobilegeeks.de'", start_urls = "'https://www.mobilegeeks.de/test/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='article-info']//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='wp-pagenavi']//a[@class='nextpostslink']/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='breadcrumbs']//div[last()]//a//text()", category_path_xpath = "//div[@class='breadcrumbs']//a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "translate(//link[@rel='canonical']/@href,'-',' ')", ocn_xpath = "//div[@class='breadcrumbs']//a//text()", pic_xpath = "//div[@class='billboard-image']//img/@src | //div[contains(@class,'main-top')]//span[@class='author'][count(//div[@class='billboard-image']//img)=0]/following::img[1]/@src", manuf_xpath = "//div/div[@class='category-top-list'][position()=2]//div[@style='text']//text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "translate(//link[@rel='canonical']/@href,'-',' ')", rating_xpath = "//div[@class='meter-circle']//div[contains(@class,'editor_rating')]//text()", date_xpath = "substring(//div[contains(@class,'main-top')]//span[@class='date']//text(),5)", pros_xpath = "//div[contains(@class,'section-subtitle')][contains(text(),'Pro')]/following::*[name()='ul' or name()='ol'][1]//text()", cons_xpath = "//div[contains(@class,'section-subtitle')][contains(text(),'Kontra')]/following::*[name()='ul' or name()='ol'][1]//text()", summary_xpath = "//div[contains(@class,'main-top')]//div[contains(@class,'billboard-subtitle')]//text() | //div[contains(@class,'main-top')]//span[@class='author'][count(//div[contains(@class,'main-top')]//div[contains(@class,'billboard-subtitle')])=0]/following::p[string-length(.//text())>2][1]//text()", verdict_xpath = "//h2[contains(.//text(),'Fazit')]/following-sibling::p[string-length(.//text())>2][1]//text()", author_xpath = "//div[contains(@class,'main-top')]//span[@class='author']//a//text()", title_xpath = "//h1[contains(@class,'main-title')]//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "((?<=test/).*(?=/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "ProductName", regex = "((?<=test/).*(?=/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d. %B %Y", languages = "de", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/mobilegeeks_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

