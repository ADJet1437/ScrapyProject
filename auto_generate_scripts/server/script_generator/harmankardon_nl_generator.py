import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Harmankardon_nlSpider", spider_type = "AlaSpider", allowed_domains = "'harmankardon.nl', 'bazaarvoice.com'", start_urls = "'http://www.harmankardon.nl/sitemap'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@id='primary']//ul/li/a[not(contains(@href, 'sale'))]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//a[@class='thumb-link']/@href", level_index = "3", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='product-row']//div[1]/a[@class='inline-button more']/@href", level_index = "3", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='breadcrumb']//div[a][last()]//span/text()", category_path_xpath = "//div[@class='breadcrumb']//div[a]//span/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//span[@itemprop='mpn']//text()", pname_xpath = "//h1[@class='product-name']/text()", ocn_xpath = "", pic_xpath = "//img[@itemprop='image']/@src", manuf_xpath = "harmankardon")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = "", id_kind = "mpn")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/harmankardon_nl.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

