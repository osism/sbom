#!/usr/bin/env python3

import os
from packaging import version

from loguru import logger
from tabulate import tabulate
from yaml import dump, safe_load, YAMLError

RELEASE_A = os.environ.get("RELEASE_A", "5.0.0")
RELEASE_B = os.environ.get("RELEASE_B", None)

result = []

with open(f"{RELEASE_A}/openstack.yml", "r") as fp:
    try:
        openstack = safe_load(fp)
    except YAMLError as e:
        logger.error(e)

for image in openstack["versions"]:
    image_version = openstack["versions"][image]
    try:
        parsed_version = version.parse(image_version[:-9])
    except version.InvalidVersion:
        parsed_version = image_version[:-9]

    if not type(parsed_version) == str:
        release_version = ".".join([str(x) for x in list(parsed_version.release)])
    else:
        release_version = parsed_version

    result.append([image, release_version])

print(tabulate(result, headers=["service", "version"], tablefmt="rst"))
