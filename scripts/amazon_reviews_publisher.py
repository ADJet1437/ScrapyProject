#!/usr/bin/env python
import re
import socket
from datetime import datetime
from os import listdir, unlink
from os.path import isfile, join, getsize
from alascrapy.lib.conf import get_project_conf
from alascrapy.lib.mq.mq_publisher import MQPublisher

amazon_source_ids = [230492, 263862, 263863, 39000015, 1, 3140]

def is_file_empty(fpath):
    return isfile(fpath) and getsize(fpath) == 0

def main():
    project_conf = get_project_conf()
    finish_path = project_conf.get("OUTPUT", 'finished_directory')
    amazon_path = project_conf.get("OUTPUT", 'amazon_directory')

    filename_re = "([\w_]+)-(\d{8}_\d{6})-(\d+)\.csv"
    host_re = "\w+(\d{3})"
    files = [f for f in listdir(finish_path) if isfile(join(finish_path, f))]
    processed_times = set()
    filenames = {}

    hostname = socket.gethostname()
    host_match = re.match(host_re, hostname)
    try:
        host_suffix = host_match.group(1)
    except:
        pass
    #    raise Exception("Illegal hostname %s" % hostname )



    for file in files:
        match = re.match(filename_re, file)
        if not match:
            print("bad file name! %s" % file)
            continue

        timestamp = match.group(2)
        source_id = match.group(3)

        processed_key = "%s-%s" % (source_id, timestamp)

        if int(source_id) not in amazon_source_ids:
            continue

        if processed_key in processed_times:
            continue

        new_timestamp = datetime.now().strftime('%Y%m%d_%H')
        #new_timestamp = new_timestamp + ("0%s" % host_suffix)
        new_timestamp = new_timestamp + ("0000")
        for filetype in ['reviews', 'products', 'product_id']:
            source_filesnames = filenames.get(source_id, {})
            new_filename = source_filesnames.get(filetype, None)
            if not new_filename:
                new_filename = "%s-%s-%s.csv" % (filetype, new_timestamp, source_id)

            new_filepath = join(amazon_path, new_filename)
            source_filesnames[filetype] = new_filepath
            filenames[source_id] = source_filesnames

            old_filename = "%s-%s-%s.csv" % (filetype, timestamp, source_id)
            old_filepath = join(finish_path, old_filename)
            has_header = isfile(new_filepath) and getsize(new_filepath) > 0
            #if file and it is not empty exists then has header
            if isfile(old_filepath):
                with open(new_filepath, "a+") as new_file:
                    with open(old_filepath, 'r') as old_file:
                        if has_header:
                            try:
                                next(old_file)
                            except StopIteration, e:
                                pass
                        for line in old_file:
                             new_file.write(line)
                unlink(old_filepath)
        processed_times.add(processed_key)

    # send to load
    #publisher = MQPublisher(project_conf, 'LOAD')
    #for source_id in filenames:
    #    source_filesnames = filenames.get(source_id, {})
    #    if source_filesnames:
    #        source_file_list = source_filesnames.values()
    #        publisher.send_load_message(source_file_list)

if __name__ == "__main__":
    main()