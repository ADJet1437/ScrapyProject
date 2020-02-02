# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Gearburn_enSpider", spider_type = "AlaSpider", allowed_domains = "'gearburn.com'", start_urls = "'http://gearburn.com/category/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//ul[@class='archive-list']//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[contains(text(),'Next')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//div[contains(@class,'headline')]/h1/text()", ocn_xpath = "//div[@id='crumbs']/a/text()", pic_xpath = "//meta[@property='og:image'][1]/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//div[contains(@class,'headline')]/h1/text()", rating_xpath = "//*[*[text()='Score:' or text()='Score' or text()='Score: ']][last()]/text()", date_xpath = "//meta[@property='article:published_time']/@content", pros_xpath = "//*[contains(text(),'Positives')]/following-sibling::*[1]/*/text() | //*[*[contains(text(),'Positives')]]/following-sibling::*[1]/*/text()", cons_xpath = "//*[contains(text(),'Negatives')]/following-sibling::*[1]/*/text() | //*[*[contains(text(),'Negatives')]]/following-sibling::*[1]/*/text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "//*[*[contains(text(),'Verdict') or contains(text(),'Nutshell')]]/text() | //p[contains(text(),'Verdict')]/text() | //*[*[contains(text(),'Verdict')]]/following-sibling::*[1]/text()", author_xpath = "//span[@class='post-byline']/a[@rel='author']/text()", title_xpath = "//div[@class='story-headline']/h1/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = ":*(.*)/10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%Y-%m-%dT%I:%M:%S%z", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/gearburn_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

