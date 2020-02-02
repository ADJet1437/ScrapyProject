# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Oxgadgets_comSpider", spider_type = "AlaSpider", allowed_domains = "'oxgadgets.com'", start_urls = "'http://www.oxgadgets.com/category/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h2[@class='entry-title']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//nav[contains(@class,'entry-nav')]//li[contains(@class,'right')]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//p[@class='entry-category']/a[last()]//text()", category_path_xpath = "//p[@class='entry-category']/a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "(//span[@itemprop='name']/h2[@itemprop='name'] | //h1[@class='entry-title'])[(position()>count(//span[@itemprop='name']/h2[@itemprop='name']) and count(//span[@itemprop='name']/h2[@itemprop='name'])>0) or count(//span[@itemprop='name']/h2[@itemprop='name'])=0]//text()", ocn_xpath = "//p[@class='entry-category']/a//text()", pic_xpath = "(//div[@class='content-part']//p[.//img][1]//img | //li[@class='entry-date'][count(//div[@class='rev-wu-image'])=0]/following::img[1])[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "(//span[@itemprop='name']/h2[@itemprop='name'] | //h1[@class='entry-title'])[(position()>count(//span[@itemprop='name']/h2[@itemprop='name']) and count(//span[@itemprop='name']/h2[@itemprop='name'])>0) or count(//span[@itemprop='name']/h2[@itemprop='name'])=0]//text()", rating_xpath = "//span[@itemprop='ratingValue']//text()", date_xpath = "//li[@class='entry-date']//text()", pros_xpath = "//h2[text()='Pros']/following::ul[1]//text()", cons_xpath = "//h2[text()='Cons']/following::ul[1]//text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "//strong[starts-with(text(),'Verdict')]/following::p[string-length(text())>5][1]//text()", author_xpath = "//li[@class='entry-author']/a//text()", title_xpath = "//h1[@class='entry-title']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['Review:'])
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/oxgadgets_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

