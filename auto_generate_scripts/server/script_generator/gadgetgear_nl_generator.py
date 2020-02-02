import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Gadgetgear_nlSpider", spider_type = "AlaSpider", allowed_domains = "'gadgetgear.nl'", start_urls = "'http://www.gadgetgear.nl/tag/review/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h2[contains(@class,'biglink')]//a[contains(text(),'Review:')]//@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//h2[contains(@class,'biglink')]//a[contains(text(),'Volgende pagina')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//p[@class='link']//a[@title][last()-1]//text()", category_path_xpath = "//p[@class='link']//a[@title]//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "//p[@class='link']//a[@title]//text()", pic_xpath = "//article//h1/../img/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "//span[@itemprop='ratingValue']//text()", date_xpath = "//span[@itemprop='datePublished']//text()", pros_xpath = "//div[@class='col-md-8']//ul[position()=1]//li//text()", cons_xpath = "//div[@class='col-md-8']//ul[position()=2]//li//text()", summary_xpath = "//span[@itemprop='reviewBody']//div//p[1]//text()|//div[@class='mainContent']/p[1]//text()", verdict_xpath = "//h2[text()='Conclusie']//following-sibling::p[1]//text()", author_xpath = "//span[@itemprop='author']//span[@itemprop='name']//text()", title_xpath = "//article//h1//text()", award_xpath = "//div[@class='col-md-4']//img//@alt", awpic_xpath = "//div[@class='col-md-4']//img//@src")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = ['REVIEW: '])
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "TestDateText", regex = "\w+ (.+)", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%d %B %Y", languages = "nl", review_type = "pro")

code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/gadgetgear_nl.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

