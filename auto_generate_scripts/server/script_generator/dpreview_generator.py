import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "DpreviewSpider", spider_type = "AlaSpider", allowed_domains = "'dpreview.com'", start_urls = "'http://www.dpreview.com/reviews?category=cameras'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='name']/a/@href", level_index = "2", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//ul[@class='otherReviews']/li/a/@href", level_index = "2", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "//a[@class='mainItem']//span[contains(text(), 'Cameras')]/text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "", date_xpath = "//div[@class='metadata']//span[@class='date']/text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//meta[@property='og:description']/@content", verdict_xpath = "", author_xpath = "//div[@class='metadata']//a[@class='author'][1]/text()", title_xpath = "//div[@class='articleHeader']//h1//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [])
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = ['Published'], format_string = "", languages = "", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "100", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[@class='articleTableOfContents']//a[contains(text(), 'Conclusion') or contains(text(), 'Impressions')]/@href", test_verdict_xpaths = ['//h2[contains(text(), "conclusion") or contains(text(), "Conclusion")]//following-sibling::p[1]//text()','//h2[contains(text(), "conclusion") or contains(text(), "Conclusion")]//following-sibling::p[2]//text()','//*[contains(text(), "First Impressions")]//following-sibling::p[1]//text()','//*[contains(text(), "First Impressions")]//following-sibling::p[2]//text()'], pros_xpath = "//ul[@type='square'][1]/li//text()", cons_xpath = "//ul[@type='square'][2]/li//text()", rating_xpath = "//div[@class='score']/text()", award_xpath = "", award_pic_xpath = "//p[@align='center']/img/@src")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/dpreview.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

