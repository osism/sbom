#!/usr/bin/env bash

# collections

pulp ansible repository create --name "ansible_collections"

pulp ansible remote -t "collection" create \
    --name "ansible_collections" \
    --url "https://galaxy.ansible.com/" \
    --requirements @ansible-collections.yml

pulp ansible repository sync \
    --name "ansible_collections" \
    --remote "ansible_collections"

pulp ansible distribution create \
    --name "ansible_collections" \
    --base-path "ansible_collections" \
    --repository "ansible_collections"

# roles

pulp ansible repository create --name "ansible_roles"

python3 ansible-roles.py

pulp ansible distribution create \
    --name "ansible_roles" \
    --base-path "ansible_roles" \
    --repository "ansible_roles"
