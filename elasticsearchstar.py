from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log
from starcluster import exception
import string
import os
import re
import math

"""Starcluster plugin to install and configure an elasticsearch cluster.

The elasticsearch cluster will be configured with the cloud-aws plugin to
perform auto discovery.

The elasticsearch cluster name will match the starcluster name.

Each elasticsearch node will be named to match the starcluster allocated node name,
eg master, node001, etc.

Parameters:
version = 2.3.5
- set the version of elasticsearch to use. Defaults to 2.3.5.
"""

SCRIPT = '''
#!/bin/bash

set -ex

# change to directory of script
cd $(dirname $0)

# record to log
exec > setup.log 2>&1

echo '** starcluster elasticsearch setup script **'

elasticsearch_deb_url=https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-%%version.deb
# store files under starcluster nfs share so only downloaded once
debfile=/home/sgeadmin/elasticsearch-%%version.deb

# use already downloaded version if present
if [ -e $debfile ]; then
  echo "** skipping download, using existing $debfile"
else
  echo "** downloading $debfile"
  wget -q $elasticsearch_deb_url -O $debfile
fi

echo "** installing $debfile"
dpkg --force-confold -i $debfile
# installing the deb attempts to start elasticsearch, this is expected to fail
# as the cloud-aws plugin mentioned in configuration is not present yet. next...

echo "** installing cloud plugin"
/usr/share/elasticsearch/bin/plugin install -b cloud-aws

echo "** creating data dir"
mkdir -p %%data_dir
chown elasticsearch:elasticsearch %%data_dir

echo '** starting elasticsearch'
service elasticsearch start
'''

ELASTICSEARCH_YML = '''
cluster.name: %%clustername
node.name: %%nodename
cloud:
    aws:
        access_key: '%%access_key'
        secret_key: '%%secret_key'
        region: '%%region'
    node:
        auto_attributes: true
discovery:
    type: ec2
    ec2:
        groups: '%%security_group'
'''

ELASTICSEARCH_CONF = '''
# Heap Size
ES_HEAP_SIZE=%%heap_size

# ElasticSearch data directory
DATA_DIR=%%data_dir
'''

class Template(string.Template):
    delimiter = '%%'

re_valid_version = re.compile(r'^\d\.\d+\.\d+(\.RC\d+)?$')
 
class Elasticsearch(ClusterSetup):
    """
    Installs and configures an elasticsearch cluster on starcluster
    """
    def __init__(self, version='2.3.5', data_dir=None, heap_size=None):
        if not re_valid_version.match(version):
            raise exception.ValidationError('Elasticsearch version should be format x.y.z[.RCn]: %s' % version)
        self.version = version
        self.data_dir = data_dir or '/mnt/elasticsearch'
        self.heap_size = heap_size
 
    def run(self, nodes, master, user, user_shell, volumes):
        params = self._params(master)
        for node in nodes:
            self._setup(node, params)
          
        log.info('** Your elasticsearch cluster is configured, check:')
        log.info('http://%s:9200/_cluster/health' % master.dns_name)

    def _params(self, node):
        # template parameters common to all nodes
        clustername = node.parent_cluster.name.replace('@sc-', '')
        return dict(
            version=self.version,
            clustername=clustername,
            access_key=node.ec2._conn.aws_access_key_id,
            secret_key=node.ec2._conn.aws_secret_access_key,
            region=node.ec2._conn.region.name,
            security_group=node.groups[0].name,
            data_dir=self.data_dir)

    def _setup(self, node, params):
        log.info("Installing elasticsearch on %s" % node.alias)
          
        tmpdir = '/tmp/elasticsearch'
          
        # upload templated files
        params = params.copy()
          
        # node specific parameters
        params['nodename'] = node.alias
        if self.heap_size:
            # user specified heap size
            heap_size = self.heap_size
        else:
            # memory size is set to 50% of node memory (minus 128M for OS etc), rounded up to nearest 128m
            # t1.micro 638.0  => 256m
            # m1.small 1657.0 => 768m
            # etc
            heap_size = int(math.ceil((node.memory-128) / 2.0 / 128) * 128)
        log.info("Setting heap size to %sm" % heap_size)
        params['heap_size'] = '%sm' % heap_size

        setup_sh = tmpdir+'/setup.sh'
        self._template(node, SCRIPT, setup_sh, params)
        self._template(node, ELASTICSEARCH_YML, '/etc/elasticsearch/elasticsearch.yml', params)
        self._template(node, ELASTICSEARCH_CONF, '/etc/default/elasticsearch', params)

        # run setup.sh
        node.ssh.chmod(0755, setup_sh)
        node.ssh.execute(setup_sh)
        log.info("Finished installation on %s" % node.alias)
      
    def _template(self, node, template, filename, params):
        content = Template(template).substitute(params)
        dirname = os.path.dirname(filename)
        node.ssh.execute('mkdir -p %s' % dirname)
        fout = node.ssh.remote_file(filename)
        print >>fout, content
        fout.close()

    def on_add_node(self, node, nodes, master, user, user_shell, volumes):
        params = self._params(master)
        self._setup(node, params)
