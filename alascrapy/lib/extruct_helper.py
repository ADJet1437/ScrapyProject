import sys
from extruct.w3cmicrodata import MicrodataExtractor
from extruct.jsonld import JsonLdExtractor
from extruct.rdfa import RDFaExtractor
from lxml.etree import XMLSyntaxError
from HTMLParser import HTMLParser

from alascrapy.items import CategoryItem, ProductIdItem, ProductItem, ReviewItem
from generic import get_full_url, remove_prefix, parse_float, normalize_price, date_format


def extract_all_json_ld(html_text):
    try:
        jslde = JsonLdExtractor()
        data = jslde.extract(html_text)
        return data
    except:
        return {}


def extract_json_ld(html, typ_str):
    try:
        jslde = JsonLdExtractor()
        items = jslde.extract(html)
        for item in items:
            item_context = item.get('@context', '').rstrip(' /')
            if (item_context == 'http://schema.org' or item_context == 'https://schema.org') \
                    and item.get('@type', '') == typ_str:
                return item

        return None
    except:
        return None


def leaf_category_item_from_breadcrumbs_json_ld(json_ld, _category=None, base_url=None, overwrite=False):
    category = _category if _category else CategoryItem()
    leaf_category = {}

    html_parser = HTMLParser()

    category_lists = json_ld.get('itemListElement', [])
    if category_lists:
        leaf_category = max(
            category_lists, key=lambda cat: cat.get('position', 0))

    leaf_category_item = leaf_category.get('item', {})
    category_name_raw = leaf_category_item.get('name', '')
    category_name = html_parser.unescape(category_name_raw)

    if overwrite or not category.get('category_path', ''):
        category['category_path'] = category_name
    if overwrite or not category.get('category_leaf', ''):
        category['category_leaf'] = category_name
    if overwrite or not category.get('category_url', ''):
        category['category_url'] = leaf_category_item.get('url', '')
        # TODO: check if '@id' contains a valid URL
        if not category['category_url']:
            category['category_url'] = leaf_category_item.get('@id', '')
            if base_url:
                category['category_url'] = get_full_url(
                    base_url, category['category_url'])

    return category


def category_item_from_breadcrumbs_json_ld(json_ld, _category=None, separator=' | ',
                                           base_url=None, including_leaf=True, overwrite=False):
    category = _category if _category else CategoryItem()
    html_parser = HTMLParser()

    category_lists = json_ld.get('itemListElement', [])
    if not category_lists:
        return

    # By convention, items in BreadcrumbList are ordered by their 'position', but this is not guaranteed.
    # See http://schema.org/BreadcrumbList
    category_lists = sorted(category_lists, key=lambda c: c.get('position', 0))
    if not including_leaf:
        category_lists.pop()

    leaf_category = max(category_lists, key=lambda c: c.get('position', 0))
    leaf_category_item = leaf_category.get('item', {})
    leaf_category_name_raw = leaf_category_item.get('name', '')
    leaf_category_name = html_parser.unescape(leaf_category_name_raw)

    if overwrite or not category.get('category_path', ''):
        category_path_raw = separator.join(
            [cat.get('item', {}).get('name', '') for cat in category_lists])
        category_path = html_parser.unescape(category_path_raw)
        category['category_path'] = category_path
    if overwrite or not category.get('category_leaf', ''):
        category['category_leaf'] = leaf_category_name
    if overwrite or not category.get('category_url', ''):
        category['category_url'] = leaf_category_item.get('url', '')
        # TODO: check if '@id' contains a valid URL
        if not category['category_url']:
            category['category_url'] = leaf_category_item.get('@id', '')
            if base_url:
                category['category_url'] = get_full_url(
                    base_url, category['category_url'])

    return category


def product_item_from_product_json_ld(json_id, _product=None, base_url=None, overwrite=False):
    product = _product if _product else ProductItem()
    html_parser = HTMLParser()

    # TODO: test if it is a valid URL
    if overwrite or not product.get('PicURL'):
        pic_url = json_id.get('image', '')
        if pic_url:
            if base_url:
                product['PicURL'] = get_full_url(base_url, pic_url)
            else:
                product['PicURL'] = pic_url

    if overwrite or not product.get('ProductManufacturer'):
        brand = json_id.get('brand', '')
        if isinstance(brand, dict):
            brand = brand.get('name', '')
        if brand:
            product['ProductManufacturer'] = html_parser.unescape(
                brand).strip()

    if overwrite or not product.get('ProductName'):
        product_name = html_parser.unescape(json_id.get('name', '')).strip()

        if product_name:
            product['ProductName'] = product_name

        # TODO: undo this step if it does not make sense for most of the sources
        if product.get('ProductManufacturer') and product.get('ProductName') and \
                product['ProductManufacturer'].lower() not in product['ProductName'].lower():
            product['ProductName'] = product['ProductManufacturer'] + \
                ' ' + product['ProductName']

    return product


def review_item_from_article_json_ld(json_ld, _review=None, overwrite=False):
    review = _review if _review else ReviewItem()
    html_parser = HTMLParser()

    if overwrite or not review.get('TestSummary', ''):
        summary = json_ld.get('description', '')
        if summary:
            review['TestSummary'] = html_parser.unescape(summary).strip()

    if overwrite or not review.get('TestTitle', ''):
        title = json_ld.get('name', '')
        if not title:
            title = json_ld.get('headline', '')

        if title:
            review['TestTitle'] = html_parser.unescape(title).strip()

    if overwrite or not review.get('Author', ''):
        try:
            author_str = json_ld.get('author', {}).get('name', '')
        except:
            author_list = json_ld.get('author', [])
            author_str = ', '.join(a.get('name', '') for a in author_list)

        if author_str:
            review['Author'] = html_parser.unescape(author_str).strip()

    if overwrite or not review.get('TestDateText', ''):
        test_date_text = json_ld.get('datePublished', '')
        if test_date_text:
            test_date_text = date_format(test_date_text, '')
            review['TestDateText'] = test_date_text

    return review


def review_item_from_review_json_ld(json_ld, _review=None, overwrite=False):
    review = _review if _review else ReviewItem()
    html_parser = HTMLParser()

    review_rating_obj = json_ld.get('reviewRating', {})

    if review_rating_obj and (overwrite or not review.get('SourceTestScale', '')):
        # according to Google Developers, 5 is the default best rating
        review['SourceTestScale'] = review_rating_obj.get('bestRating', 5)

    if review_rating_obj and (overwrite or not review.get('SourceTestRating', '')):
        review['SourceTestRating'] = review_rating_obj.get('ratingValue', None)
        if review.get('SourceTestRating') is not None:
            # Do not assign rating from JSON LD if its value is less than that of worst rating
            try:
                # according to Google Developers, 1 is the default worst rating
                worst_rating = float(review_rating_obj.get('worstRating', 1))
                if float(review['SourceTestRating']) < worst_rating:
                    review['SourceTestRating'] = ''
            except:
                pass

    if overwrite or not review.get('ProductName', ''):
        item_reviewed = json_ld.get('itemReviewed', {})
        product_name = item_reviewed.get('name', '')
        if product_name:
            review['ProductName'] = html_parser.unescape(product_name).strip()

    # For all the information we can extract from 'Article' JSON-LD, the way
    # to extract them from 'Review' JSON-LD is exactly the same
    review = review_item_from_article_json_ld(json_ld, review, overwrite)

    return review


def get_microdata_extruct_items(htmltext):
    mde = MicrodataExtractor()
    try:
        items = mde.extract(htmltext)
    except XMLSyntaxError:
        return  # Nothing to do here

    return items


# TODO: refactor, give methods that parses items from microdata better names
def get_products_microdata_extruct(items, response, category, locale='en'):
    for item in items:
        if item['type'] == "http://schema.org/Product":
            product = product_microdata_extruct(
                response, item, category=category, locale=locale)
            yield product


def product_items_from_microdata(response, category='', htmltext='', locale='en'):
    if not htmltext:
        htmltext = response.text
    items = get_microdata_extruct_items(htmltext)
    _product = list(get_products_microdata_extruct(
        items, response, category, locale))

    if len(_product) == 0:
        return _product

    if len(_product) > 1:
        raise Exception("Number of products microdata in html is greater "
                        "than one %s" % _product)
    return _product[0]


# TODO: Maybe allow a product to be passed in? Or at least its source_internal_id,
# also allow the script to select the source_internal_id to be used
def product_microdata_extruct(response, product_extruct, category='', locale='en'):
    properties = product_extruct['properties']
    product_name = properties.get('name', '')
    if isinstance(product_name, list):
        product_name = product_name[0]

    brand = properties.get('brand', '')
    if not brand:
        brand = properties.get('manufacturer', '')

    if isinstance(brand, dict):
        brand = brand['properties'].get('name', '')

    pic_url = properties.get('image', '')
    if not pic_url:
        img_dict = properties.get('review', {}).get('properties', {}).get('image', [])
        if isinstance(img_dict[0], dict):
            pic_url = img_dict[0].get('properties', {}).get('url', '')
        else:  # str
            pic_url = img_dict[0]

    sku = properties.get('sku', '')
    source_internal_id = sku.replace('sku:', '', 1)

    gtin = properties.get('gtin14', '')
    gtin = properties.get('gtin13', gtin)
    gtin = properties.get('gtin12', gtin)
    gtin = properties.get('gtin8', gtin)
    mpn = properties.get('mpn', '')
    productid = properties.get('productID', '')
    model = properties.get('model', '')
    offers = properties.get('offers', {})

    product = ProductItem.from_response(response, category, product_name=product_name,
                                        manufacturer=brand, pic_url=pic_url,
                                        source_internal_id=source_internal_id)
    product_ids = []
    if isinstance(offers, list):
        offers = offers[0]
    if offers:
        price = offers.get('properties', {}).get('price', '')
        if not price:
            price = offers.get('properties', {}).get('lowPrice', '')
        if not price:
            raise Exception("Found offer but no price!, check")
        price = parse_float(price, locale=locale)
        if not price:
            print price
        price = normalize_price(price)
        price_id = ProductIdItem.from_product(
            product, kind='price', value=price)
        product_ids.append(price_id)

    if sku:
        sku_id = ProductIdItem.from_product(product, kind='sku', value=sku)
        product_ids.append(sku_id)

    if productid:
        # raise Exception("This source has productid") #TODO
        pass

    # According to http://schema.org/Product, only a few domains
    # uses the following properties. Extract them if they become used widely
    if mpn:
        # raise Exception("This source has mpn") #TODO
        pass

    if gtin:
        # raise Exception("This source has gtin") #TODO
        pass

    if model:
        # raise Exception("This source has model") #TODO
        pass

    return {'product': product, 'product_ids': product_ids}


def get_reviews_microdata_extruct(items, product, review_type,
                                  verdict='', url='', pros='', cons='',
                                  award='', award_pic=''):
    for item in items:
        if item['type'] == "http://schema.org/Review":
            review = review_microdata_extruct(item, product=product, tp=review_type,
                                              verdict=verdict, url=url, pros=pros, cons=cons,
                                              award=award, award_pic=award_pic)
            yield review


def review_microdata_extruct(review_extruct, product=None, tp='',
                             verdict='', url='', pros='', cons='',
                             award='', award_pic=''):
    properties = review_extruct['properties']

    rating = properties.get('reviewRating', {}).get('ratingValue', '')
    if not rating:
        rating = properties.get('reviewRating', {}).get(
            'properties', {}).get('ratingValue', '')

    scale = properties.get('reviewRating', {}).get('bestRating', '')
    if not scale:
        scale = properties.get('reviewRating', {}).get(
            'properties', {}).get('bestRating', '')

    summary = properties.get('description', '')

    title = properties.get('name', '')
    if not title:
        title = properties.get('headline', '')
    if not title:  # mm.de uses summary as review title. Makes a bit of
        # sense, therefore it is here
        title = properties.get('summary', '')

    author = properties.get('author', '')
    if not isinstance(author, basestring):
        author = author.get('properties', {}).get('name', '')

    date = properties.get('datePublished', '')

    return ReviewItem.from_product(product=product, tp=tp, rating=rating, scale=scale,
                                   date=date, author=author, title=title,
                                   summary=summary, verdict=verdict, url=url, pros=pros,
                                   cons=cons, award=award, award_pic=award_pic)


def get_review_items_from_microdata(spider, review_type, response, product, reviews_xpath=None,
                                    pros_xpath=None, cons_xpath=None):
    '''
    Get all reviews from a page, useful for user review pages with microdata
    :param spider: the spider we use to scrape the site
    :param review_type: type of the reviews to scrape, should be either USER or PRO
    :param response: an instance of Scrapy's Response object where reviews will be scraped from
    :param product: the product item the reviews are written for
    :param reviews_xpath: the xpath to extract review selectors from 'response'
    :param pros_xpath: the xpath to extract pros from review selectors
    :param cons_xpath: the xpath to extract cons from review selectors
    :return: list of all review items extracted
    '''
    mde = MicrodataExtractor()
    try:
        items = mde.extract(response.text)
    except XMLSyntaxError:
        return []  # Nothing to do here...

    all_review_extracts = [i for i in items if i['type']
                           == "http://schema.org/Review"]
    all_pros = []
    all_cons = []

    if reviews_xpath:
        add_pros_and_cons = True
        all_reviews = response.xpath(reviews_xpath)
        for single_review in all_reviews:
            if pros_xpath:
                pros = spider.extract_all(
                    single_review.xpath(pros_xpath), separator=' ; ')
            else:
                pros = ''
            if cons_xpath:
                cons = spider.extract_all(
                    single_review.xpath(cons_xpath), separator=' ; ')
            else:
                cons = ''
            all_pros.append(pros)
            all_cons.append(cons)

        if len(all_pros) != len(all_review_extracts) or len(all_cons) != len(all_review_extracts):
            spider.logger.warning(
                "Number of reviews extracted from xpath is different from number of review microdata.")
            add_pros_and_cons = False
    else:
        add_pros_and_cons = False

    review_items = []
    for index, item in enumerate(all_review_extracts):
        if add_pros_and_cons:
            review = review_microdata_extruct(item, product=product, tp=review_type,
                                              pros=all_pros[index], cons=all_cons[index])
        else:
            review = review_microdata_extruct(
                item, product=product, tp=review_type)
        review_items.append(review)

    return review_items


def extract_all_rdfa(response):
    rdfa_extractor = RDFaExtractor()
    return rdfa_extractor.extract(response.text, url=response.url)


def find_rdfa_items_by_type(rdfa_items, typ_str):
    return_items = []

    for item in rdfa_items:
        if '@type' in item and \
                (typ_str in item['@type'] or 'http://schema.org/' + typ_str in item['@type'] or
                 'https://schema.org/' + typ_str in item['@type']):
            return_items.append(item)

    return return_items


def get_rdfa_attribute_value(item, attribute):
    attribute_list = item.get(attribute, [])
    value = attribute_list[0].get('@value') if attribute_list else ''
    if isinstance(value, basestring):
        value = value.strip()

    return value


def get_rdfa_attribute_id(item, attribute):
    attribute_list = item.get(attribute, [])
    return attribute_list[0].get('@id') if attribute_list else ''


# TODO: we are only using this function for alphr.com right now, update it with new logic if necessary
def get_review_items_from_rdfa(response, rdfa_items):
    extracted_reviews = []

    all_review_rdfa = find_rdfa_items_by_type(rdfa_items, 'Review')
    for review_rdfa in all_review_rdfa:
        review = ReviewItem()
        review['TestUrl'] = response.url

        review['ProductName'] = get_rdfa_attribute_value(
            review_rdfa, 'http://schema.org/itemReviewed')
        review['TestTitle'] = get_rdfa_attribute_value(
            review_rdfa, 'http://schema.org/headline')
        review['TestSummary'] = get_rdfa_attribute_value(
            review_rdfa, 'http://schema.org/description')
        review['TestDateText'] = get_rdfa_attribute_value(
            review_rdfa, 'http://schema.org/datePublished')

        # TODO: see how a page with multiple authors is like
        review_author_id = get_rdfa_attribute_id(
            review_rdfa, 'http://schema.org/author')
        review_rating_id = get_rdfa_attribute_id(
            review_rdfa, 'http://schema.org/reviewRating')

        review['Author'] = ''
        for item in rdfa_items:
            item_id = item.get('@id')
            if item_id == review_author_id:
                review['Author'] = get_rdfa_attribute_value(
                    item, 'http://schema.org/name')
            elif item_id == review_rating_id:
                review['SourceTestRating'] = get_rdfa_attribute_value(
                    item, 'http://schema.org/ratingValue')

        extracted_reviews.append(review)

    return extracted_reviews
