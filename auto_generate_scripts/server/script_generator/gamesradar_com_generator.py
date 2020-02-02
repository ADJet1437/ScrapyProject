# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Gamesradar_comSpider", spider_type = "AlaSpider", allowed_domains = "'gamesradar.com'", start_urls = "'http://www.gamesradar.com/all-platforms/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pagination-top']//span[contains(@class,'next')]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[starts-with(@class,'listingResult')]/a[not(contains(@class,'category'))]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//*[@itemprop='itemReviewed']//text()", ocn_xpath = "string(normalize-space(concat(//td[text()='Platform']/following-sibling::td[not(//p/em[contains(.,'review')])],' ','Games',substring-before(substring-after(//p/em[contains(.,'review')],'reviewed'),'.'))))", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//*[@itemprop='itemReviewed']//text()", rating_xpath = "//meta[@itemprop='ratingValue']/@content", date_xpath = "//time[@itemprop='datePublished']/@datetime", pros_xpath = "//*[normalize-space()='Pros']/following-sibling::*/descendant-or-self::*[normalize-space()]//text()", cons_xpath = "//*[normalize-space()='Cons']/following-sibling::*/descendant-or-self::*[normalize-space()]//text()", summary_xpath = "//meta[@name='description']/@content", verdict_xpath = "//p[contains(@class,'verdict')]//text()", author_xpath = "//a[@itemprop='author']//text()", title_xpath = "//h1[starts-with(@class,'review-title')]//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [])
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d.*(?=T))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/gamesradar_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

