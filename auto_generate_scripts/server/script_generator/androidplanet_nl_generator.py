# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Androidplanet_nlSpider", spider_type = "AlaSpider", allowed_domains = "'androidplanet.nl'", start_urls = "'https://www.androidplanet.nl/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//nav[@id='pagination']//a[@class='pagination-next']/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[@id='reviews']//h3/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = u"//span[contains(@*,'Breadcrumb')]/descendant-or-self::a[last()-1]//text()", category_path_xpath = u"//span[contains(@*,'Breadcrumb')]/descendant-or-self::a[position()<last()]//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"substring-after(//body/@class,'postid-')", pname_xpath = u"((//span[contains(@*,'Breadcrumb')]/descendant-or-self::a[3]//text() | //span[contains(@*,'Breadcrumb')]//span[@class='breadcrumb_last']//text())[1] | //footer[@class='more-post-meta']//li[contains(.,'Device:')]//a[1]//text())[last()]", ocn_xpath = u"//span[contains(@*,'Breadcrumb')]/descendant-or-self::a[position()<last()]//text()", pic_xpath = u"//meta[@property='og:image']/@content", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "(\d+)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"substring-after(//body/@class,'postid-')", pname_xpath = u"((//span[contains(@*,'Breadcrumb')]/descendant-or-self::a[3]//text() | //span[contains(@*,'Breadcrumb')]//span[@class='breadcrumb_last']//text())[1] | //footer[@class='more-post-meta']//li[contains(.,'Device:')]//a[1]//text())[last()]", rating_xpath = u"//div[@itemprop='reviewRating']//meta[@itemprop='ratingValue']/@content", date_xpath = u"substring-before(//meta[@property='DC.date.issued']/@content,'T')", pros_xpath = u"", cons_xpath = u"", summary_xpath = u"normalize-space(//div[@itemprop='description']/p[string-length(normalize-space())>1][1])", verdict_xpath = u"normalize-space(//*[name()='h2' or name()='h3'][contains(.,'onclusie')]/following::p[string-length(normalize-space())>1][1])", author_xpath = u"//span[@itemprop='author']//a//text()", title_xpath = u"//h1//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/androidplanet_nl.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

