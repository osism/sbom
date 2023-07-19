#!/usr/bin/env python3

import subprocess

import yaml

with open("ubuntu.yml", "r+") as fp:
    data = yaml.safe_load(fp)

for x in data:
    subprocess.run(f"pulp deb repository create --name {x['name']}", shell=True)

    if "component" in x:
        subprocess.run(
            f"pulp deb remote create --name {x['name']} --url {x['url']} --distribution {x['distribution']} --component {x['component']} --architecture amd64",
            shell=True,
        )
    else:
        subprocess.run(
            f"pulp deb remote create --name {x['name']} --url {x['url']} --distribution {x['distribution']}",
            shell=True,
        )
    subprocess.run(
        f"pulp deb repository sync --name {x['name']} --mirror --remote {x['name']}",
        shell=True,
    )
    subprocess.run(
        f"pulp deb publication -t verbatim create --repository {x['name']}", shell=True
    )
    subprocess.run(
        f"pulp deb distribution create --name {x['name']} --base-path {x['name']} --repository {x['name']}",
        shell=True,
    )
