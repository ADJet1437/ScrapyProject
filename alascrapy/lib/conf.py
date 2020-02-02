import ConfigParser
import StringIO
import json
import pkgutil
import os, sys

from os.path import isfile, join, dirname

def get_project_conf():
    """ Returns a ConfigParser Object with the contents of
        conf/alascrapy.conf.

        Arguments:
            project_path -- Realpath of the project's base directory
    """
    
    conf = pkgutil.get_data('alascrapy','conf/alascrapy.conf')
    conf_fp = StringIO.StringIO(conf)

    config_parser = ConfigParser.SafeConfigParser(
        {'graylog_host': "localhost",
         'graylog_port': "12201",
         'log_level': "INFO"})
    config_parser.readfp(conf_fp)
    return config_parser


def get_source_conf(spider_name):
    source_file = 'conf/sources_conf/%s.json' % spider_name
    source_conf = pkgutil.get_data('alascrapy', source_file)
    if source_conf:
        return json.loads(source_conf)
    else:
        return None

def update_source_conf(spider_name, source_conf):
    source_file = 'conf/sources_conf/%s.json' % spider_name
    d = os.path.dirname(sys.modules["alascrapy"].__file__)
    with open(os.path.join(d, source_file), 'w') as outfile:
        json.dump(source_conf, outfile, indent=4)