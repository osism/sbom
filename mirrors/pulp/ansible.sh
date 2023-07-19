#!/usr/bin/env bash

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
