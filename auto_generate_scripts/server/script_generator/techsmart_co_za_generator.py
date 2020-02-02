# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Techsmart_co_zaSpider", spider_type = "AlaSpider", allowed_domains = "'techsmart.co.za'", start_urls = "'http://techsmart.co.za/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[contains(@class,'pagination') and contains(@class,'right')]/a[1]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='article_list_item' or @class='feature_article']/a/@href", level_index = "2", url_regex = "(^(?!.*((\/movies\/)|(\/beer\/))).*$)", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@id='main_content']/descendant-or-self::div[contains(@class,'breadcrumb')][1]/a[last()]//text()", category_path_xpath = "//div[@id='main_content']/descendant-or-self::div[contains(@class,'breadcrumb')][1]/a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//*[@itemprop='itemReviewed']//text()", ocn_xpath = "", pic_xpath = "//article/descendant-or-self::img[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//*[@itemprop='itemReviewed']//text()", rating_xpath = "", date_xpath = "//span[@itemprop='dtreviewed']//text()", pros_xpath = "normalize-space(//div[contains(normalize-space(./span),'PROS')]/following-sibling::node()[string-length(normalize-space())>1 or normalize-space()='-'][1])", cons_xpath = "normalize-space(//div[contains(normalize-space(./span),'CONS')]/following-sibling::node()[string-length(normalize-space())>1 or normalize-space()='-'][1])", summary_xpath = "//meta[@name='description']/@content", verdict_xpath = "//body/descendant-or-self::p[contains(.//strong,'verdict') or contains(.//strong,'get') or contains(.//strong,'buy') or contains(.//strong,'choice') or starts-with(.//strong,'Final') or contains(.//strong,'decision') or starts-with(translate(.//strong,' ',''),'Thebest') or starts-with(translate(.//strong,' ',''),'Summingup') or contains(translate(.//strong,' ',''),'bestyet')][last()]/following-sibling::p[string-length(normalize-space())>1][1]//text()[normalize-space()]", author_xpath = "//span[@itemprop='reviewer']//text()", title_xpath = "//*[@itemprop='itemReviewed']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d %B %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/techsmart_co_za.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

