# Ansible Collections Mirroring

* https://pulpproject.org

```
pulp user create --username mirror --password Ahphee6a
pulp user role-assignment add \
    --role ansible.ansibledistribution_viewer \
    --username mirror  \
    --object ""
pulp ansible repository create --name "mirror"
pulp ansible remote -t "collection" create \
    --name "ansible-galaxy" \
    --url "https://galaxy.ansible.com/" \
    --requirements @ansible-galaxy.yml
pulp ansible repository sync \
    --name "mirror" \
    --remote "ansible-galaxy"
pulp ansible distribution create \
    --name "mirror" \
    --base-path "mirror" \
    --repository "mirror"
```

## Add new collections

```
pulp ansible remote -t "collection" update \
    --name "ansible-galaxy" \
    --url "https://galaxy.ansible.com/" \
    --requirements @ansible-galaxy.yml
```

## Sync

```
pulp ansible repository sync \
    --name "mirror" \
    --remote "ansible-galaxy"
pulp ansible distribution destroy --name mirror
pulp ansible distribution create \
    --name "mirror" \
    --base-path "mirror" \
    --repository "mirror"
```
