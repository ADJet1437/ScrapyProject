# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Pcworld_enSpider", spider_type = "AlaSpider", allowed_domains = "'pcworld.com'", start_urls = "'http://www.pcworld.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.click_continuous(target_xpath = "//div[@id='reviewsCrawlLatest']//a[@class='seeMore']", wait_for_xpath = "", wait_type = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@id='reviewsCrawlLatestResults']//div[@class='excerpt-text']//a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//li[last()]//span[@itemprop='title']/text()", category_path_xpath = "//span[@itemprop='title']/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[@itemprop='name']/text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1[@itemprop='name']/text()", rating_xpath = "//div[contains(@class,'top')]//meta[@itemprop='ratingValue']/@content", date_xpath = "//li[@itemprop='datePublished']/text()", pros_xpath = "//div[@class='product-pros']//li/text()", cons_xpath = "//div[@class='product-cons']//li/text()", summary_xpath = "(//div[contains(@class,'top')]//p[@itemprop='description']/text() | //meta[@property='og:description']/@content)[last()]", verdict_xpath = "//h2[last()]/following-sibling::p[1]/text()", author_xpath = "//span[@itemprop='name']/text()", title_xpath = "//h1[@itemprop='name']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%b %d, %Y %I:%M %p", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/pcworld_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

