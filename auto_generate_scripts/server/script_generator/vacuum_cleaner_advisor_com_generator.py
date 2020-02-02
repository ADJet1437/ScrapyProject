# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Vacuum_cleaner_advisor_comSpider", spider_type = "AlaSpider", allowed_domains = "'vacuum-cleaner-advisor.com'", start_urls = "'http://vacuum-cleaner-advisor.com/Bagless-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Bagged-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Upright-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Canister-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Handheld-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Stick-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Steam-Cleaner-Reviews.html','http://vacuum-cleaner-advisor.com/HEPA-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Wet-Dry-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Cordless-Vacuum-Reviews.html','http://vacuum-cleaner-advisor.com/Allergy-Vacuum-Reviews.html'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = u"//div[@itemprop='articleBody']/div[@class='contentheading']/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = u"//ul[@class='breadcrumb']/li[.//a][last()]//a//text()[normalize-space()]", category_path_xpath = u"//ul[@class='breadcrumb']/li[.//a]//a//text()[normalize-space()]")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = u"", pname_xpath = u"//h1//text()", ocn_xpath = u"//ul[@class='breadcrumb']/li[.//a]//a//text()[normalize-space()]", pic_xpath = u"//div[@itemprop='articleBody']/p[.//img][1]//img/@src", manuf_xpath = u"")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = u"", pname_xpath = u"//h1//text()", rating_xpath = u"substring-before(//div[@itemprop='articleBody']/p[contains(translate(.,' ',''),'rating=')]/descendant-or-self::*[name()='b' or name()='strong'][1],'/')", date_xpath = u"substring-before(//time[@itemprop='datePublished']/@datetime,'T')", pros_xpath = u"//div[@itemprop='articleBody']/p[.//text()[normalize-space()='PROS']]//text()[./preceding-sibling::node()[normalize-space()='PROS']]", cons_xpath = u"//div[@itemprop='articleBody']/p[.//text()[normalize-space()='CONS']]//text()[./preceding-sibling::node()[normalize-space()='CONS']]", summary_xpath = u"//div[@itemprop='articleBody']/p[./descendant-or-self::text()[string-length(normalize-space())>1][last()][contains(.,'.')]][1]//text()[string-length(normalize-space())>1 and not(./following-sibling::*[contains(.,'/100')]) and not(./preceding::text()[1]/following-sibling::br[1]/following-sibling::text()[normalize-space()]) and not(substring-after(.,'/')='100')]", verdict_xpath = u"", author_xpath = u"substring-before(substring-after(//div[translate(.,' ','')='AboutMe']/following::div[@class='module-content'][1]//p[1],' '),',')", title_xpath = u"//h1//text()", award_xpath = u"", awpic_xpath = u"")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "100", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/vacuum_cleaner_advisor_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code.encode('utf-8'))
    fh.write("")
fh.close()

