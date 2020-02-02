# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Dgl_ruSpider", spider_type = "AlaSpider", allowed_domains = "'dgl.ru'", start_urls = "'http://www.dgl.ru/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = u"//div[@class='pagination']//li[.//a[@class='active']]/following-sibling::li[1]//a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[@class='post-module']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"substring-before(substring-after(//meta[@itemprop='url']/@content,'_'),'.')", pname_xpath = u"//h1[@itemprop='name']//text()", ocn_xpath = u"//span[@itemprop='articleSection']//text()", pic_xpath = u"//meta[@property='og:image']/@content", manuf_xpath = u"//p//text()[string-length(normalize-space())>1 and ./preceding::text()[1][contains(.,'Производитель')]]")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"substring-before(substring-after(//meta[@itemprop='url']/@content,'_'),'.')", pname_xpath = u"//h1[@itemprop='name']//text()", rating_xpath = u"translate(concat(translate((//div[@class='aecms-cut' or @class='article-vrezka']/p//text()[string-length(normalize-space())>1 or not(string(number(normalize-space()))='NaN')][./preceding::text()[string-length(normalize-space())>1][1][(contains(.,'Оценка') or contains(.,'Итого:')) and not(./following::*[contains(.,'Оценка') or contains(.,'Итого:')])]] | //div[@class='aecms-cut']/p[(contains(.,'Оценка:') or contains(.,'Итого:')) and string-length(normalize-space(substring-after(.,':')))>1][last()] | //div[@class='aecms-cut']/p[contains(./u,' звезды')])[not(contains(.,'100')) and string(number(substring(normalize-space(),1,2)))='NaN'],',','.') , string(number(substring(substring-after(normalize-space(translate((//div[@class='aecms-cut']/p//text()[string-length(normalize-space())>1 or not(string(number(.))='NaN')][./preceding::text()[string-length(normalize-space())>1][1][(contains(.,'Оценка') or contains(.,'Итого:')) and not(./following::*[contains(.,'Оценка') or contains(.,'Итого:')])]] | //div[@class='aecms-cut']/p[(contains(.,'Оценка:') or contains(.,'Итого:')) and string-length(normalize-space(substring-after(.,':')))>1][last()] | //div[@class='aecms-cut']/p[contains(./u,' звезды')])[contains(.,'100') or not(string(number(substring(normalize-space(),1,2)))='NaN')],',','.')),' '),1,2)) div 20)),'Na','')", date_xpath = u"//span[@itemprop='datePublished']/@content", pros_xpath = u"//p[starts-with(normalize-space(),'•') and ./preceding-sibling::p[./u][1][contains(.,'Достоинства') or contains(.,'Преимущества')]]//text() | //p[string-length(normalize-space(substring-after(.,'Достоинства')))>1 or string-length(normalize-space(substring-after(.,'Преимущества')))>1]//text()[(./preceding::text()[contains(.,'Достоинства')] or ./preceding::text()[contains(.,'Преимущества')]) and string-length(normalize-space())>1] | //ul[./preceding-sibling::*[1][contains(.,'Достоинства') or contains(.,'Преимущества')]]/li//text() | //p[./preceding-sibling::*[1][normalize-space()='Достоинства' or normalize-space()='Достоинства:' or normalize-space()='Преимущества' or normalize-space()='Преимущества:']]//text()", cons_xpath = u"//p[starts-with(normalize-space(),'•') and ./preceding-sibling::p[./u][1][contains(.,'Недостатки')]]//text() | //p[string-length(normalize-space(substring-after(.,'Недостатки')))>1]//text()[./preceding::text()[contains(.,'Недостатки')] and string-length(normalize-space())>1] | //ul[./preceding-sibling::*[1][contains(.,'Недостатки')]]/li//text() | //p[./preceding-sibling::*[1][normalize-space()='Недостатки' or normalize-space()='Недостатки:']]//text()", summary_xpath = u"//div[@itemprop='articleBody']/descendant-or-self::p[string-length(normalize-space())>1][1]//text()", verdict_xpath = u"(//div[@class='article-vrezka']/p[normalize-space(./text())][1]//text() | //p//text()[./preceding::text()[1][contains(.,'Вывод') and string-length(normalize-space(substring-after(.,'Вывод')))<2]])[last()]", author_xpath = u"//div[@id='header']//a[contains(@class,'logo')]/@title", title_xpath = u"//h1[@itemprop='name']//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = u"//p//text()[string-length(normalize-space())>1 and ./preceding::text()[1][contains(.,'Цена')]]", id_kind = "Price")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductManufacturer", regex = "(\w.*\w)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\d\.\d)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\d\b)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\d(?=\s|\/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/dgl_ru.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

