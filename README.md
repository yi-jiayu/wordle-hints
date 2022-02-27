Wordle Hint App
---------------

The corpus and word ranking functions are stored in `data_source.py`.

To run the app, run `python main.py`.

## Docker commands

```shell
# assuming from src directory

# dash app is deprecated
# docker image build -t danielbok/wordle-dash-app .

# To build api server image
docker image build -t danielbok/wordle-api-server -f api.Dockerfile .

cd web
docker image build -t danielbok/wordle-web -f web.Dockerfile .

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
```