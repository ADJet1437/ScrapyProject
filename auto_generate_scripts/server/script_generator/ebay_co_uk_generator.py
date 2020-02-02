import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Ebay_co_ukSpider", spider_type = "AlaSpider", allowed_domains = "'ebay.co.uk'", start_urls = "'http://www.ebay.co.uk/rpp/electronics'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//li[@data-node-id='0']/ul/li/a[contains(@href, 'rpp')]/@href", level_index = "2", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//li[@data-node-id='0']/ul/li/a[contains(@href, 'sch')]/@href", level_index = "3", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[@class='gspr next']/@href", level_index = "3", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='mimg itmcd img']//a[@class='vip']/@href", level_index = "4", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "4", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//li[@itemprop='itemListElement'][last()]//text()", category_path_xpath = "//li[@itemprop='itemListElement']//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[@itemprop='name']/text()", ocn_xpath = "", pic_xpath = "//img[@itemprop='image']/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = "//td[contains(text(), 'MPN')]/following-sibling::td[1]/span/text()", id_kind = "mpn")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = "//td[contains(text(), 'EAN')]/following-sibling::td[1]/span/text()", id_kind = "ean")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@id='rwid']//a[@class='btn btn-ter right']/@href", level_index = "5", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "5", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_containers_review(containers_xpath = "//div[@itemprop='review']", button_next_javascript = "no", button_next_xpath = "//a[@rel='next']/@href", sii_xpath = "", pname_xpath = "//h1[@itemprop='name']/a/text()", rating_xpath = ".//span[@class='star-rating']/@aria-label", date_xpath = ".//span[@class='review-item-date']/text()", pros_xpath = "", cons_xpath = "", summary_xpath = ".//p[@itemprop='reviewBody']//text()", verdict_xpath = "", author_xpath = ".//a[@class='review-item-author']/text()", title_xpath = ".//p[@itemprop='name']//text()", award_xpath = "", awpic_xpath = "")

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "user")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d %b, %Y", languages = "en", review_type = "user")

code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "user")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(.+) stars", review_type = "user")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "user")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/ebay_co_uk.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

