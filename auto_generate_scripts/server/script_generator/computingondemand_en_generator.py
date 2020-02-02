# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Computingondemand_enSpider", spider_type = "AlaSpider", allowed_domains = "'computingondemand.com'", start_urls = "'http://computingondemand.com/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@id='masonry-grid']//a[img]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//span[@id='tie-next-page']/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@id='crumbs']/span[a][last()]/a/text()", category_path_xpath = "//div[@id='crumbs']/span[a]/a/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[@itemprop='itemReviewed']/span[@itemprop='name']/text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image'][2]/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(.*)Review", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1[@itemprop='itemReviewed']/span[@itemprop='name']/text()", rating_xpath = "//div[@class='widget-container']//div[@class='review-final-score']/h3/text()", date_xpath = "//meta[@property='article:published_time']/@content", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[@class='post-inner']/div/p[text()][1]//text() | //div[@class='post-inner']/div/p[span][1]/span//text()", verdict_xpath = "//div[@class='widget-container']//div[@itemprop='description']/p/text()", author_xpath = "//span[contains(@class,'author')]/a/text()", title_xpath = "//h1[@itemprop='itemReviewed']/span[@itemprop='name']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%Y-%m-%dT%H:%M:%S-%z", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/computingondemand_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

