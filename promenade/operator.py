from . import config, etcd, logging, kube, pki, renderer
import os
import subprocess

__all__ = ['Operator']


LOG = logging.getLogger(__name__)


class Operator:
    @classmethod
    def from_config(cls, *,
                    config_path,
                    hostname,
                    target_dir):
        return cls(hostname=hostname, target_dir=target_dir,
                   **config.load_config_file(config_path=config_path,
                                             hostname=hostname))

    def __init__(self, *, cluster_data, hostname, node_data, target_dir):
        self.cluster_data = cluster_data
        self.hostname = hostname
        self.node_data = node_data
        self.target_dir = target_dir

    def genesis(self, *, asset_dir=None):
        self.setup(asset_dir=asset_dir)
        self.expand_etcd_cluster()

    def join(self, *, asset_dir=None):
        self.setup(asset_dir=asset_dir)

    def setup(self, *, asset_dir):
        self.rsync_from(asset_dir)
        self.render()
        self.install_keys()

        self.bootstrap()

    def rsync_from(self, src):
        if src:
            LOG.debug('Syncing assets from "%s" to "%s".', src, self.target_dir)
            subprocess.run(['/usr/bin/rsync', '-r',
                            os.path.join(src, ''), self.target_dir],
                           check=True)
        else:
            LOG.debug('No source directory given for rsync.')


    def render(self):
        r = renderer.Renderer(node_data=self.node_data,
                              target_dir=self.target_dir)
        r.render()

    def install_keys(self):
        pki.generate_keys(initial_pki=self.cluster_data['pki'],
                          target_dir=self.target_dir)

    def bootstrap(self):
        LOG.debug('Running genesis script with chroot "%s"', self.target_dir)
        subprocess.run([os.path.join(self.target_dir, 'usr/sbin/chroot'),
                        self.target_dir,
                        '/bin/bash', '/usr/local/bin/bootstrap'],
                       check=True)

    def expand_etcd_cluster(self):
        for node in self.node_data['etcd']['boot_order'][1:]:
            LOG.info('Waiting for Node "%s" to be Ready', node['hostname'])
            kube.wait_for_node(node['hostname'])
            LOG.info('Node "%s" Ready.  Adding to etcd cluster.', node['hostname'])
            etcd.add_member(self.genesis_etcd_pod, node['hostname'], port=2380)
        LOG.info('Finished expanding etcd cluster.')

    @property
    def genesis_etcd_pod(self):
        return 'kube-etcd-%s' % self.node_data['genesis']['hostname']
