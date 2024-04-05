#!/usr/bin/env python3

import subprocess

import yaml

with open("ansible-roles.yml", "r+") as fp:
    data = yaml.safe_load(fp)

for x in data:
    namespace, name = x.split(".")
    subprocess.run(
        f"pulp ansible remote -t role create --name {x} --url https://galaxy.ansible.com/api/v1/roles/?format=json&namespace__name={namespace}&repository__name={name}",
        shell=True,
    )
    subprocess.run(
        f"pulp ansible repository sync --name ansible_roles --remote role:{x}",
        shell=True,
    )
