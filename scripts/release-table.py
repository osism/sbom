#!/usr/bin/env python3

import os
from packaging import version

from loguru import logger
from tabulate import tabulate
from yaml import safe_load, YAMLError

RELEASE_A = os.environ.get("RELEASE_A", "5.0.0")
RELEASE_B = os.environ.get("RELEASE_B", None)

result = []
result_changed = []

with open(f"{RELEASE_A}/openstack.yml", "r") as fp:
    try:
        openstack_a = safe_load(fp)
    except YAMLError as e:
        logger.error(e)

if RELEASE_B:
    with open(f"{RELEASE_B}/openstack.yml", "r") as fp:
        try:
            openstack_b = safe_load(fp)
        except YAMLError as e:
            logger.error(e)

if not RELEASE_B:
    for image in openstack_a["versions"]:
        image_version = openstack_a["versions"][image]
        try:
            parsed_version = version.parse(image_version[:-9])
        except version.InvalidVersion:
            parsed_version = image_version[:-9]

        if not type(parsed_version) is str:
            release_version = ".".join([str(x) for x in list(parsed_version.release)])
        else:
            release_version = parsed_version

        result.append([image, release_version])

    print("\nVersions\n========\n\n")
    print(tabulate(result, headers=["service", "version"], tablefmt="rst"))

else:
    for image in openstack_a["versions"]:
        image_version_a = openstack_a["versions"][image]
        try:
            parsed_version_a = version.parse(image_version_a[:-9])
        except version.InvalidVersion:
            parsed_version_a = image_version_a[:-9]
        if not type(parsed_version_a) is str:
            release_version_a = ".".join(
                [str(x) for x in list(parsed_version_a.release)]
            )
        else:
            release_version_a = parsed_version_a

        try:
            image_version_b = openstack_b["versions"][image]
        except KeyError:
            next

        try:
            parsed_version_b = version.parse(image_version_b[:-9])
        except version.InvalidVersion:
            parsed_version_b = image_version_b[:-9]
        if not type(parsed_version_a) is str:
            release_version_b = ".".join(
                [str(x) for x in list(parsed_version_b.release)]
            )
        else:
            release_version_b = parsed_version_b

        if version.parse(release_version_b) > version.parse(release_version_a):
            result_changed.append([image, release_version_a, release_version_b])

        result.append([image, release_version_b])

    print("\n\nChanged versions\n================\n\n")
    print(
        tabulate(
            result_changed,
            headers=["service", f"{RELEASE_A}", f"{RELEASE_B}"],
            tablefmt="rst",
        )
    )
    print("\n\nVersions\n========\n\n")
    print(tabulate(result, headers=["service", "version"], tablefmt="rst"))
