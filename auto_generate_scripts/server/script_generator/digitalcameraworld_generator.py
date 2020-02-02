import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "DigitalcameraworldSpider", spider_type = "AlaSpider", allowed_domains = "'digitalcameraworld.com'", start_urls = "'http://www.digitalcameraworld.com/category/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[@class='next page-numbers']/@href", level_index = "1", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_request_containers_urls(containers_xpath = "//article", url_xpath = ".//header/h2/a/@href", level_index = "2", params_xpath = {'OriginalCategoryName':'.//small//p/a[not(contains(text(), "Reviews"))][1]//text()'}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "", rating_xpath = "//p/strong[contains(text(), 'Overall Score')]/parent::p//text()", date_xpath = "//span[@class='posted-at']//text()", pros_xpath = "", cons_xpath = "", summary_xpath = "//meta[@property='og:description']//@content", verdict_xpath = "//*[contains(text(), 'Verdict')]/following-sibling::p[1]//text()", author_xpath = "//a[@rel='author']//text()", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_productname_from_title(replace_words = [])
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "PRO")

code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "PRO")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = ".+: (\d.*\d*)/5", review_type = "PRO")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "PRO")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/digitalcameraworld.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

