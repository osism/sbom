#!/usr/bin/env bash

pulp ansible repository create --name "ansible"

pulp ansible remote -t "collection" create \
    --name "ansible" \
    --url "https://galaxy.ansible.com/" \
    --requirements @ansible-collections.yml
pulp ansible repository sync \
    --name "ansible" \
    --remote "ansible"

python3 ansible-roles.py

pulp ansible distribution create \
    --name "ansible" \
    --base-path "ansible" \
    --repository "ansible"
