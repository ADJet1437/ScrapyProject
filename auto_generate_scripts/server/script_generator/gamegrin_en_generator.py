# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Gamegrin_enSpider", spider_type = "AlaSpider", allowed_domains = "'gamegrin.com'", start_urls = "'http://www.gamegrin.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='article__image']/a[img]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pagination']/a[text()='Next']/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[@class='splitter']/span[@itemprop='title']/text()", ocn_xpath = "game", pic_xpath = "//meta[@name='twitter:image']/@content", manuf_xpath = "//td[text()='Publisher']/following-sibling::td[1]/*/text()")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductName", regex = "(.*)Review", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1[@class='splitter']/span[@itemprop='title']/text()", rating_xpath = "//span[@itemprop='ratingValue']/text()", date_xpath = "//meta[@itemprop='datePublished']/@content", pros_xpath = "", cons_xpath = "", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "//p[@itemprop='reviewBody']/text()", author_xpath = "//div[contains(@class,'breadcrumbs')]/span/a/text()", title_xpath = "//h1[@class='splitter']/span[@itemprop='title']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/gamegrin_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

