# Container Registry Mirroring

* https://github.com/containers/skopeo

```
skopeo login --username 'robot$XXX' osism.harbor.regio.digital
```

```
skopeo sync -s yaml -d docker images-ceph.yaml osism.harbor.regio.digital/osism
skopeo sync -s yaml -d docker images-manager.yaml osism.harbor.regio.digital/osism
skopeo sync -s yaml -d docker images-openstack-release.yaml osism.harbor.regio.digital/kolla/release
skopeo sync -s yaml -d docker images-openstack.yaml osism.harbor.regio.digital/kolla
```
