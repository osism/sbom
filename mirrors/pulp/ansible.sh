#!/usr/bin/env bash

pulp ansible repository create --name "ansible-galaxy"

pulp ansible remote -t "collection" create \
    --name "ansible-galaxy" \
    --url "https://galaxy.ansible.com/" \
    --requirements @ansible-collections.yml
pulp ansible repository sync \
    --name "ansible-galaxy" \
    --remote "ansible-galaxy"

python3 ansible-roles.py

pulp ansible distribution create \
    --name "ansible-galaxy" \
    --base-path "ansible-galaxy" \
    --repository "ansible-galaxy"
