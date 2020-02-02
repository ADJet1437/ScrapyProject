# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Play3r_netSpider", spider_type = "AlaSpider", allowed_domains = "'play3r.net'", start_urls = "'http://www.play3r.net/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[contains(@class,'td_module_10')]//h3[contains(@class,'entry-title')]/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[contains(@class,'page-nav')]//i[contains(@class,'menu-right')]/../@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='entry-crumbs']/span[last()]//text()", category_path_xpath = "//div[@class='entry-crumbs']/span//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "//div[@class='entry-crumbs']/span//text()", pic_xpath = "//div[contains(@class,'featured-image')]//img/@src", manuf_xpath = "//div[@class='td-post-content']//*[text()=concat(substring-after(//strong[contains(text(),'Brand:') or contains(text(),'Manufacturer:')]//text(), ': '),string(//strong[contains(text(),'Brand:') or contains(text(),'Manufacturer:')]//a[1]//text()))]//text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "//span[@itemprop='review']//text()", date_xpath = "//div[contains(@class,'meta-info')]/span[1]/time[contains(@class,'entry-date')]//text()", pros_xpath = "((//p[starts-with(normalize-space(),'Pros')]/following-sibling::p[position()=1 and count(//p[starts-with(normalize-space(),'Pros')]//text())<2]//text() | //p[starts-with(normalize-space(),'Pros')]/self::p[count(//p[starts-with(normalize-space(),'Pros')]//text())>1]) | (//p[starts-with(normalize-space(),'Pros')]/following-sibling::ul[position()=1 and count(li)>1] | //p[starts-with(normalize-space(),'Pros')]/following-sibling::li[preceding-sibling::p[1][starts-with(normalize-space(),'Pros')]]))//text()", cons_xpath = "((//p[starts-with(normalize-space(),'Cons')]/following-sibling::p[position()=1 and count(//p[starts-with(normalize-space(),'Cons')]//text())<2]//text() | //p[starts-with(normalize-space(),'Cons')]/self::p[count(//p[starts-with(normalize-space(),'Cons')]//text())>1]) | (//p[starts-with(normalize-space(),'Cons')]/following-sibling::ul[position()=1 and count(li)>1] | //p[starts-with(normalize-space(),'Cons')]/following-sibling::li[preceding-sibling::p[1][starts-with(normalize-space(),'Cons')]]))//text()", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "//h2[text()='Conclusion']/following-sibling::p[1]//text()", author_xpath = "//div[contains(@class,'meta-info')]/div[contains(@class,'author-name')][1]/a//text()", title_xpath = "//h1[@class='entry-title']//text()", award_xpath = "//p[a/img[contains(@src,'award')]][1]//img/@alt", awpic_xpath = "substring-after(string(//p[a/img[contains(@src,'award')]][1]//img/@src),'//')")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [' Review'])
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%b %d, %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[contains(@class,'page-nav')]/a[last()-1]/@href", test_verdict_xpaths = ['//h2[text()="Conclusion"]/following-sibling::p[1]//text()'], pros_xpath = "((//p[starts-with(normalize-space(),'Pros')]/following-sibling::p[position()=1 and count(//p[starts-with(normalize-space(),'Pros')]//text())<2]//text() | //p[starts-with(normalize-space(),'Pros')]/self::p[count(//p[starts-with(normalize-space(),'Pros')]//text())>1]) | (//p[starts-with(normalize-space(),'Pros')]/following-sibling::ul[position()=1 and count(li)>1] | //p[starts-with(normalize-space(),'Pros')]/following-sibling::li[preceding-sibling::p[1][starts-with(normalize-space(),'Pros')]]))//text()", cons_xpath = "((//p[starts-with(normalize-space(),'Cons')]/following-sibling::p[position()=1 and count(//p[starts-with(normalize-space(),'Cons')]//text())<2]//text() | //p[starts-with(normalize-space(),'Cons')]/self::p[count(//p[starts-with(normalize-space(),'Cons')]//text())>1]) | (//p[starts-with(normalize-space(),'Cons')]/following-sibling::ul[position()=1 and count(li)>1] | //p[starts-with(normalize-space(),'Cons')]/following-sibling::li[preceding-sibling::p[1][starts-with(normalize-space(),'Cons')]]))//text()", rating_xpath = "//span[@itemprop='review']//text()", award_xpath = "(//p[a/img[contains(@src,'award')]][1]/following-sibling::p[1] | //p[a/img[contains(@src,'award')]][1]/preceding-sibling::p[1])[1]//text()", award_pic_xpath = "substring-after(string(//p[a/img[contains(@src,'award')]][1]//img/@src),'//')")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/play3r_net.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

