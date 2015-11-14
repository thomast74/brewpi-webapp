# oinkbrew_webapp
Oink Brew API Service Layer and Web Application for configuring BrewPis with Oink Brew Firmware, controlling and viewing brews and fermentations.


## Installation

###1. InfluxDB on Raspberry Pi  
  
####a) install gvm
> sudo apt-get install bison  
> bash < <(curl -s -S -L https://raw.githubusercontent.com/moovweb/gvm/master/binscripts/gvm-installer)  
> source ~/.gvm/scripts/gvm  

####b) follow https://github.com/influxdb/influxdb/blob/master/CONTRIBUTING.md#installing-go
> gvm install go1.5  
> vm use go1.5 --default  

####c) install fpm
> sudo apt-get install ruby-dev rpm  
> sudo gem install fpm  

####d) follow the first code snippet of https://github.com/influxdb/influxdb/blob/master/CONTRIBUTING.md#project-structure
> export GOPATH=$HOME/gocodez  
> mkdir -p $GOPATH/src/github.com/influxdb  
> cd $GOPATH/src/github.com/influxdb  
> git clone https://www.github.com/influxdb/influxdb
  
####e) Create installation package
> cd influxdb  
> NIGHTLY_BUILD=false  
> ./package.sh 0.9.4

####f) Install package
> sudo dpkg -i influxdb_0.9.4_armhf.deb  

####g) Start influxdb
> sudo update-rc.d influxdb defaults  
> sudo update-rc.d influxdb enable  
> sudo /etc/init.d/influxdb start  

####h) Create database
> /opt/influxdb/influx  
> CREATE DATABASE oinkbrew  
> exit  

###2. RabbitMQ

####a) Install RabbitMQ
> sudo apt-get install rabbitmq-server  

####b) Configure RabbitMQ
> sudo rabbitmqctl add_user oink funbrewing  
> sudo rabbitmqctl add_vhost oinkbrew  
> sudo rabbitmqctl set_permissions -p oinkbrew oink ".*" ".*" ".*"  

####c) Change configuration if disk free space is less than 1GB
Create or edit `/etc/rabbitmq/rabbitmq.config`  
  
Add the following line or change existing: `[{rabbit, [{disk_free_limit, 500000000}]}].`

Important is that the `disk_free_limit` is less than the current disk free space of your disk.
If not celery will not startup.

> sudo service rabbitmq-server restart  

###3. OinkBrew Listener

####a) Installation
For installation see: [OinkBrew Listener Installation](https://github.com/thomast74/oinkbrew_listener/blob/master/README.md)    

####b) Configuration
> sudo /etc/init.d/oinkbrew_listener stop  
  
Edit `/etc/oinkbrew/oinkbrew_listener.cfg`  
    Change `post-url` to match your Django deployment  
    Change `log-level` to `INFO`  

####c) Enable and start service
> sudo /etc/init.d/oinkbrew_listener start  

###4. OinkBrew Web App

####a) Install application requirements


sudo addgroup --system "oinkbrew" --quiet  
sudo useradd -N -m --system -g oinkbrew -s /bin/bash oinkbrew  

sudo apt-get install python-dev python-pip apache2  

sudo chown oinkbrew:oinkbrew -R /opt/oinkbrew/oinkbrew_webapp

cd /opt/oinkbrew/oinkbrew_webapp

sudo pip install -r requirements.txt

####b) Celery setup
  
cd /opt/oinkbrew/oinkbrew_webapp

sudo cp default/celeryd /etc/default/
sudo cp init.d/celeryd /etc/init.d/
sudo chmod +x /etc/init.d/celeryd
sudo update-rc.d celeryd defaults
sudo update-rc.d celeryd enable

sudo service celeryd start

####c) Configure apache2

sudo apt-get install libapache2-mod-proxy-html libapache2-mod-wsgi  

Change /etc/apache2/envvars:

export APACHE_RUN_USER=oinkbrew
export APACHE_RUN_GROUP=oinkbrew

Change apache2.conf

KeepAlive Off


sudo cp apache2/sites-available/000-default.conf /etc/apache2/sites-available
sudo cp apache2/sites-available/default-ssl.conf /etc/apache2/sites-available

sudo a2enmod proxy_html
sudo a2enmod proxy_http
sudo a2enmod wsgi

sudo a2ensite 000-default.conf
sudo a2ensite default-ssl.conf

sudo service apache2 restart


###5. Grafana

####a) Install latest nodejs
> sudo su -c 'echo "deb https://deb.nodesource.com/armv6l-node/ weezy main" >> /etc/apt/sources.list'  
> curl -s https://deb.nodesource.com/gpgkey/nodesource.gpg.key | sudo apt-key add -  
> sudo apt-get update  
> sudo apt-get install nodejs  

####b) Get and build Grafana
> export GOPATH=/home/pi/gocodez  
> mkdir -p $GOPATH/src/github.com/grafana  
> cd $GOPATH/src/github.com/grafana  
> git clone https://www.github.com/grafana/grafana  
> cd $GOPATH/src/github.com/grafana/grafana  
> go run build.go setup  
> $GOPATH/bin/godep restore  
> go run build.go build  
  
> sudo npm config set registry http://registry.npmjs.org/  
> sudo npm install  
> sudo npm install -g grunt-cli  
> grunt  

####c) Setup Grafana application folder
> sudo addgroup --system "grafana" --quiet  
> sudo useradd -N -M --system -g oinkbrew -s /bin/false grafana  

> sudo mkdir /opt/grafana  
> sudo cp -R bin/ /opt/grafana  
> sudo cp -R conf/ /opt/grafana  
> sudo cp -R public/ /opt/grafana  
> sudo cp -R vendor/ /opt/grafana  
> sudo cp packaging/deb/init.d/grafana-server /etc/init.d/  
> sudo cp packaging/deb/default/defaults.ini /etc/default/grafana-server  
> sudo chown -R grafana:grafana /opt/grafana  

####d) Change configuration file
Edit `/etc/default/grafana-server`:  
  Change `GRAFANA_HOME=/opt/grafana`  
  Change `CONF_DIR=/opt/grafana/conf`  
  Change `CONF_FILE=/opt/grafana/conf/defaults.ini`
  
Edit `/etc/init.d/grafana-server`:  
  Change `GRAFANA_HOME=/opt/grafana`  
  Change `DAEMON=/opt/grafana/bin/$NAME`  

####e) Enable and start service
> sudo update-rc.d grafana-server defaults  
> sudo update-rc.d grafana-server enable  
> sudo /etc/init.d/grafana-server start  

## Getting Started  

curl -X POST http://192.168.2.11/api/brewpis/54ff6c066678574929420567/reset/
