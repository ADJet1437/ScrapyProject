# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Pcbrain_itSpider", spider_type = "AlaSpider", allowed_domains = "'pcbrain.it'", start_urls = "'http://pcbrain.it/index.php/articoli.html'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//ul[@class='pagination']/li[.//a[@title='Succ.']]//a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"(//div[@class='contentpaneopen'] | //ul[@class='blogsection']/li)/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"substring-before(substring-after(substring-after(//base/@href,'/articoli/'),'/'),'-')", pname_xpath = u"//meta[@name='title']/@content", ocn_xpath = u"substring-after(substring-before(substring-after(//base/@href,'/articoli/'),'/'),'-')", pic_xpath = u"//div[@class='article-content']/descendant-or-self::img[1]/@src", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"substring-before(substring-after(substring-after(//base/@href,'/articoli/'),'/'),'-')", pname_xpath = u"//meta[@name='title']/@content", rating_xpath = u"", date_xpath = u"//span[@class='createdate']//text()", pros_xpath = u"", cons_xpath = u"", summary_xpath = u"//div[@class='article-content']/p[string-length(normalize-space())>1][1]//text()", verdict_xpath = u"", author_xpath = u"//span[@class='createby']//text()", title_xpath = u"//meta[@name='title']/@content", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d+\s.+\s\d{4})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d %B %Y", languages = "it", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = u"//table[@class='contenttoc']//tr[last()]//a/@href", test_verdict_xpaths = ['//div[@class="article-content"]/p[string-length(normalize-space())>1][1]//text()'], pros_xpath = u"", cons_xpath = u"", rating_xpath = u"", award_xpath = u"//div[@class='article-content']/descendant-or-self::img[contains(@src,'award')]/@alt", award_pic_xpath = u"//div[@class='article-content']/descendant-or-self::img[contains(@src,'award')]/@src")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/pcbrain_it.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

