ELK Setup
=========

ELK is the short term for a software compilation used by BoardFarm to store, process and visualize test results.
ELK consists of three tools:

* Elasticsearch
* Logstash
* Kibana

For this basic setup guide, we won't even need Logstash as the results are already stored in the correct format in the Elasticsearch database.

Installation
------------

This guide was written for Ubuntu 16.04 LTS and the following versions of Elasticsearch and Kibana:

* Elasticsearch 2.3.3
* Kibana 4.5.1

If you follow this guide and you can't get it working with newer versions, you should try again with these versions.

### Prerequisites

Elasticsearch and Logstash require Java. Elasticsearch recommends Oracle Java 8 but I had no issues using OpenJDK 8. Use whatever you prefer, I'll use OpenJDK in this guide.

    apt-get install -y openjdk-8-jre openjdk-8-jdk

Now that we've installed Java, we can go on with Elasticsearch.

### Installing Elasticsearch

We'll just download the Elasticsearch Debian package and install it:

    wget https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/deb/elasticsearch/2.3.3/elasticsearch-2.3.3.deb
    dpkg -i ./elasticsearch-2.3.3.deb

You probably want Elasticsearch to automatically start every time you reboot your machine:

    systemctl enable elasticsearch
    
Now let's edit the Elasticsearch configuration to restrict access from anywhere except the host itself:

    nano /etc/elasticsearch/elasticsearch.yml

Look for a line containing 'network.host' and uncomment it. Set the value to 'localhost':

    network.host: localhost

This will only allow the machine itself to access Elasticsearch on port 9200. Otherwise, anyone with network access to the machine could access your stored data or shut down the Elasticsearch server.

Finally, restart Elasticsearch to apply the changed settings:

    systemctl restart elasticsearch

### Installing Kibana

Kibana is available as a 32-bit package and a 64-bit package, I'm using the 64-bit package in this guide:

    wget https://download.elastic.co/kibana/kibana/kibana_4.5.1_amd64.deb
    dpkg -i ./kibana_4.5.1_amd64.deb

As we did with Elasticsearch, we'll make Kibana automatically start on bootup:

    systemctl enable kibana

You should now be able to access the Kibana webinterface on port 5601. Before visiting the webinterface for the first time, we want to store some data in the Elasticsearch database so Kibana has something to work with when we start it for the first time.

### Configuring BoardFarm

We need to tell BoardFarm to store the data in the Elasticsearch database by specifying the server address in BoardFarm's `config.py`. In this guide, I'm running BoardFarm, Elasticsearch and Kibana on the same host, so I'll use 'localhost' as the server address:

    elasticsearch_server = 'localhost'

You should then run a few BoardFarm tests to store some data in the Elasticsearch database. After running the tests, you should see something like this at the end of the output:

    Elasticsearch: Data stored at localhost boardfarm-2016.07.05/bft_run/AVW6ozxZoiJNDeD5bFyj

Now, we have data to work with.

### Specifying an index pattern in Kibana

When visiting the Kibana webinterface for the first time, you'll have to specify an index pattern so Kibana knows which logfiles to analyze. BoardFarm stores its data in the format boardfarm-\<yyyy.mm.dd>, so we'll tell Kibana to use 'boardfarm-\*' as the index pattern.
Kibana should then automatically recognize your existing database entries and suggest '@timestamp' as the time-field name.
Click 'create' and you're good to go. You should now see a table with a number of fields, e.g. 'board_type' or 'tests_total'.

*Note: If you now run other testcases with new field names, you'll have to click the 'refresh field list' button at the top of the page, otherwise the new fields won't be displayed.*

You can now go to the 'Discover' page to see your log entries or to the 'Visualize' page to create new visualizations.
