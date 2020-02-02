# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Toptenreviews_comSpider", spider_type = "AlaSpider", allowed_domains = "'toptenreviews.com'", start_urls = "'http://www.toptenreviews.com/software/','http://www.toptenreviews.com/mobile/','http://www.toptenreviews.com/health/','http://www.toptenreviews.com/electronics/','http://www.toptenreviews.com/computers/','http://www.toptenreviews.com/home/','http://www.toptenreviews.com/outdoor/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[contains(@class,'all-reviews')]//li//a[not(contains(@href,'/toys/') or contains(@href,'/camping/'))]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[@id='mtx_holder']//div[contains(@class,'reviewLink')]/a/@href", level_index = "3", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = u"//ol[@itemprop='breadcrumb']/li[.//a][last()]//a//text()", category_path_xpath = u"//ol[@itemprop='breadcrumb']/li[.//a]//a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"//div[@class='article_content']/descendant-or-self::*[./@data-product-id][1]/@data-product-id", pname_xpath = u"normalize-space(//h1)", ocn_xpath = u"//ol[@itemprop='breadcrumb']/li[.//a]//a//text()", pic_xpath = u"//article/descendant-or-self::div[@class='img_cont'][1]/img/@src", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"//div[@class='article_content']/descendant-or-self::*[./@data-product-id][1]/@data-product-id", pname_xpath = u"normalize-space(//h1)", rating_xpath = u"//div[@itemprop='reviewRating']//span[@itemprop='ratingValue']//text()", date_xpath = u"//*[@itemprop='datePublished']/@content", pros_xpath = u"//p[.//*[contains(@class,'_pro')]]/text()", cons_xpath = u"//p[.//*[contains(@class,'_con')]]/text()", summary_xpath = u"//*[@id='review_summary']//p//text() | //div[@class='article_content' and not(//*[@id='review_summary']//p)]/p[string-length(normalize-space())>1][1]//text()", verdict_xpath = u"//p[.//*[contains(@class,'verdict')]]/text()", author_xpath = u"//span[@itemprop='author']//text() | //meta[@property='og:site_name' and not(//span[@itemprop='author'])]/@content", title_xpath = u"normalize-space(//h1)", award_xpath = u"//article/descendant-or-self::div[@class='award_badge'][1]//img/@alt", awpic_xpath = u"//article/descendant-or-self::div[@class='award_badge'][1]//img/@src")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/toptenreviews_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

