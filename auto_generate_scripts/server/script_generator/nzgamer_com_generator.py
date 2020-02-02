# -*- coding: utf8 -*-
import sys
sys.path.append("../")
from server.gen_spiders import *

code_fragments = []

spa = SpiderGenerator()
return_code = spa.gen_import()
code_fragments.append(return_code)

return_code = spa.gen_init(spider_name = "Nzgamer_comSpider", spider_type = "AlaSpider", allowed_domains = "'nzgamer.com'", start_urls = "'http://nzgamer.com/reviews/'")
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "1", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.gen_request_urls(urls_xpath = "//tr//td/a/@href", level_index = "2", url_regex = "", include_original_url = "", params_xpath = {}, params_regex = {})
code_fragments.append(return_code)

return_code = spa.gen_request_single_url(url_xpath = "//span[contains(@class,'btn_active')]/following-sibling::a[1]/@href", level_index = "1", url_regex = "", product_fields = [])
code_fragments.append(return_code)

return_code = spa.gen_level(level_index = "2", need_parse_javascript = "")
code_fragments.append(return_code)

return_code = spa.get_category(category_leaf_xpath = "'nzgamer.com'", category_path_xpath = "'nzgamer.com'")
code_fragments.append(return_code)

return_code = spa.gen_product(sii_xpath = "", pname_xpath = "//h1[@itemprop='itemreviewed']//text()", ocn_xpath = "'nzgamer.com'", pic_xpath = "((//img[@class='main-image']|//div[@class='feature-main']/img)[1]|//div[@class='article']/p[a/img][1]//img)[1]/@src", manuf_xpath = "")
code_fragments.append(return_code)

return_code = spa.gen_review(sii_xpath = "", pname_xpath = "//h1[@itemprop='itemreviewed']//text()", rating_xpath = "//div[@itemprop='rating']/span[@itemprop='value']//text()", date_xpath = "//span[@itemprop='dtreviewed']/@datetime", pros_xpath = "", cons_xpath = "", summary_xpath = "//div[@class='article']/p[1]//text()", verdict_xpath = "//div[@class='quick_glance']//text()", author_xpath = "//span[@itemprop='reviewer']//text()", title_xpath = "//h1[@itemprop='itemreviewed']//text()", award_xpath = "", awpic_xpath = "")
code_fragments.append(return_code)

return_code = spa.get_sourcetestscale(scale = "10", review_type = "pro")
code_fragments.append(return_code)

return_code = spa.save_product()

code_fragments.append(return_code)

return_code = spa.get_dbasecategoryname(dbcn = "pro")
code_fragments.append(return_code)

return_code = spa.get_fields_supplement(in_another_page_xpath = "//div[@class='pagination']/a[last()]/@href", test_verdict_xpaths = ['//div[@class="quick_glance"]//text()'], pros_xpath = "", cons_xpath = "", rating_xpath = "//div[@itemprop='rating']/span[@itemprop='value']//text()", award_xpath = "", award_pic_xpath = "")
code_fragments.append(return_code)

return_code = spa.save_review(review_type = "pro")
code_fragments.append(return_code)

script_name = "/home/alascrapy/alaScrapy/alascrapy/spiders/nzgamer_com.py"
fh = open(script_name, 'w+')
for code in code_fragments:
    fh.write(code)
    fh.write("")
fh.close()

