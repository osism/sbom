# Container Registry Mirroring

* https://github.com/containers/skopeo

```
skopeo login --username 'robot$XXX' TARGET.harbor.regio.digital
```

```
skopeo sync -s yaml -d docker images-ceph.yaml TARGET.harbor.regio.digital/osism
skopeo sync -s yaml -d docker images-manager.yaml TARGET.harbor.regio.digital/osism
skopeo sync -s yaml -d docker images-openstack-release.yaml TARGET.harbor.regio.digital/kolla/release
skopeo sync -s yaml -d docker images-openstack.yaml TARGET.harbor.regio.digital/kolla
```
