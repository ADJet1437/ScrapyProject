# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Whatmobile_netSpider", spider_type = "AlaSpider", allowed_domains = "'whatmobile.net'", start_urls = "'http://www.whatmobile.net/category/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//li[@class='cpn-next-link']/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='cb-meta']/h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//p[contains(@class,'vcard')]/a[2]//text()", category_path_xpath = "//p[contains(@class,'vcard')]/a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "//p[contains(@class,'vcard')]/a//text()", pic_xpath = "(//div[@class='cb-featured-image']/img/@src|//span[@itemprop='reviewBody']/a[img][1]/img/@src|//div[@class='backstretch'][img][1]/img/@src)[1]", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "//div[@itemprop='reviewRating']//span[@itemprop='ratingValue']//text()", date_xpath = "//time[@class='updated']/@datetime", pros_xpath = "//div[@class='cb-good-summary']/ul/li//text()", cons_xpath = "//div[@class='cb-bad-summary']/ul/li//text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "(//strong[text()='VERDICT' or text()='Conclusion']/following::p[//text()][1] | //h3[text()='Verdict']/following::p[//text()][1])[1]//text()", author_xpath = "//span[@class='author']/a[@rel='author']/span//text()", title_xpath = "//h1[contains(@class,'cb-entry-title')]//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['Review- '])
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[contains(@class,'link-pages')]//a[last()]/@href", test_verdict_xpaths = ['(//strong[text()="VERDICT" or text()="Conclusion"]/following::p[//text()][1] | //h3[text()="Verdict"]/following::p[//text()][1])[1]//text()'], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/whatmobile_net.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

