# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Greenbot_comSpider", spider_type = "AlaSpider", allowed_domains = "'greenbot.com'", start_urls = "'http://www.greenbot.com/reviews/?start=0'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//a[starts-with(@id,'load-more')]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//div[starts-with(@class,'index-promo') or starts-with(@class,'river-well')]//h3/descendant-or-self::a[1]/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "//nav[starts-with(@class,'breadcrumbs')]/ul/li[last()]//text()", category_path_xpath = "//nav[starts-with(@class,'breadcrumbs')]/ul/li//text()")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "//meta[@property='og:url']/@content", pname_xpath = "(//article/descendant-or-self::ul[@class='aag-list'][1]/descendant-or-self::*[@class='product-name']/descendant-or-self::*[text()][last()]//text() | //meta[@property='og:title']/@content | //h1//text())[last()]", ocn_xpath = "", pic_xpath = "(//*[(name()='div' and @itemprop='reviewBody') or (name()='figure' and @id='page-lede')]/descendant-or-self::img[1]/@src | //meta[@property='og:image' and normalize-space(./@content)]/@content)[1]", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "//meta[@property='og:url']/@content", pname_xpath = "(//article/descendant-or-self::ul[@class='aag-list'][1]/descendant-or-self::*[@class='product-name']/descendant-or-self::*[text()][last()]//text() | //meta[@property='og:title']/@content | //h1//text())[last()]", rating_xpath = "translate(string(concat(//article/descendant-or-self::ul[@class='aag-list'][1]/descendant-or-self::div[@class='rating' and not(//*[starts-with(normalize-space(),'Rating:')])][1]/meta/@content, substring-before(concat(substring-before(concat(normalize-space(substring-after(//*[starts-with(normalize-space(),'Rating:')]//text(),'Rating:')),'/'),'/'),' '),' '),string(number(substring-before(substring-after(//p/img[contains(@src,'rating') and not(//div[@class='rating'])]/@src,'rating_'),'-')) div 10),translate(string(count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'one-star') and not(//meta[@itemprop='ratingValue'])])*1 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'one-half-star') and not(//meta[@itemprop='ratingValue'])])*1.5 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'two-star') and not(//meta[@itemprop='ratingValue'])])*2 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'two-half-star') and not(//meta[@itemprop='ratingValue'])])*2.5 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'three-star') and not(//meta[@itemprop='ratingValue'])])*3 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'three-half-star') and not(//meta[@itemprop='ratingValue'])])*3.5 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'four-star') and not(//meta[@itemprop='ratingValue'])])*4 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'four-half-star') and not(//meta[@itemprop='ratingValue'])])*4.5 + count(//article/descendant-or-self::div[@class='rating'][1]/span[contains(@class,'five-star') and not(//meta[@itemprop='ratingValue'])])*5),'0',''))),'NaN','')", date_xpath = "//meta[@name='date']/@content", pros_xpath = "//div[contains(@class,'pros')]/ul/li//text()", cons_xpath = "//div[contains(@class,'cons')]/ul/li//text()", summary_xpath = "//meta[@name='description']/@content", verdict_xpath = "//div[@itemprop='reviewBody']/descendant-or-self::*[(name()='h2' or name()='h3' or name()='h4') and ./following-sibling::p[string-length(normalize-space())>1]][last()]/following-sibling::p[string-length(normalize-space())>1 and not(//ul[@class='aag-list']//div[@class='expanded-content']/p)][1]//text() | //ul[@class='aag-list']//div[@class='expanded-content']/p//text()", author_xpath = "//div/descendant-or-self::*[(name()='a' and @rel='author') or ((name()='p' or name()='span') and @itemprop='author')][1]/span//text()", title_xpath = "//meta[@property='og:title']/@content", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "5", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "product", field = "source_internal_id", regex = "((?<=\/article\/)\d*(?=\/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.clean_field(type = "review", field = "source_internal_id", regex = "((?<=\/article\/)\d*(?=\/))", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//section[@class='pagination']/span[@class='page-numbers']/a[last()]/@href", test_verdict_xpaths = ['//div[@itemprop="reviewBody"]/descendant-or-self::*[(name()="h2" or name()="h3" or name()="h4") and ./following-sibling::p[string-length(normalize-space())>1]][last()]/following-sibling::p[string-length(normalize-space(./text()))>1 and not(//ul[@class="aag-list"]//div[@class="expanded-content"]/p)][1]//text() | //ul[@class="aag-list"]//div[@class="expanded-content"]/p//text()'], pros_xpath = "//div[contains(@class,'pros')]/ul/li//text()", cons_xpath = "//div[contains(@class,'cons')]/ul/li//text()", rating_xpath = "", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/greenbot_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

