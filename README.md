elasticsearch*
==============
(aka elasticsearch-star)

Starcluster plugin to install and configure an elasticsearch cluster.

Introduction
------------

Starcluster is a command line tool for spinning up clusters of ec2 nodes quickly, great for some
analytics / data chomping.

Elasticsearch is a distributed search engine with smart clustering capabilities.

The elasticsearch* plugin makes it dead easy to start a starcluster with elasticsearch on top
in 2-3 minutes.

This can be great for testing all sorts of things like:

- which instance size works best for my queries? (eg. more memory vs more cpu)
- what elasticsearch configuration parameters work best for my queries?
- how many shards should I have?
- how does elasticsearch version x compare to version y?
- how does performance change if I have 2x, 3x, etc more instances.
- running big scale machine learning training on a spot instance priced elasticsearch cluster
- and many more...

The elasticsearch cluster will be configured with the cloud-aws plugin to
perform auto discovery. Just add data<sup>TM</sup>.

Installation
------------
Currently as simple as:

    pip install starcluster
    cp elasticsearch.py ~/.starcluster/plugins
    cp config.example ~/.starcluster/config
    emacs/vim ~/.starcluster/config # configure your keys / cluster
    starcluster start -s 5 smallcluster # start a 5 node cluster

Once the cluster is provisioned, the http url of elasticsearch (the one on master) will be printed
back to the console.

Configuration
-------------

A minimalist configuration is included in config.example - simply copy to ~/.starcluster/config
and fill out your keys.

If you already have an existing starcluster configuration, then you just need to:

Enable the plugin - add the following to your .starcluster/config:

    PLUGINS = elasticsearch
    PERMISSIONS = elasticsearch

to each [cluster ...] section you wish to use the plugin with.

At the end of config add:

    [permission elasticsearch]
    PROTOCOL = tcp
    FROM_PORT = 9200
    TO_PORT = 9200
    
    [plugin elasticsearch]
    SETUP_CLASS = elasticsearch.Elasticsearch

### Parameters:

You can be thankful, currently there's just one optional configuration parameter...

    version = 0.19.11
(optional) Set the version of elasticsearch to use. Defaults to 0.19.11.

The elasticsearch cluster name will match the starcluster name.

Each elasticsearch node will be named to match the starcluster allocated node name,
eg master, node001, etc. The elasticsearch master will be assigned by elasticsearch, so 
may not correspond to the starcluster host named 'master', but usually you don't need to
worry about this!

