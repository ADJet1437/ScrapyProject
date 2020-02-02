__author__ = 'graeme'

import dateparser
import dateutil.parser
import lxml.etree
import lxml.html
import json
import re
import urllib2
import requests
import hashlib

from scrapy.http import Response
from babel.numbers import format_decimal, parse_decimal, NumberFormatError

from urllib import urlencode
from contextlib import closing
from os.path import join
from urlparse import urlparse, parse_qs, urlsplit, urlunsplit, urljoin

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_html(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def strip(string, strip_chars='', strip_unicode=None, keep_whitespace=False):
    if strip_unicode is None:
        strip_unicode = []
    for unicode in strip_unicode:
        string = string.replace(unicode, '')

    string = string.replace(u'\xa0', ' ')
    if keep_whitespace:
        string = string.strip(strip_chars)
    else:
        string = string.strip(" \t\n\r" + strip_chars)

    return string

def set_query_parameter(url, param_name, param_value):
    """Given a URL, set or replace a query parameter and return the
    modified URL.

     set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://example.com?foo=stuff&biz=baz'

    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))

def remove_query_parameter(url, param_name):
    """Given a URL, remove a query parameter and return the
    modified URL.

     set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo')
    'http://example.com?biz=baz'

    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    query_params.pop(param_name, None)
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))



def md5(abs_filepath):
    hash = hashlib.md5()
    with open(abs_filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

def download_file(url, abs_filepath, auth=None, params=None):
    with closing(requests.get(url, auth=auth, params=params, stream=True)) as r:
        with open(abs_filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)


def get_query_parameter(url, param_name):
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    param = query_params.get(param_name, [])
    if len(param) == 1:
        return param[0]
    else:
        return param

def remove_querystring(url):
    if not url:
        return None
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    return urlunsplit((scheme, netloc, path, '', ''))    

def normalize_price(price):
    #return format_decimal(price, format="#.##", locale='de_DE')
    return str(int(price))

def get_base_url(url):
    if not url:
        return None
    parsed_uri = urlparse(url)
    base_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return base_url


def get_full_url(url, relative_url):
    if isinstance(url, Response):
        url = url.url

    if relative_url:
        return urljoin(url, relative_url)
    return None


def get_text_from_selector(selector, *strip_nodes):
    element = selector._root
    lxml.etree.strip_elements(element, lxml.etree.Comment, *strip_nodes, with_tail=False)
    text = lxml.html.tostring(element, method="text", encoding=unicode)
    return text.strip()


def search_regex_group(pattern, string, group=1):
    name_match = re.search(pattern, string)
    if name_match:
        return name_match.group(group)
    return None


def get_num(x):
    """
    Extract all digits from a string
    :param x: Input string
    :return: integer made from all the numbers in the string
    """
    return int(''.join(ele for ele in x if ele.isdigit()))


def abbreviate_month(date, separator=' '):
    """
    Replace month name in date string with its abbreviated version, for example,
    Augusti -> Aug, thus it can be parsed by date_format. Required for Swedish sources 
    with full month name, as dateparser does not support Swedish language
    :param date: The date string to format
    :param separator: The separators of date, month, and year
    :return: The date string with abbreviated month name
    """
    new_date = ''
    try:
        date_items = date.split(separator)
        for item in date_items:
            if item.isdigit():
                new_date += item
            else:
                new_date += item[:3]
            new_date += separator

        new_date.rstrip(separator)
    except Exception, e:
        print str(e)
        print "Failed to abbreviate the month in abbreviate_month. " \
              "Original date is {}".format(date)

    return new_date


def date_format(date, format_string, languages=None):
    """
    Take a date and format it into our normal database format (YYYY-MM-DD)
    :param date: The date to format
    :param format_string: The format of the date
    :return: The date reformatted to our format
    """
    new_date = None
    try:
        if ('%Y-%m-%dT%H:%M:%S' in format_string): #iso format fails using the library
            datetime = dateutil.parser.parse(date)
        else:
            datetime = dateparser.parse(date,
                                        date_formats=[format_string],
                                        languages=languages)
        new_date = datetime.strftime('%Y-%m-%d')
    except Exception, e:
        print str(e)
        print "Date parsing failed! Extracted_date was: %s" % date
    return new_date

def parse_float(float_str, locale='en'):
    float_str = re.sub(r'[^0-9,\.]', '', float_str)
    #cleaning some trash. ex: "600,-" - MediaMarkt!
    try:
        return parse_decimal(float_str, locale)
    except NumberFormatError, e:
        pass

def get_page(url, project_conf):
    """
    Perform a single request outside of using the standard scrapy requests
    :param url: the url to request
    :param project_conf: the project configuration to get the proxy from
    :return: data from the requested website
    """

    use_tor = False
    scraping_proxy = None

    # Pull out the proxy settings first (if we have them)
    if project_conf.has_section("PROXY"):
        if project_conf.has_option("PROXY", "use_tor"):
            use_tor = project_conf.getboolean("PROXY", "use_tor")

        if project_conf.has_option("PROXY", "scraping_proxy"):
            scraping_proxy = project_conf.get("PROXY", "scraping_proxy")

    # Set the proxy up if we do
    if use_tor and scraping_proxy:
        proxy = urllib2.ProxyHandler({'http': scraping_proxy,
                                      'https': scraping_proxy})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)

    # Request the page and nab some "dataz". I believe that's the term the
    # youth of today use...
    file = urllib2.urlopen(url)
    data = file.read()
    file.close()

    # Be nice and give it to the person who asked for it
    return data

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever

def remove_suffix(text, prefix):
    if text.endswith(prefix):
        return text[:-len(prefix)]
    return text  # or whatever

def first_or_empty(list):
    if len(list) > 0:
        return list[0]
    return ""

def unescape_js_string(s):
    '''
    Remove extra backslashes used for escaping characters in a string containing JavaScript
    :param s: a string containing JavaScript code
    :return: an unescaped string
    '''
    return s.encode('utf-8').decode('unicode-escape').replace('\\/', '/')

def js_object_string_to_python_json(s):
    '''
    Convert a JavaScript Object string literal to a Python JSON object ready to be parsed
    :param s: a JavaScript Object string literal to be converted
    :return: a Python JSON object ready for product and review info collection
    '''
    try:
        # Quote keys of Javascript object
        json_text = re.sub('([{,])([^{:\s"]*):', lambda m: '%s"%s":' % (m.group(1), m.group(2)), s)
        # Quote variables of Javascript object
        json_text = re.sub(r'((?<![\\])":)([^"{\[,\s]+),', lambda m: '%s"%s",' % (m.group(1), m.group(2)), json_text)
        # this probably does not cover all json invalid escape cases, but it should work most of the time
        json_text = json_text.replace("\\'", "'").replace('\\/', '/')

        return json.loads(json_text)
    except:
        return None
