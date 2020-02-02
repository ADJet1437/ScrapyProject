# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Frandroid_comSpider", spider_type = "AlaSpider", allowed_domains = "'frandroid.com'", start_urls = "'http://www.frandroid.com/test'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[starts-with(@class,'newer')]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[contains(@class,'bloc-wrapper')]/a/@href", level_index = "2", url_regex = "(\w.*(test).*)", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='breadcrumb']/ul/li[position()=last()-2]/a/text() | //span[contains(@typeof,'Breadcrumb')]/*[last()]/text()", category_path_xpath = "//div[@class='breadcrumb']/ul/li[position()<last()-1]/a/text() | //span[contains(@typeof,'Breadcrumb')]//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//div[starts-with(@class,'bg-content')]/div/@data-single-post-id", pname_xpath = "(//head/meta[@itemprop='itemreviewed']/@content | //h1[contains(@class,'title')]/text())[1]", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "//*[starts-with(@class,'after-content')]//a[@class='brand']//text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//div[starts-with(@class,'bg-content')]/div/@data-single-post-id", pname_xpath = "(//head/meta[@itemprop='itemreviewed']/@content | //h1[contains(@class,'title')]/text())[1]", rating_xpath = "(//span[contains(@class,'rate-frandroid')]/text() | //div[starts-with(@class,'global-grade')]/div[@class='grade']//descendant-or-self::span[last()]/text() | //div[starts-with(@class,'article-content')]//span[@class='rank-value' and not(./preceding::canvas[1]/@data-rankvalue='0')]/text())[1]", date_xpath = "substring-before(//meta[contains(@property,'published_time')]/@content,'T')", pros_xpath = "//ul[starts-with(@class,'good-bad-container')]/li[starts-with(@class,'good')]/ul/li/text()", cons_xpath = "//ul[starts-with(@class,'good-bad-container')]/li[starts-with(@class,'bad')]/ul/li/text()", summary_xpath = "//div[@itemprop='reviewBody' or @itemprop='articleBody']/p[string-length(normalize-space())>1][1]//text()", verdict_xpath = "//div[@class='conclusion']/span[@itemprop='description']/descendant::node()[string-length(normalize-space())>1][1] | //span[@id='conclusion']/following::p[1]//text()", author_xpath = "(//meta[@name='author']/@content | //span[@class='author']//text())[1]", title_xpath = "//h1[contains(@class,'title')]/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = "(//a[@class='buy-button']/span[last()]//text() | //div[starts-with(@class,'product-info')]//div[@class='offers']/a[1]/span[@class='offer']/span[last()]/text())[1]", id_kind = "price")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\d+(?=\/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/frandroid_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

