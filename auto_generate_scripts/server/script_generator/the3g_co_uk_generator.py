# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "The3g_co_ukSpider", spider_type = "AlaSpider", allowed_domains = "'3g.co.uk'", start_urls = "'https://3g.co.uk/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "concat('/reviews',//div[@class='pagination']/a[@class='next']/@href)", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[contains(@class,'story')]/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[contains(@class,'crumb')]/descendant-or-self::a[last()]//text()[normalize-space()]", category_path_xpath = "//div[contains(@class,'crumb')]//a//text()[normalize-space()]")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1//text()", ocn_xpath = "//div[contains(@class,'crumb')]//a//text()[normalize-space()]", pic_xpath = "//div[contains(@class,'reviewImage')]/img/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1//text()", rating_xpath = "substring-before(normalize-space(substring-after(substring-after(//div[contains(@class,'blogRowWrapper')]/script,'ratingValue'),':')),' ')", date_xpath = "substring-before(normalize-space(substring-after(substring-after(//div[contains(@class,'blogRowWrapper')]/script,'datePublished'),':')),',')", pros_xpath = "//table[(.//text()[normalize-space()='Pros'] or .//text()[normalize-space()='Pros:'])and (.//text()[normalize-space()='Cons'] or .//text()[normalize-space()='Cons:'])]//tr/td[starts-with(normalize-space(),'+')]//text() | //div[@class='reviewSummary']/p[contains(normalize-space(),'Pros:') or contains(normalize-space(),'Pros ')]/text()[./preceding::*[string-length(normalize-space())>1][1][contains(.,'Pros')]] | //div[@class='reviewSummary']//*[name()='h2' or name()='h3' or (./strong and not(./text()))][contains(.,'Pro')]/following-sibling::p[string-length(normalize-space())>1][1]//text() | //div[@class='reviewSummary']/p[starts-with(normalize-space(./text()),'Pros:') or starts-with(normalize-space(./text()),'Pros :') and string-length(normalize-space(substring-after(normalize-space(),':')))>1]//text()", cons_xpath = "//table[(.//text()[normalize-space()='Pros'] or .//text()[normalize-space()='Pros:'])and (.//text()[normalize-space()='Cons'] or .//text()[normalize-space()='Cons:'])]//tr/td[starts-with(normalize-space(),'-')]//text() | //div[@class='reviewSummary']/p[contains(normalize-space(),'Cons:') or contains(normalize-space(),'Cons ')]/text()[./preceding::*[string-length(normalize-space())>1][1][contains(.,'Cons')]] | //div[@class='reviewSummary']//*[name()='h2' or name()='h3' or (./strong and not(./text()))][contains(.,'Con')]/following-sibling::p[string-length(normalize-space())>1][1]//text() | //div[@class='reviewSummary']/p[starts-with(normalize-space(./text()),'Cons:') or starts-with(normalize-space(./text()),'Cons :') and string-length(normalize-space(substring-after(normalize-space(),':')))>1]//text()", summary_xpath = "//div[@class='reviewSummary']//*[contains(.,'Verdict') or contains(.,'Conclusion') or contains(translate(.,' ',''),'Theverdict')]/following-sibling::p[string-length(normalize-space())>1][1]//text() | //div[@class='reviewSummary']//p[contains(.,'erdict') or contains(.,'ERDICT')][last()]//text()[not(normalize-space()='Verdict' or normalize-space()='Verdict:' or normalize-space()='VERDICT' or normalize-space()='VERDICT:') and ./preceding::text()[contains(.,'erdict') or contains(.,'ERDICT')]][string-length(normalize-space())>1] | //div[@id='tab1' and not(normalize-space(//div[@class='reviewSummary']))]/p[string-length(normalize-space(./text()))>1][1]//text() | //div[@class='reviewSummary']/p[string-length(normalize-space(substring-after(normalize-space(./text()),'Verdict:')))>1 or string-length(normalize-space(substring-after(normalize-space(./text()),'Verdict :')))>1]//text()", verdict_xpath = "normalize-space(//div[contains(@class,'content')]/*[contains(.,'erdict') or contains(.,'onclusion')]/following::p[string-length(normalize-space())>1][1])", author_xpath = "substring-before(normalize-space(substring-after(substring-after(normalize-space(substring-after(substring-after(//div[contains(@class,'blogRowWrapper')]/script,'author'),':')),'name'),':')),'}')", title_xpath = "//h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestSummary", regex = "(\w[^\:]*[\w|\.|\?])", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\d.*\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d.*\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "(\w.*\w)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/the3g_co_uk.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

