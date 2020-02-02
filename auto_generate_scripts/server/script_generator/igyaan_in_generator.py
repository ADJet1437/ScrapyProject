# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Igyaan_inSpider", spider_type = "AlaSpider", allowed_domains = "'igyaan.in'", start_urls = "'http://www.igyaan.in/category/review/amp/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//div[@class='next']/a/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//h2/a/@href", level_index = "2", url_regex = "(\w.*(?=\/amp\/))", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "substring-before(substring-after(//body/@class,'postid-'),' ')", pname_xpath = "//meta[@property='og:title']/@content", ocn_xpath = "//a[contains(@class,'category')]//text()", pic_xpath = "//meta[@property='og:image']/@content", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "substring-before(substring-after(//body/@class,'postid-'),' ')", pname_xpath = "//meta[@property='og:title']/@content", rating_xpath = "//div[contains(@class,'editor_rating')]/div[contains(@class,'number')]//text()", date_xpath = "//meta[contains(@property,'published_time')]/@content", pros_xpath = "//*[(starts-with(translate(.,' ',''),'GOODTHINGS') or starts-with(translate(.,' ',''),'TheGood')) and not(./ul)]/following-sibling::ul[1]/li//text() | //*[(starts-with(translate(.,' ',''),'GOODTHINGS') or starts-with(translate(.,' ',''),'TheGood')) and ./ul]/ul[1]/li//text()", cons_xpath = "//*[(starts-with(translate(.,' ',''),'BADTHINGS') or starts-with(translate(.,' ',''),'TheBad')) and not(./ul)]/following-sibling::ul[1]/li//text() | //*[(starts-with(translate(.,' ',''),'BADTHINGS') or starts-with(translate(.,' ',''),'TheBad')) and ./ul]/ul[1]/li//text()", summary_xpath = "//*[normalize-space()='Overview']/following::p[string-length(normalize-space())>1][1]//text() | //div[starts-with(translate(./@class,' ',''),'postcontentcontent') and not(//*[normalize-space()='Overview'])]/span[@itemprop='description']/descendant-or-self::p[string-length(normalize-space())>1][1]//text() | //div[starts-with(translate(./@class,' ',''),'postcontentcontent') and not(./span[@itemprop='description']/p) and not(//*[normalize-space()='Overview'])]/descendant-or-self::p[string-length(normalize-space())>1][1]//text() | //div[starts-with(@id,'content') and not(//*[normalize-space()='Overview']) and not(//div[starts-with(translate(./@class,' ',''),'postcontentcontent')])]/descendant-or-self::p[string-length(normalize-space())>1][1]//text() | //meta[@property='og:description' and not(//div[starts-with(@id,'content')]//p[string-length(normalize-space())>1])]/@content", verdict_xpath = "", author_xpath = "//span[contains(@class,'author')]/a//text()", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[contains(@class,'pagination')]/a[last()]/@href", test_verdict_xpaths = ['//div[contains(@class,"description-cell")]/p[normalize-space()][1]//text() | //*[(starts-with(.,"Conclusion") or starts-with(.,"CONCLUSION") or starts-with(.,"VERDICT") or starts-with(substring(.,2),"Conclusion") or starts-with(substring(.,2),"CONCLUSION") or starts-with(substring(.,2),"VERDICT")) and not(//div[contains(@class,"description-cell")]/p[normalize-space()])]/following-sibling::p[normalize-space()][1]//text() | //*[(starts-with(.,"Conclusion") or starts-with(.,"CONCLUSION") or starts-with(.,"VERDICT") or starts-with(substring(.,2),"Conclusion") or starts-with(substring(.,2),"CONCLUSION") or starts-with(substring(.,2),"VERDICT")) and not(//div[contains(@class,"description-cell")]/p[normalize-space()]) and not(./following-sibling::p)]/following-sibling::div[normalize-space()][1]//text() | //div[@class="reviewtop" and not(//div[contains(@class,"description-cell")]/p[normalize-space()]) and not(//*[(starts-with(.,"Conclusion") or starts-with(.,"CONCLUSION") or starts-with(.,"VERDICT"))])]//p//text() | //*[contains(.,"Roundup")]/following-sibling::p[string-length(normalize-space())>1][last()]//text()'], pros_xpath = "//*[(starts-with(translate(.,' ',''),'GOODTHINGS') or starts-with(translate(.,' ',''),'TheGood')) and not(./ul)]/following-sibling::ul[1]/li//text() | //*[(starts-with(translate(.,' ',''),'GOODTHINGS') or starts-with(translate(.,' ',''),'TheGood')) and ./ul]/ul[1]/li//text()", cons_xpath = "//*[(starts-with(translate(.,' ',''),'BADTHINGS') or starts-with(translate(.,' ',''),'TheBad')) and not(./ul)]/following-sibling::ul[1]/li//text() | //*[(starts-with(translate(.,' ',''),'BADTHINGS') or starts-with(translate(.,' ',''),'TheBad')) and ./ul]/ul[1]/li//text()", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/igyaan_in.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

