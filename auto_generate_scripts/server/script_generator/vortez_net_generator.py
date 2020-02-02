# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Vortez_netSpider", spider_type = "AlaSpider", allowed_domains = "'vortez.net'", start_urls = "'http://www.vortez.net/articles_categories/cpusandmotherboards.html','http://www.vortez.net/articles_categories/memory.html','http://www.vortez.net/articles_categories/graphics.html','http://www.vortez.net/articles_categories/cooling.html','http://www.vortez.net/articles_categories/cases_and_psu.html','http://www.vortez.net/articles_categories/storage.html','http://www.vortez.net/articles_categories/peripherals.html','http://www.vortez.net/articles_categories/audio.html','http://www.vortez.net/articles_categories/full_systems.html','http://www.vortez.net/articles_categories/misc.html','http://www.vortez.net/articles_categories/games.html'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//div[contains(@class,'the-article-content')]/span[@class='pagelinkselected'][1]/following-sibling::span[1]//a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//h1/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"//div[@class='article-icons']//@data-disqus-identifier", pname_xpath = u"//div[contains(@class,'the-article-title')]//h2//text() | //div[@id='content']//h1//text()", ocn_xpath = u"//ul[translate(@rel,' ','')='MainMenu']/li/a[contains(@href,'articles/')]//text()", pic_xpath = u"//div[@align='justify']//div[contains(@style,'center')]//img/@src", manuf_xpath = u"//div[@align='justify']/a[./preceding-sibling::*[string-length(normalize-space())>1][1][normalize-space()='Manufacturer']]//text()")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"//div[@class='article-icons']//@data-disqus-identifier", pname_xpath = u"//div[contains(@class,'the-article-title')]//h2//text() | //div[@id='content']//h1//text()", rating_xpath = u"", date_xpath = u"normalize-space(//div[@class='article-icons'])", pros_xpath = u"", cons_xpath = u"", summary_xpath = u"//meta[@name='description']/@content", verdict_xpath = u"", author_xpath = u"concat(substring-after(//div[@class='article-icons']//text()[starts-with(normalize-space(),'by ')],'by'),substring-before(substring-after(//base[not(//div[@class='article-icons']//text()[starts-with(normalize-space(),'by ')])]/@href,'www.'),'/'))", title_xpath = u"//div[contains(@class,'the-article-title')]//h2//text() | //div[@id='content']//h1//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = u"//div[@align='justify']//text()[./preceding-sibling::*[1][translate(.,' ','')='StreetPrice']]", id_kind = "Price")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "(\d{2}\-\d{2}\-\d{2})", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d-%m-%y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = u"//div[contains(@class,'the-article-content')]//span[@class='pagelink' and ./a][last()]/a/@href", test_verdict_xpaths = ['//div[contains(@class,"main-content")]/descendant-or-self::div[@class="the-article-content"][1]/*[normalize-space()="Conclusion" or starts-with(normalize-space(),"Conclu")]/following::text()[string-length(normalize-space())>1][1]'], pros_xpath = u"//div[@class='quoteblock']//text()[./preceding-sibling::*[normalize-space()='Pros' or normalize-space()='Pros:'] and not(./preceding-sibling::*[normalize-space()='Cons' or normalize-space()='Cons:'])]", cons_xpath = u"//div[@class='quoteblock']//text()[./preceding-sibling::*[normalize-space()='Cons' or normalize-space()='Cons:']]", rating_xpath = u"", award_xpath = u"translate(substring-before(substring-after(//div[contains(@class,'main-content')]/descendant-or-self::div[@class='the-article-content'][1]/descendant-or-self::a[contains(@href,'vortez_net_awards')]/@href,'/content_page/'),'.html'),'_',' ')", award_pic_xpath = u"//div[contains(@class,'main-content')]/descendant-or-self::div[@class='the-article-content'][1]/descendant-or-self::img[contains(@src,'award')]/@src")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/vortez_net.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

