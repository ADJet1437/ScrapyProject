# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Bit_tech_netSpider", spider_type = "AlaSpider", allowed_domains = "'bit-tech.net'", start_urls = "'http://www.bit-tech.net/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//ul[@class='pageNav']/li[last()]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//ul[@class='articles']/li//h3/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@id='subNav']/ul/li[@class='active']/a//text()", category_path_xpath = "//body/@class")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//meta[@property='og:title']/@content", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "//*[starts-with(.,'Manufacturer')]/descendant-or-self::a[1]//text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//meta[@property='og:title']/@content", rating_xpath = "", date_xpath = "translate(//meta[@property='og:url']/@content,'/','-')", pros_xpath = "", cons_xpath = "", summary_xpath = "substring-after(//meta[@name='description']/@content,'. ')", verdict_xpath = "", author_xpath = "//p[@class='byline']/text()", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "((?<=-)\d{4}-\d{2}-\d{2}(?=-))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "((?<=by\s)\w.*\w)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//body/descendant-or-self::div[@class='pageSelector'][1]//optgroup[@label='Pages']/option[last()]/@value", test_verdict_xpaths = ['string(//*[starts-with(.,"Conclusion")]/following-sibling::node()[normalize-space()][1])'], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "//div[@class='award']/img/@alt", award_pic_xpath = "//div[@class='award']/img/@src")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/bit_tech_net.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

