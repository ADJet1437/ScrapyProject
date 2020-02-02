# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Androidworld_itSpider", spider_type = "AlaSpider", allowed_domains = "'androidworld.it'", start_urls = "'http://www.androidworld.it/recensioni/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@id='pagination']/a[last()]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h2[starts-with(@class,'entry')]/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//body/@class", pname_xpath = "//h3[@itemprop='itemReviewed']/span[@itemprop='name']/text()", ocn_xpath = "//section[@id='content']/article[1]//span[@class='cat']//text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//body/@class", pname_xpath = "//h3[@itemprop='itemReviewed']/span[@itemprop='name']/text()", rating_xpath = "//div[@class='head-vote']//p/text()", date_xpath = "//meta[contains(@property,'date')]/@content", pros_xpath = "//span[starts-with(normalize-space(),'Pro')]/following-sibling::*[1]//*[text()]/text()", cons_xpath = "//span[starts-with(normalize-space(),'Contro')]/following-sibling::*[1]//*[text()]/text()", summary_xpath = "//span[@class='fix']/following-sibling::p[text()][1]//text()", verdict_xpath = "string(//*[text()=(//meta[@itemprop='ratingValue']/following-sibling::node()[not(name()) or text()[preceding-sibling::meta[@itemprop='ratingValue']]])])", author_xpath = "//span[@class='authorname']//text()", title_xpath = "//h1[@itemtype='headline']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=id-)\d*(?=\s))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=id-)\d*(?=\s))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d[^\s]*\d(?=T))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/androidworld_it.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

