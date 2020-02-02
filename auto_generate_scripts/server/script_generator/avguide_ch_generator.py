# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Avguide_chSpider", spider_type = "AlaSpider", allowed_domains = "'avguide.ch'", start_urls = "'http://www.avguide.ch/testberichte'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pagingTabsCarrousel']/div[last()]/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='boxcorner']//a[starts-with(@href,'/testbericht/') and img]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//head/title/text()", ocn_xpath = "//meta[@name='Keywords']/@content", pic_xpath = "//div[@class='article']/img/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//head/title/text()", rating_xpath = "", date_xpath = "//div[@class='articlebox-content']/div[5]/text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[@class='boxcorner']/div[2]/div/h3/text()", verdict_xpath = "", author_xpath = "//meta[@itemprop='creator accountablePerson']/@content", title_xpath = "//head/title/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d. %B %Y", languages = "de", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[@id='chapterbox']/div[1]/div[contains (@class,'kapitel')][last()]/a/@href", test_verdict_xpaths = ['//div[@class="article"]//*[contains (*,"Fazit")]/descendant-or-self::p[text()][1]/text()[1]'], pros_xpath = "//div[contains (.,'STECKBRIEF')]/following-sibling::div[@class='content']/div[contains (.,'Pro:')][1]/following-sibling::div[1]/text()", cons_xpath = "//div[contains (.,'STECKBRIEF')]/following-sibling::div[@class='content']/div[contains (.,'Contra:')][1]/following-sibling::div[1]/text()", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/avguide_ch.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

