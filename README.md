elasticsearch*
==============
(aka elasticsearch-star)

Starcluster plugin to install and configure an elasticsearch cluster.

Introduction
------------

Starcluster is a command line tool for spinning up clusters of ec2 nodes quickly, great for some
analytics / data chomping. A great introductory screencast is here:
<http://youtu.be/vC3lJcPq1FY>

Elasticsearch is a distributed search engine with smart clustering capabilities:
<http://www.elasticsearch.org/videos/2010/02/07/es-introduction.html>

The elasticsearch* plugin makes it dead easy to start a starcluster with elasticsearch on top
in 2-3 minutes.

This can be great for testing all sorts of things like:

- which instance size is optimal for my queries? (e.g. m1.xlarge or c1.xlarge)
- what elasticsearch configuration parameters work best for my queries?
- how does elasticsearch version x compare to version y?
- how many shards should I have?
- how much will it cost to meet performance requirement X?
- training large scale machine learning on a spot instance priced elasticsearch cluster
- and many more...

The elasticsearch cluster will be configured with the cloud-aws plugin to
perform auto discovery.

Just add data<sup>TM</sup>.

Installation
------------

    sudo pip install starcluster
    git clone git://github.com/barnybug/elasticsearch-star.git
    cp elasticsearch.py ~/.starcluster/plugins
    cp config.example ~/.starcluster/config
    emacs/vim ~/.starcluster/config # configure your EC2 keys and clusters
    starcluster start -s 5 smallcluster # start a 5 node cluster

Once the cluster is provisioned, the http url of elasticsearch (the one on master) will be printed
back to the console. This usually take about 2 minutes.

When you are done with the cluster:

    starcluster terminate smallcluster

Configuration
-------------

A minimalist configuration is included in config.example - simply copy to ~/.starcluster/config
and fill out your keys (as above).

If you already have an existing starcluster configuration, then you just need to:

Enable the plugin - add the following to your .starcluster/config:

    PLUGINS = elasticsearchstar
    PERMISSIONS = elasticsearch

to each [cluster ...] section you wish to use the plugin with.

At the end of config add:

    [plugin elasticsearchstar]
    SETUP_CLASS = elasticsearchstar.Elasticsearch

    [permission elasticsearch]
    PROTOCOL = tcp
    FROM_PORT = 9200
    TO_PORT = 9200
    # CIDR_IP = <your_ip>/32
    # add this in to secure elasticsearch access

In your cluster section as you'll not be using SGE (the Sun
Grid Engine), you can set:

    DISABLE_QUEUE=TRUE
    
### Parameters:

The plugin can be configured by adding to the [plugin elasticsearchstar] section:

    version = 0.20.0.RC1
(optional) Set the version of elasticsearch to use. Defaults to 0.19.11.

    data_dir = /var/lib/elasticsearch
(optional) Set an alternative place to store data directory on the instance.
Defaults to /mnt/elasticsearch - i.e. on ephemeral storage.

    heap_size = 256
(optional) Set heap size in MB. The recommended amount of memory to allocate is
about 50% of the instance memory. This will be calculated by default to match
your instance size selected, but can be overridden with this parameter.

### Reconfiguration

If you change any of these parameters, you can reconfigure elasticsearch on the cluster by running:

    starcluster runplugin elasticsearchstar <clustername>


Elasticsearch Notes
-------------------

- Cluster name will match the starcluster name.
- Each node will be named to match the starcluster allocated node name, eg
  master, node001, etc.
- Elasticsearch will be allocated the suggested 50% of the instance memory,
  leaving the rest for disk buffers.
- The data directory will be set to /mnt/elasticsearch by default - the
  ephemeral storage on an instance. This is plentiful in size, but comes with
  the usual caveats of being volatile, so stopping or terminating the instances
  will lose the data.
- If you need your cluster data to survive stop/start, then change the data_dir
  parameter, you'll probably want to mount some EBS volumes too. But perhaps
  your use case is more intricate than transient throw-away clusters this plugin
  has in mind...
  

