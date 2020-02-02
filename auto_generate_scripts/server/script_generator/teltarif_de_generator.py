import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Teltarif_deSpider", spider_type = "AlaSpider", allowed_domains = "'teltarif.de'", start_urls = "'http://www.teltarif.de/handy/test.html'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[img[@alt='vor']]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//li[contains(@class, 'ttboxpad')]//a[contains(@class, 'extra')]/@href", level_index = "2", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@id='breadcrumb']//span[last()]//a//text()", category_path_xpath = "//div[@id='breadcrumb']//a//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "", date_xpath = "//span[@class='dateNews']/time/text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[@class='abstract']//text()", verdict_xpath = "", author_xpath = "//span[@itemprop='author']/a/text()", title_xpath = "//h1[@itemprop='name']/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [])
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d.%m.%Y %H:%M", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//a[img[@alt='letzte']]/@href", test_verdict_xpaths = ['//*[@class="shl"][contains(text(), "Fazit:")]//following-sibling::div[@class="ttsbox"][1]/following::text()[1]'], pros_xpath = "//ul[@class='ttProConUL Pro']/li//text()", cons_xpath = "//ul[@class='ttProConUL Contra']/li//text()", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/teltarif_de.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

