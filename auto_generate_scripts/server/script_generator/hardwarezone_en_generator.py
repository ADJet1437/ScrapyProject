# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Hardwarezone_enSpider", spider_type = "AlaSpider", allowed_domains = "'hardwarezone.com.sg'", start_urls = "'http://www.hardwarezone.com.sg/product-guide/all/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@id='reviews-coverage']//h3/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='inner']/div[@class='paginate'][1]/ul/li/a[@class='next-page']/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//meta[@property='og:title']/@content", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//meta[@property='og:title']/@content", rating_xpath = "//meta[@itemprop='ratingvalue']/@content", date_xpath = "//span[@itemprop='datePublished']/text()", pros_xpath = "//div[contains(text(),'The Good')]/following-sibling::div/text()", cons_xpath = "//div[contains(text(),'The Bad')]/following-sibling::div/text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "", author_xpath = "//span[@class='author']/text()", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "on (.*)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d %M %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[contains(@class,'resizeable')]/following-sibling::div[@class='paginate_article']//div[contains(@class,'jumplist')]//a[contains(@href,'conclusion')]/@href", test_verdict_xpaths = ['//h3[contains(text(),"Conclusion")]/following-sibling::p[contains(./descendant-or-self::*," ")][1]/text()' , '//h3[contains(text(),"Conclusion")]/following-sibling::p[text()][1]' , '//div/div[@itemprop="reviewBody"]/p[last()]//text()'], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/hardwarezone_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

