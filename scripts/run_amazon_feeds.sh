#!/usr/bin/env bash

pushd `dirname $0` > /dev/null
PROJECT_PATH=`pwd -P`
popd > /dev/null

cd $PROJECT_PATH/..
PATH=$PATH:/usr/local/bin
export PATH

scrapy crawl amazon_de_csv
scrapy crawl amazon_fr_csv
scrapy crawl amazon_it_csv
scrapy crawl amazon_uk_csv
scrapy crawl amazon_api_com
