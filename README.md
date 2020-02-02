# Gitlab alaScrapy Repository

Imported November 2nd, 2017 (by Erik)


### environment setup

#### fabric
get the ver 1.14.0 of fabric to be able to deploy

```bash
pip install fabric==1.14.0
```

### How to run tests locally
This document is pretty useful for instructions on how to deploy and test:
https://docs.google.com/document/d/1TSXLl7VK4rvOQUMmE3DDU6NJD54Oi2jUTWv2zXvTrYI/edit#


#### With a virtualenv (without docker)
```bash
# Create directories on local computer and give it permissions for storing CSV files and log files
sudo mkdir /var/local/load && sudo chmod -R 777 /var/local/load
sudo mkdir /var/log/alaScrapy && sudo chmod -R 777 /var/log/alaScrapy

# Make sure the conf is setup and valid
cd <path-to-alascrapy-project>
ln -s alascrapy/conf/alascrapy.conf.live alascrapy/conf/alascrapy.conf  # Tried to setup the alascrapy.conf.dev as conf file but didn't work

# Create a venv in the project dir
virtualenv -p python2.7 venv

# Activate the venv
source venv/bin/activate

# Install deps
(venv)$ pip install -r requirements.txt

# Run this command with the source_id
(venv)$ scrapy crawl mediamarkt_it
(venv)$ scrapy crawl valuechecker_net
(venv)$ scrapy crawl ...
```


### Original README file contents below

#### To build a the alaScrapy image:

```bash
sudo docker build --force-rm --rm -t alatest/alascrapy:0.1 docker/docker_files/docker_alascrapy/
```

#### To run a spider:

```bash
docker run --dns=192.168.17.1 \
            -v /home/leonardo/workspace/alaScrapy/:/alaScrapy \
            -v /var/log/alaScrapy:/var/log/alaScrapy \
            -v /var/local/load/:/var/local/load/ \
            alatest/alascrapy:0.1 scrapy crawl test_de

docker-compose run alascrapy scrapy crawl cnet_us
```

#### TODO:
- Separate apache from alaScrapy image
- Dockerize Neo4j
