elasticsearch-star
==================

Starcluster plugin to install and configure an elasticsearch cluster.

The elasticsearch cluster will be configured with the cloud-aws plugin to
perform auto discovery.

The elasticsearch cluster name will match the starcluster name.

Each elasticsearch node will be named to match the starcluster allocated node name,
eg master, node001, etc.

Parameters:
version = 0.19.11
- set the version of elasticsearch to use. Defaults to 0.19.11.
