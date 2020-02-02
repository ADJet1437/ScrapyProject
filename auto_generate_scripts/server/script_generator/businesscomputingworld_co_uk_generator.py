# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Businesscomputingworld_co_ukSpider", spider_type = "AlaSpider", allowed_domains = "'businesscomputingworld.co.uk'", start_urls = "'http://www.businesscomputingworld.co.uk/category/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[contains(@class,'masonry-grid-latest')]//div[@class='inner']/div[@class='post-categories']/following-sibling::a[1]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//nav[@id='post-nav']//*[contains(text(),'Older')]/../@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "'businesscomputingworld.co.uk'", pic_xpath = "(//div[@class='entry-content']/p[img or */img][1]//img/@src | //div[@class='entry-content']//li[img or */img][1]//img/@src)[1]", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "//div[@class='review-rating']/img/@src", date_xpath = "//span[@class='entry-date']//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "(//h2[contains(text(),'Summary') or *[contains(text(),'Summary')]]/following::p[string-length(text())>5][1] | //div[@class='entry-content']/p[.//text()][1])[(position()>count(//h2[contains(text(),'Summary') or *[contains(text(),'Summary')]]/following::p[string-length(text())>5][1]) and count(//h2[contains(text(),'Summary') or *[contains(text(),'Summary')]])>0) or (count(//h2[contains(text(),'Summary') or *[contains(text(),'Summary')]])=0)]//text() | //div[@class='entry-content']//h3/text()", verdict_xpath = "", author_xpath = "//span[contains(@class,'author')]/a//text()", title_xpath = "//div[@class='page-heading']//h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['REVIEW:'])
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d/%B/%Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "((?<=rating-).+(?=.png))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/businesscomputingworld_co_uk.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

