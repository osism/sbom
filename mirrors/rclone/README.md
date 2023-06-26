# Object Storage Mirroring

* https://github.com/rclone/rclone

Create a S3 credential with the OpenStack CLI:

```
openstack ec2 credentials create
openstack ec2 credentials list
```

Copy ``rclone.conf`` to ``$HOME/.config/rclone/rclone.conf``. Adjust source and destination
accordingly.

```
rclone sync source:openstack-image-gardenlinux destination:openstack-image-gardenlinux
rclone sync source:openstack-images destination:openstack-images
rclone sync source:openstack-ironic-images destination:openstack-ironic-images
rclone sync source:openstack-k8s-capi-images destination:openstack-k8s-capi-images
rclone sync source:openstack-octavia-amphora-image destination:openstack-octavia-amphora-image
rclone sync source:osism-node-image destination:osism-node-image
```
