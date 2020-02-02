# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Macitynet_itSpider", spider_type = "AlaSpider", allowed_domains = "'macitynet.it'", start_urls = "'http://www.macitynet.it/category/macity/recensioni/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pagination']/a[last()-1]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//ul[@class='category3']/li//a[@class='main-headline']/@href | //div[@class='featured-box']//a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='breadcrumb']/descendant::a[name(..)='span' and ../@typeof][last()]//text()", category_path_xpath = "//div[@class='breadcrumb']/descendant::a[name(..)='span' and ../@typeof]//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "substring-before(substring-after(//body/@class,'postid-'),' ')", pname_xpath = "//h1/text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "substring-before(substring-after(//body/@class,'postid-'),' ')", pname_xpath = "//h1/text()", rating_xpath = "substring-after(//div[@itemprop='aggregateRating']/img/@src,'rat=')", date_xpath = "substring-before(//meta[starts-with(@property,'DC.date')]/@content,'T')", pros_xpath = "//*[(name()='p' or name()='h3' or name()='h2') and (.//text()='Pro' or .//text()='PRO' or .//text()='Pro:') and count(./node()[string-length(normalize-space())>1])=1]/following::*[(name()='p' or name()='ul') and string-length(normalize-space())>1][1]//text() | //p[.//text()='Pro' and count(./node()[string-length(normalize-space())>1])>1]/descendant-or-self::node()[normalize-space()='Pro']/following-sibling::text() | //*[name()='b' and (.//text()='Pro' or .//text()='PRO' or .//text()='Pro:') and count(./node()[string-length(normalize-space())>1])=1]/following::div[contains(./following::b[1]/text(),'Contro') or contains(./preceding::b[1]/text(),'CONTRO')]//text()", cons_xpath = "//*[(name()='p' or name()='h3' or name()='h2') and (.//text()='Contro' or .//text()='CONTRO' or .//text()='Contro:') and count(./node()[string-length(normalize-space())>1])=1]/following::*[(name()='p' or name()='ul') and string-length(normalize-space())>1][1]//text() | //p[.//text()='Contro' and count(./node()[string-length(normalize-space())>1])>1]/descendant-or-self::node()[normalize-space()='Contro']/following-sibling::text() | //div[contains(./b,'Contro') or contains(./b,'CONTRO')]/following::div[string-length(normalize-space())>1 and (contains(./preceding::b[1]/text(),'Contro') or contains(./preceding::b[1]/text(),'Contro')) and not(./b)]//text()", summary_xpath = "//span[@itemprop='articleBody']/p[(./preceding::div[starts-with(@class,'side_col')] or not(//span[@itemprop='articleBody']/div[starts-with(@class,'side_col')])) and string-length(normalize-space())>1][1]//text() | //span[@itemprop='articleBody']/div[string-length(normalize-space())>1 and not(.//script) and not(//span[@itemprop='articleBody']/p)][1]//text()", verdict_xpath = "", author_xpath = "//span[@itemprop='author']//text()", title_xpath = "//h1/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//*[@id='post-pagination']/a[last()]/@href", test_verdict_xpaths = ['//*[(name()="h2" or name()="h3" or name()="strong") and (starts-with(.//text(),"Conclusioni") or starts-with(.//text(),"Conclusione"))]/preceding::*[1]/following::p[not(count(./*[string-length(normalize-space())>1])=1 and (.//text()="Conclusioni" or .//text()="Conclusione")) and string-length(normalize-space())>1][1]//text()'], pros_xpath = "//*[(name()='p' or name()='h3' or name()='h2') and (.//text()='Pro' or .//text()='PRO' or .//text()='Pro:') and count(./node()[string-length(normalize-space())>1])=1]/following::*[(name()='p' or name()='ul') and string-length(normalize-space())>1][1]//text() | //p[.//text()='Pro' and count(./node()[string-length(normalize-space())>1])>1]/descendant-or-self::node()[normalize-space()='Pro']/following-sibling::node() | //*[name()='b' and (.//text()='Pro' or .//text()='PRO' or .//text()='Pro:') and count(./node()[string-length(normalize-space())>1])=1]/following::div[contains(./following::b[1]/text(),'Contro') or contains(./preceding::b[1]/text(),'CONTRO')]//text()", cons_xpath = "//*[(name()='p' or name()='h3' or name()='h2') and (.//text()='Contro' or .//text()='CONTRO' or .//text()='Contro:') and count(./node()[string-length(normalize-space())>1])=1]/following::*[(name()='p' or name()='ul') and string-length(normalize-space())>1][1]//text() | //p[.//text()='Contro' and count(./node()[string-length(normalize-space())>1])>1]/descendant-or-self::node()[normalize-space()='Contro']/following-sibling::node() | //div[contains(./b,'Contro') or contains(./b,'CONTRO')]/following::div[string-length(normalize-space())>1 and (contains(./preceding::b[1]/text(),'Contro') or contains(./preceding::b[1]/text(),'Contro')) and not(./b)]//text()", rating_xpath = "substring-after(//div[@itemprop='aggregateRating']/img/@src,'rat=')", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/macitynet_it.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

