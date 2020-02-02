# -*- coding: utf8 -*-
import jinja2
from script_template import *

class SpiderGenerator():
    
    def __init__(self):
        self.response_meta = []
        self.fields_on_other_page = False
        self.verdict_xpath_num = None
        self.click_next_page = False
        self.first_js_on_page = 'true'
        self.highest_level = 0
        
    def gen_import(self):
        tp = jinja2.Template(import_template)
        import_code = tp.render()
        return import_code
    
    def gen_init(self, spider_name, spider_type, allowed_domains, start_urls):
        name = ""
        name = spider_name.lower().replace('spider','')
        tp = jinja2.Template(init_func_template)
        init_func_code = tp.render(spider_name = spider_name, name = name, spider_type = spider_type, allowed_domains = allowed_domains, start_urls = start_urls)
        return init_func_code
        
    def gen_level(self, level_index, need_parse_javascript = ''):
        self.first_js_on_page = 'true'
        self.highest_level += 1
        tp = jinja2.Template(level_template)
        level_name_code = tp.render(level_index = level_index, need_parse_javascript = need_parse_javascript)
        if need_parse_javascript == 'yes':
            self.first_js_on_page = 'false'
        return level_name_code
        
    def gen_request_single_url(self, url_xpath, level_index, url_regex, product_fields):
        for item in product_fields:
            self.response_meta.append(item)
        tp = jinja2.Template(request_single_url_template)
        request_single_url_code = tp.render(url_xpath = url_xpath, level_index = level_index, url_regex = url_regex)
        return request_single_url_code
        
    def gen_request_urls(self, urls_xpath, level_index, url_regex, include_original_url = '', params_xpath = {}, params_regex = {}):
        tp = jinja2.Template(request_urls_template)
        request_urls_code = tp.render(urls_xpath = urls_xpath, level_index = level_index, url_regex = url_regex, include_original_url = include_original_url, params_xpath = params_xpath, params_regex = params_regex)
        return request_urls_code
        
    def gen_request_containers_urls(self, containers_xpath, url_xpath, level_index, params_xpath = {}, params_regex = {}):
        for item in params_xpath.keys():
            self.response_meta.append(item)
        tp = jinja2.Template(request_containers_urls_template)
        request_containers_urls_code = tp.render(containers_xpath = containers_xpath, url_xpath = url_xpath, level_index = level_index, params_xpath = params_xpath, params_regex = params_regex)
        return request_containers_urls_code
        
    def gen_product(self, sii_xpath = '', pname_xpath = '', ocn_xpath = '', pic_xpath = '', manuf_xpath = ''):
        tp = jinja2.Template(product_template)
        init_product_code = tp.render(sii_xpath = sii_xpath, pname_xpath = pname_xpath, ocn_xpath = ocn_xpath, pic_xpath = pic_xpath, manuf_xpath = manuf_xpath)
        return init_product_code
        
    def gen_review(self, sii_xpath = '', pname_xpath = '', rating_xpath = '', date_xpath = '', pros_xpath = '', cons_xpath = '', 
                                            summary_xpath = '', verdict_xpath = '', author_xpath = '', title_xpath = '', award_xpath = '', awpic_xpath = ''):
        tp = jinja2.Template(review_template)
        init_review_code = tp.render(sii_xpath = sii_xpath, pname_xpath = pname_xpath, rating_xpath = rating_xpath, date_xpath = date_xpath, pros_xpath = pros_xpath, cons_xpath = cons_xpath, 
                                                        summary_xpath = summary_xpath, verdict_xpath = verdict_xpath, author_xpath = author_xpath, title_xpath = title_xpath, award_xpath = award_xpath, awpic_xpath = awpic_xpath)
        return init_review_code

    def gen_containers_review(self, containers_xpath = '', button_next_javascript = 'no', button_next_xpath = '', sii_xpath = '', pname_xpath = '', rating_xpath = '', date_xpath = '', pros_xpath = '', cons_xpath = '', 
                                            summary_xpath = '', verdict_xpath = '', author_xpath = '', title_xpath = '', award_xpath = '', awpic_xpath = ''):
        tp = jinja2.Template(containers_review_template)
        init_review_code = tp.render(containers_xpath = containers_xpath, button_next_javascript = button_next_javascript, button_next_xpath = button_next_xpath, sii_xpath = sii_xpath, pname_xpath = pname_xpath, rating_xpath = rating_xpath, date_xpath = date_xpath, pros_xpath = pros_xpath, cons_xpath = cons_xpath, 
                                                        summary_xpath = summary_xpath, verdict_xpath = verdict_xpath, author_xpath = author_xpath, title_xpath = title_xpath, award_xpath = award_xpath, awpic_xpath = awpic_xpath, first_js_on_page = self.first_js_on_page, highest_level = str(self.highest_level), response_meta = self.response_meta)
        if button_next_javascript == 'yes':
            self.click_next_page = True
            self.first_js_on_page = 'false'
        return init_review_code
        
    def get_productname_from_title(self, replace_words = []):
        tp = jinja2.Template(get_pname_from_title_template)
        productname_code = tp.render(replace_words = replace_words)
        return productname_code
        
    def get_dbasecategoryname(self, dbcn):
        tp = jinja2.Template(get_dbasecategoryname_template)
        dbcn_code = tp.render(dbcn = dbcn.upper(), review_type = dbcn.upper(), click_next_page = self.click_next_page, first_js_on_page = self.first_js_on_page)
        return dbcn_code
    
    def get_sourcetestscale(self, scale, review_type):
        tp = jinja2.Template(get_sourcetestscale_template)
        scale_code = tp.render(scale = scale, review_type = review_type.upper(), click_next_page = self.click_next_page, first_js_on_page = self.first_js_on_page)
        return scale_code
        
    def get_testdatetext(self, review_type, replace_words = [], format_string = '', languages = ''):
        tp = jinja2.Template(get_testdatetext_template)
        if format_string == '':
            format_string = '%d %B %Y'
        if languages == '':
            languages = 'en'
        date_code = tp.render(review_type = review_type.upper(), click_next_page = self.click_next_page, replace_words = replace_words, format_string = format_string, languages = languages, first_js_on_page = self.first_js_on_page)
        return date_code
        
    def clean_field(self, type, field, regex, review_type):
        tp = jinja2.Template(clean_field_template)
        field_code = tp.render(type = type, field = field, regex = regex, review_type = review_type.upper(), click_next_page = self.click_next_page, first_js_on_page = self.first_js_on_page)
        return field_code

    def get_supplement_xpaths(self, type, field, supplement_xpaths, review_type):
        tp = jinja2.Template(get_supplement_xpath_template)
        field_code = tp.render(type = type, field = field, supplement_xpaths = supplement_xpaths, review_type = review_type.upper(), click_next_page = self.click_next_page, first_js_on_page = self.first_js_on_page)
        return field_code
        
    def get_fields_supplement(self, in_another_page_xpath = '', test_verdict_xpaths = [], pros_xpath = '', cons_xpath = '', rating_xpath = '', award_xpath = '', award_pic_xpath = ''):
        if in_another_page_xpath:
            self.fields_on_other_page = True
            self.verdict_xpath_num = xrange(len(test_verdict_xpaths))
        tp = jinja2.Template(get_fields_supplement_template)
        get_fields_code = tp.render(in_another_page_xpath = in_another_page_xpath, test_verdict_xpaths = test_verdict_xpaths, pros_xpath = pros_xpath, cons_xpath = cons_xpath, rating_xpath = rating_xpath, award_xpath = award_xpath, award_pic_xpath = award_pic_xpath)
        return get_fields_code
        
    #common types: invisibility_of_element_located, presence_of_all_elements_located, element_to_be_clickable
    def click(self, target_xpath, wait_for_xpath = '', wait_type = ''):
        tp = jinja2.Template(click_template)
        if wait_for_xpath == "" or wait_type == "":
            wait_type = "wait_none"
        click_code = tp.render(target_xpath = target_xpath, wait_for_xpath = wait_for_xpath, wait_type = wait_type, first_js_on_page = self.first_js_on_page)
        self.first_js_on_page = 'false'
        return click_code
        
    def click_continuous(self, target_xpath, wait_for_xpath = '', wait_type = ''):
        tp = jinja2.Template(click_continuous_template)
        if wait_for_xpath == "" or wait_type == "":
            wait_type = "wait_none"
        click_continuous_code = tp.render(target_xpath = target_xpath, wait_for_xpath = wait_for_xpath, wait_type = wait_type, first_js_on_page = self.first_js_on_page)
        self.first_js_on_page = 'false'
        return click_continuous_code  

    def scroll(self, wait_for_xpath = '', wait_type = ''):
        tp = jinja2.Template(scroll_template)
        if wait_for_xpath == "" or wait_type == "":
            wait_type = "wait_none"
        scroll_code = tp.render(wait_for_xpath = wait_for_xpath, wait_type = wait_type, first_js_on_page = self.first_js_on_page)
        self.first_js_on_page = 'false'
        return scroll_code

    def get_product_id(self, id_value_xpath = '', id_kind = ''):
        tp = jinja2.Template(product_id_template)
        product_id_code = tp.render(id_value_xpath = id_value_xpath, id_kind = id_kind)
        return product_id_code

    def get_category(self, category_leaf_xpath = '', category_path_xpath = ''):
        tp = jinja2.Template(category_template)
        category_code = tp.render(category_leaf_xpath = category_leaf_xpath, category_path_xpath = category_path_xpath)
        return category_code

        
    def save_product(self):
        tp = jinja2.Template(save_product_template)
        save_product_code = tp.render(response_meta = self.response_meta)
        return save_product_code
        
    def save_review(self, review_type):
        parse_verdict_page_code = ''
        tp = jinja2.Template(save_review_template)
        save_review_code = tp.render(response_meta = self.response_meta, review_type = review_type.upper(), click_next_page = self.click_next_page, first_js_on_page = self.first_js_on_page)
        if self.fields_on_other_page:
            tp = jinja2.Template(parse_fields_template)
            parse_verdict_page_code = tp.render(verdict_xpath_num = self.verdict_xpath_num)
            save_review_code = ''
        return save_review_code + parse_verdict_page_code
    
if __name__ == '__main__':
    spa = SpiderGenerator()
    import_code = spa.gen_import()
    init_func_code = spa.gen_init("Zdnet_DeSpider", "AlaSpider", "zdnet.de", "'http://www.zdnet.de/kategorie/mobility/laptops/', 'http://www.zdnet.de/kategorie/mobility/smartphones/', 'http://www.zdnet.de/kategorie/mobility/tablets/' ")
    level_1 = spa.gen_level("1")
    request_single_url_code = spa.gen_request_single_url("//li[@class='next']/a/@href", '1')
    request_urls_code = spa.gen_request_urls("//article/h2/a/@href", '2')
    level_2 = spa.gen_level("2")
    init_product_code = spa.gen_product(pic_xpath = "(//*[@property='og:image'])[1]/@content", ocn_xpath = "//div[@id='breadcrumb']/a[last()]/text()")
    init_review_code = spa.gen_review(title_xpath = "//*[@property='og:title']/@content", summary_xpath = "//meta[@name='description']/@content", author_xpath = "//span[@class='byline']/a/text()", 
                                                            rating_xpath = "//div[@class='score']/text()", date_xpath = "//span[@class='byline']//time/@datetime", verdict_xpath = "//div[@class='fazit']/p/text()", 
                                                            pros_xpath = "//div[@class='pro']//li//text()", cons_xpath = "//div[@class='con']//li//text()"
                                                            )
    productname_code = spa.get_productname_from_title(replace_words = ["| ZDNet.de"])
    dbcn_code = spa.get_dbasecategoryname('PRO')
    scale_code = spa.get_sourcetestscale('10')
    date_code = spa.get_testdatetext()
    save_product_code = spa.save_product()
    save_review_code, parse_verdict_page_code = spa.save_review()
    
    print import_code
    print init_func_code
    print level_1
    print request_single_url_code
    print request_urls_code
    print level_2
    print init_product_code
    print init_review_code
    print productname_code
    print dbcn_code
    print scale_code
    print date_code
    print save_product_code
    print save_review_code
    
