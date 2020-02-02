from alascrapy.spiders.base_spiders.amazon_API_spider import AmazonAPISpider


class AmazonComAPISpider(AmazonAPISpider):
    source_key = 'com'
    name = 'amazon_api_com'
    start_urls = ['https://www.amazon.com']
    endpoint = 'webservices.amazon.com'
    associate_tag = 'alatestcouk0e-21'
    subscription_id = '0EWA6R5AGNW9AA6JF8R2'
    secret_key = '1RFwtwfJeqi6fTzO/hxmf+J9E8Nfai2rHWSwy6xu'