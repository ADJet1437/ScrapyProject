# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Hometheaterhifi_enSpider", spider_type = "AlaSpider", allowed_domains = "'hometheaterhifi.com'", start_urls = "'http://hometheaterhifi.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@id='main']//a[img]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[contains(text(),'Load More')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='cb-breadcrumbs']//a[last()]/span/text()", category_path_xpath = "//div[@class='cb-breadcrumbs']//span/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[@itemprop='headline']/text()", ocn_xpath = "//span[contains(@class,'category')]/a/text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(.*)Review", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1[@itemprop='headline']/text()", rating_xpath = "", date_xpath = "//div[contains(@class,'header')]/div[@class='cb-byline']//span[@class='cb-date']/time/@datetime", pros_xpath = "//div[contains(text(),'Like')]/following-sibling::ul[1]/li/text() | //p[contains(text(),'Likes')]/following-sibling::ul[1]/li/text() | //p[*[contains(text(),'Likes')]]/following-sibling::ul[1]/li/text()", cons_xpath = "//div[contains(text(),'Would Like')]/following-sibling::ul[1]/li/text() | //p[contains(text(),'Dislikes')]/following-sibling::ul[1]/li/text() | //p[*[contains(text(),'Dislikes')]]/following-sibling::ul[1]/li/text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "//div[contains(text(),'Conclusions')]/following-sibling::p[1]/text() | //p[*/*[contains(text(),'Conclusion')]]/following-sibling::p[1]/text() | //div[text()='Conclusions']/following::h2/text()", author_xpath = "//div[contains(@class,'header')]/div/span[@class='cb-author']/a/text()", title_xpath = "//h1[@itemprop='headline']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/hometheaterhifi_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

