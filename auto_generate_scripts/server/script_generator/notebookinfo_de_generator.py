# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Notebookinfo_deSpider", spider_type = "AlaSpider", allowed_domains = "'notebookinfo.de'", start_urls = "'http://www.notebookinfo.de/tests/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//ul[contains(@class,'pagination')]/li[contains(@class,'next')]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//article//h3/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//ol[./@*[contains(.,'crumb')]]//li[last()-1]//span//text()", category_path_xpath = "//ol[./@*[contains(.,'crumb')]]//li[position()<last()]//span//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//input[@name='id']/@value", pname_xpath = "//h1//text()", ocn_xpath = "//ol[./@*[contains(.,'crumb')]]//li[position()<last()]//span//text()", pic_xpath = "//meta[@property='og:image']/@content | //article[not(normalize-space(//meta[@property='og:image']/@content))]/descendant-or-self::img[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//input[@name='id']/@value", pname_xpath = "//h1//text()", rating_xpath = "string((5 - number(translate(//span[@itemprop='reviewRating']/meta[@itemprop='ratingValue']/@content,',','.'))) * 1.25)", date_xpath = "substring-before(//time[@itemprop='datePublished']/@datetime,'T')", pros_xpath = "", cons_xpath = "", summary_xpath = "//p[@itemprop='description']//text() | //article[@itemprop='reviewBody' and not(normalize-space(//p[@itemprop='description']))]/p[string-length(normalize-space(./text()))>1][1]//text()", verdict_xpath = "//h2[contains(.,'Fazit') or @*=Fazit]/following-sibling::p[string-length(normalize-space())>1][1]//text()", author_xpath = "//span[@itemprop='author']//a//text()", title_xpath = "//h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/notebookinfo_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

