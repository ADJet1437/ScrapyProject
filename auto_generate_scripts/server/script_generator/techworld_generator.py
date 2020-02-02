import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "TechworldSpider", spider_type = "AlaSpider", allowed_domains = "'techworld.com'", start_urls = "'http://www.techworld.com/review/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h2[@class='headline']//a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[@title='Next Page']/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//li[@property='itemListElement'][last()-1]//span[@property]/text()", category_path_xpath = "//li[@property='itemListElement'][a]//span//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//li[@property='itemListElement'][last()]//span[@property]/text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "", date_xpath = "//time/@datetime", pros_xpath = "//p[strong[text()='Pro:']]/text()", cons_xpath = "//p[strong[text()='Con:']]/text()", summary_xpath = "//h3[@class='description']/text()", verdict_xpath = "", author_xpath = "//span[@itemprop='author']//text()", title_xpath = "//h1/text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "Author", regex = "By\\s(.+)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%Y-%m-%dT%H:%M:%SZ", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[@class='pages']//ul//li[last()]//a/@href", test_verdict_xpaths = ['//section[@class="reviewVerdict"]//p/text()'], pros_xpath = "", cons_xpath = "", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "PRO")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/techworld.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

