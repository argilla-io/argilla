# Lighter Elasticsearch instance when developing with Rubrix

Elasticsearch when downloaded can consume by default nearly half of the RAM on your local machine. 🥶🥶

If you prefer to run a local instance of elasticsearch (without Docker), here are the steps to lower its memory consumption on a Debian-based distro (i.e. Mint or Ubuntu).

This tutorial was tested on a WSl Ubuntu 20.04.

## Check if you have OpenJDK 11

First, make sure you have OpenJDK 11 installed, which usually comes pre-installed with Ubuntu. To check if you have it run in terminal:

    java -version

if you don't have it installed you can follow this simple tutorial for debian-based distros: 
    https://www.digitalocean.com/community/tutorials/how-to-install-java-with-apt-on-ubuntu-20-04

Ok, so after confirming we have OpenJDK installed we can start with elasticsearch download and configuration.

## Download and install Elasticsearch:

    curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
    echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
    sudo apt update
    sudo apt install elasticsearch

## Configuration of Elasticsearch

To access the elasticsearch yml file:

    sudo nano /etc/elasticsearch/elasticsearch.yml

Uncomment 'network.host' and change it to 'localhost' for local machine: 

    network.host: localhost

Check if elasticsearch starts:

    sudo systemctl start elasticsearch

or use 'service' if you don't have 'systemctl' which is common on WSL distros)

    sudo service elasticsearch start

Great, if it starts without a problem we can now shut it down to configure memory rquirements:

    sudo systemctl stop elasticsearch 
    
or 

    sudo service elasticsearch stop

Let's create a new file called 'memory.options' in the 'jvm.options.d' directory so we can define memory requirements when an ES instance starts:
BTW, I chose to name the file 'memory' but you can choose whatever name you want as long as the file extension is `.options` :

    sudo nano /etc/elasticsearch/jvm.options.d/memory.options

In the file, add the mimium and maxium memory requirements (I decided on 1G):

    -Xms1g
    -Xmx1g

Great, we are done! Now restart elasticsearch and your RAM should be much lower!

## Resources for further hacking

https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-elasticsearch-on-ubuntu-20-04

https://www.elastic.co/guide/en/elasticsearch/reference/current/advanced-configuration.html#set-jvm-heap-size
