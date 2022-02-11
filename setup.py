# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name         = 'alascrapy',
    version      = '1.0',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = alascrapy.settings']},
    install_requires=['scrapy==1.4.0',
                      'Twisted==22.1.0',
                      'service_identity',
                      'graypy==0.3.1',
                      'pika',
                      'MySQL-python==1.2.3',
                      'stem',
                      'selenium==3.3.1',
                      'fake-useragent==0.1.8',
                      'Pillow',
                      'xvfbwrapper',
                      'BeautifulSoup4',
                      'dateparser==0.6.0',
                      'python-dateutil==2.4.2',
                      'Babel',
                      'py2neo==2.0.8',
                      'xmltodict',
                      'jsonlib2',  #cleanser
                      'extruct==0.4.0',
                      'rdflib',
                      'js2xml==0.2.1',
                      'requests',
                      'langdetect==1.0.7',
                      'scrapy-crawlera==1.3.0'
                     ],
    package_data={"alascrapy": ["conf/alascrapy.conf",
                                "conf/sources_conf/*",
                                "fake_useragent_*.json"]},
    test_suite = "tests",
)
