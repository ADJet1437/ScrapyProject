# -*- coding: utf8 -*-

#generato config
generator_save_path = './script_generator/'

#execute script cmd
execute_generator_cmd = 'python ' + generator_save_path + '%s'

#script config
script_save_path = '/home/alascrapy/alaScrapy/alascrapy/spiders/'
json_save_path = '/home/alascrapy/alaScrapy/alascrapy/conf/sources_conf/'


#source config
source_json = '''{
    "source_id": %s,
    "use_proxy": %s,
    "validate_csv_fields":{
        "product_id":{
            "source_id":          {"required": true},
            "source_internal_id": {"required": false},
            "ProductName":        {"required": true},
            "ID_kind":            {"required": false},
            "ID_value":           {"required": false}
        },
        "product":{
            "source_id":            {"required": true},
            "source_internal_id":   {"required": false},
            "ProductName":          {"required": true},
            "OriginalCategoryName": {"required": true},
            "PicURL":               {"required": true},
            "ProductManufacturer":  {"required": false},
            "TestUrl":              {"required": true}
        },
        "review":{
            "source_id":          {"required": true},
            "source_internal_id": {"required": false},
            "ProductName":        {"required": true},
            "SourceTestRating":   {"required": true},
            "SourceTestScale":    {"required": true},
            "TestDateText":       {"required": false},
            "TestPros":           {"required": false},
            "TestCons":           {"required": false},
            "TestSummary":        {"required": true},
            "TestVerdict":        {"required": false},
            "Author":             {"required": false},
            "DBaseCategoryName":  {"required": true},
            "TestTitle":          {"required": false},
            "TestUrl":            {"required": true},
            "award":              {"required": false},
            "AwardPic":           {"required": false},
            "countries":          {"required": false}
        }
    }
}'''
