import sys
sys.path.append(".")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "TechmagnifierSpider", spider_type = "AlaSpider", allowed_domains = "'techmagnifier.com'", start_urls = "'http://www.techmagnifier.com/review'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[@class='nextpostslink']/@href", level_index = "1")
code_fragments.append(return_code)

return_code = spa.gen_request_containers_urls(containers_xpath = "//article", url_xpath = ".//div[contains(@class, 'entry')]//a[@rel='bookmark']/@href", level_index = "2", params_xpath = {"SourceTestRating":"//img[contains(@title, 'Star')]/@src"}, params_regex = {"SourceTestRating":"/(\d+.*\d*)-stars"})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "//span[contains(@typeof, 'Breadcrumb')][1]//text()", pic_xpath = "//div[@class='productzoome']/img/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "", date_xpath = "//span[@itemprop='datePublished']/text()", pros_xpath = "//div[@class='pros']//p/text()", cons_xpath = "//div[@class='cons']//p/text()", summary_xpath = "//*[@property='og:description']/@content", verdict_xpath = "//*[@class='entry-title'][contains(text(),'Verdict')]//following-sibling::p[1]/text()", author_xpath = "//*[@class='author-name'][1]//text()", title_xpath = "//*[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "PRO")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "OriginalCategoryName", regex = "(.+) reviews")
code_fragments.append(return_code)

date_code = spa.get_testdatetext()
save_product_code = spa.save_product()
save_review_code, parse_verdict_page_code = spa.save_review()
code_fragments.extend([date_code, save_product_code, save_review_code, parse_verdict_page_code])

script_name = "./Techmagnifier.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

