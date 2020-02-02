import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "DellSpider", spider_type = "AlaSpider", allowed_domains = "'dell.com'", start_urls = "'http://www.dell.com/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[contains(@class,'main-nav-section')][1]/ul[@class='tier1']/li[1]//a[@href!='#']/@href", level_index = "2", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//a[@class='title'][@href!='#']/@href", level_index = "3", url_regex = "")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "3")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//div[@class='breadCrumb']//li[a][last()]/a/text()", category_path_xpath = "//div[@class='breadCrumb']//a/text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//*[@id='mastheadPageTitle']/text()", ocn_xpath = "", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "//a[@class='mhLogo']/img/@alt")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//noscript/iframe/@src", level_index = "4", url_regex = "", product_fields = ['ProductName'])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "4")
code_fragments.append(return_code)

return_code = spa.gen_containers_review(containers_xpath = "//div[@id='BVSubmissionPopupContainer']", button_next_javascript = "no", button_next_xpath = "//span[@class='BVRRPageLink BVRRNextPage']/a/@href", sii_xpath = "", pname_xpath = "", rating_xpath = ".//div[@class='BVRRReviewDisplayStyle3Summary']//div[@class='BVRROverallRatingContainer']//img/@alt", date_xpath = ".//span[@class='BVRRValue BVRRReviewDate']//text()", pros_xpath = ".//span[@class='BVRRLabel BVRRTagsPrefix'][contains(text(),'Pros:')]/following-sibling::span//text()", cons_xpath = ".//span[@class='BVRRLabel BVRRTagsPrefix'][contains(text(),'Cons:')]/following-sibling::span//text()", summary_xpath = ".//span[@class='BVRRReviewText']//text()", verdict_xpath = "", author_xpath = ".//span[@class='BVRRNickname']//text()", title_xpath = ".//span[@class='BVRRValue BVRRReviewTitle']//text()", award_xpath = "//div[@class='iconographyContainer']//img/@alt", awpic_xpath = "//div[@class='iconographyContainer']//img/@src")

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "user")
code_fragments.append(return_code)

return_code = spa.get_testdatetext(replace_words = [], format_string = "%B %d, %Y", languages = "en", review_type = "user")

code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "user")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "SourceTestRating", regex = "(\d.*\d*) / 5", review_type = "user")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "user")
code_fragments.append(return_code)

script_name = "/home/carter/alaScrapy/alascrapy/spiders/dell.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

