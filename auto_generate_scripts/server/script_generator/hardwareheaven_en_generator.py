# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Hardwareheaven_enSpider", spider_type = "AlaSpider", allowed_domains = "'hardwareheaven.com'", start_urls = "'http://www.hardwareheaven.com/cat/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h2[@class='title title20']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pagination']//a[last()-1]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='breadcrumbs']/a[@rel='category tag'][last()]/text()", category_path_xpath = "//div[@class='breadcrumbs']//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//span[@itemprop='itemReviewed']/text() | //h1/span[@itemprop='name']//text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//span[@itemprop='itemReviewed']/text() | //h1/span[@itemprop='name']//text()", rating_xpath = "count(//span[@class='star-img']/img[contains(@src,'1star')])", date_xpath = "(//div[@class='snippet-data']/time/text() | //time//span/@datetime)[1]", pros_xpath = "", cons_xpath = "", summary_xpath = "(( //p[contains(.,'Summary')]//text() | //div[@class='single-post-ad']/following-sibling::p[text()][1]//text())[1] | //div[@class='single-post-content']//p[text()][1]//text())", verdict_xpath = "", author_xpath = "//div[@class='snippet-data']/span[@itemprop='name']/text() | //span[@itemprop='author']/a[@rel='author']/text()", title_xpath = "//h1[contains(@class,'title')]/span[@itemprop='name']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[@class='page-links']//a[last()]/@href", test_verdict_xpaths = ['//*[contains(.,"Conclusion")]/following-sibling::p[text()][1]//text()'], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/hardwareheaven_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

