# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Clubic_comSpider", spider_type = "AlaSpider", allowed_domains = "'clubic.com'", start_urls = "'http://www.clubic.com/guide-test-comparatif-informatique/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[./i[contains(@class,'angle-right')]]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='row']/div[starts-with(@class,'large') and .//h2]//h2/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//ul[contains(@class,'breadcrumb')]/li[last()]//text()", category_path_xpath = "//ul[contains(@class,'breadcrumb')]/li//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "substring-before(substring-after(//meta[@property='og:url']/@content,'article-'),'-')", pname_xpath = "//h1/text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "substring-before(substring-after(//meta[@property='og:url']/@content,'article-'),'-')", pname_xpath = "//h1/text()", rating_xpath = "(//div[@itemprop='reviewRating']/span[@itemprop='ratingValue' and normalize-space(@content)]/@content | //figure//span/text())[1]", date_xpath = "substring-before(//meta[contains(@property,'published_time')]/@content,'T')", pros_xpath = "//div[contains(translate(.,' ',''),'Lesplus')]/following-sibling::*[contains(@class,'txt-success')][1]//text()", cons_xpath = "//div[contains(translate(.,' ',''),'Lesmoins')]/following-sibling::*[contains(@class,'txt-alert')][1]//text()", summary_xpath = "string(//div[contains(@class,'article-container')]/node()[((name()='strong') or (not(name()) and not(../strong)) or name()='b') and string-length(normalize-space())>1 and (contains(.,'.') or contains(.,',') or contains(.,'?') or contains(.,';'))][1])", verdict_xpath = "", author_xpath = "//meta[contains(@property,'author')]/@content", title_xpath = "//h1/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[contains(@class,'summary-content')]/descendant-or-self::div[./a][last()]/a/@href", test_verdict_xpaths = ['//h2[contains(translate(.," ",""),"Notreavis") or contains(.,"Conclusion")]/following-sibling::node()[./preceding::node()[1][name()="br" or name()="h2"] and ./following-sibling::node()[1][name()="br" or name()="i"]][string-length(normalize-space())>1][last()] | //div[contains(@class,"article-container") and not(./h2) and (contains(translate(//div[contains(@class,"summary-content")]/descendant-or-self::div[./a][last()]/a/@title," ",""),"Notreavis") or contains(//div[contains(@class,"summary-content")]/descendant-or-self::div[./a][last()]/a/@title,"Conclusion"))]/node()[not(./descendant-or-self::script) and string-length(normalize-space())>1 and ./preceding::node()[1][name()="br" or name()="h2"] and ./following-sibling::node()[1][name()="br" or name()="i"]][string-length(normalize-space())>1][1]'], pros_xpath = "//div[contains(translate(.,' ',''),'Lesplus')]/following-sibling::*[contains(@class,'txt-success')][1]//text()", cons_xpath = "//div[contains(translate(.,' ',''),'Lesmoins')]/following-sibling::*[contains(@class,'txt-alert')][1]//text()", rating_xpath = "(//div[@itemprop='reviewRating']/span[@itemprop='ratingValue' and normalize-space(@content)]/@content | //figure//span/text())[1]", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/clubic_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

