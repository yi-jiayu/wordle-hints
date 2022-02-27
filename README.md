Wordle Hint App
---------------

The corpus and word ranking functions are stored in `data_source.py`.

To run the app, run `python main.py`.

## Docker commands

```shell
# assuming from src directory

# To build api server image
cd wordle_api
docker image build -t danielbok/wordle-api-server:latest . & docker image push danielbok/wordle-api-server:latest

cd web
docker image build -t danielbok/wordle-web:latest . & docker image push danielbok/wordle-web:latest

# To test run the full service
docker-compose -p wordle up --no-build -d
```

## DigitalOcean Droplet setup

```shell
# installs the DO console so you can run commands on the site
wget -qO- https://repos-droplet.digitalocean.com/install.sh | sudo bash

# update existing list of packages
sudo apt update

# Installs docker
sudo apt install docker.io

# Install docker-compose, see https://docs.docker.com/compose/install/
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```