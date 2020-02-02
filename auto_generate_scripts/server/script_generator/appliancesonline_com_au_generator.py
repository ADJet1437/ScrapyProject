import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Appliancesonline_com_auSpider", spider_type = "AlaSpider", allowed_domains = "'appliancesonline.com.au'", start_urls = "'https://www.appliancesonline.com.au/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//a[@class='sub-item-link']/@href", level_index = "2", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='catPageTiles']//a[@selenium][contains(@title, 'All')]/@href", level_index = "3", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='pages'][last()]//a[img[@title='Next Page']]/@href", level_index = "3", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[@class='product-title-block']/a/@href", level_index = "4", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "4")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//ul[contains(@class, 'breadcrumbs')]//li[@itemprop][last()]//text()", category_path_xpath = "//ul[contains(@class, 'breadcrumbs')]//li[a]//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//script[contains(text(), 'ProductSKU')]/text()", pname_xpath = "//section[@class='product-section']//span[@itemprop='name']/text()", ocn_xpath = "", pic_xpath = "//img[contains(@class, 'media-gallery-main-image')]/@src", manuf_xpath = "//span[@class='product-section-manufacturer-logo']/a/@href")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "'ProductSKU': '(\w+)',", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "ProductManufacturer", regex = "/(\w+)/", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_product_id(id_value_xpath = "", id_kind = "sku")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.click(target_xpath = "//ul[@class='tabs']//span[text()='Reviews']", wait_for_xpath = "//li[contains(@class, 'review-item')]", wait_type = "presence_of_all_elements_located")
code_fragments.append(return_code)

return_code = spa.gen_containers_review(containers_xpath = "//li[contains(@class, 'review-item')]", button_next_javascript = "yes", button_next_xpath = "//button[contains(@class, 'load-more-button')]", sii_xpath = "//script[contains(text(), 'ProductSKU')]/text()", pname_xpath = "//section[@class='product-section']//span[@itemprop='name']/text()", rating_xpath = ".//span[@itemprop='ratingValue']/text()", date_xpath = ".//span[contains(@class, 'author-post-time')]/text()", pros_xpath = "", cons_xpath = "", summary_xpath = ".//p[contains(@class, 'review-text')]/text()", verdict_xpath = "", author_xpath = ".//span[contains(@class, 'author-name')]/text()", title_xpath = ".//h4[contains(@class, 'review-title')]/a/text()", award_xpath = "", awpic_xpath = "")

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "user")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/appliancesonline_com_au.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

