import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Electronics_and_technologySpider", spider_type = "AlaSpider", allowed_domains = "'choice.com.au'", start_urls = "'https://www.choice.com.au/electronics-and-technology'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h4[@class='type-heading type-h3']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='tile-generalcontent-body tile-generalcontent-subcategory-body']/p/a/@href", level_index = "3", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//a[@data-link-type='Article']//@href", level_index = "4", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "4", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[contains(@class, 'menu-breadcrumbs')]//li[span/a][last()]//a/text()", category_path_xpath = "//div[contains(@class, 'menu-breadcrumbs')]//span[@id]/*/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//li//span[contains(@class,'vis-hidden-ts')]//span//text()", ocn_xpath = "", pic_xpath = "//div[contains(@class,'hero-article')]//img//@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//li//span[contains(@class,'vis-hidden-ts')]//span//text()", rating_xpath = "", date_xpath = "//span[@class='meta-item']//span//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[@itemprop='description']//p[1]//text()", verdict_xpath = "", author_xpath = "//span[@itemprop='author']//text()", title_xpath = "//h1[@itemprop='name']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d %B %Y", languages = "en", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/electronics_and_technology.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

