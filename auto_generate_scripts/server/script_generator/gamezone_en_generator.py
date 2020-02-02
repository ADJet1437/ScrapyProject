# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Gamezone_enSpider", spider_type = "AlaSpider", allowed_domains = "'gamezone.com'", start_urls = "'http://www.gamezone.com/reviews'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.click_continuous(target_xpath = "//a[@class='more-articles']", wait_for_xpath = "", wait_type = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='article-stream-container']//a[img[@class=' article_wrap']]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1/span[@itemprop='itemreviewed']/text()", ocn_xpath = "game", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1/span[@itemprop='itemreviewed']/text()", rating_xpath = "//meta[@itemprop='rating']/@content", date_xpath = "//div[@class='meta-time']/text()", pros_xpath = "", cons_xpath = "", summary_xpath = " (//div[@class='body-content']/*[contains(./descendant-or-self::*,'Introduction') or contains(./descendant-or-self::*,'The Case')]/following-sibling::*[contains(.,' ')][1]/text() | /p[@class='title']/following-sibling::p/text())[1] | //div[@class='body-content']/p[not(*)][text()][1]/text()", verdict_xpath = "", author_xpath = "//div[@class='byline']//a[@rel='nofollow']/text()", title_xpath = "//h1/span[@itemprop='itemreviewed']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%b %d, %Y at %I:%M %p", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[@class='body-content']/following-sibling::div[@class='article-pagination ']/a[last()-1]/@href", test_verdict_xpaths = ['//div[@class="body-content"]/*[contains(./descendant-or-self::*,"Verdict") or contains(./descendant-or-self::*,"Conclusion")]/following-sibling::*[not(img)][contains(.," ")][1]/text()'], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/gamezone_en.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

