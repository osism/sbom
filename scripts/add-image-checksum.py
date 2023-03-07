#!/usr/bin/env python3

import io
import os
import subprocess

from loguru import logger
import json
import yaml

VERSION = os.environ.get("VERSION", "3.2.0")
LIST = os.environ.get("LIST", "openstack")

with open(os.path.join(VERSION, f"{LIST}.yml")) as fp:
    data = yaml.load(fp, Loader=yaml.SafeLoader)

images = data.get("images", {})
for image in images:
    logger.info(f"Processing {image['image']}")
    p = subprocess.Popen(
        f"skopeo inspect docker://{image['image']}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    p.wait()
    stdout = io.TextIOWrapper(p.stdout, encoding="utf-8")
    result = json.loads(stdout.read())
    image["digest"] = result["Digest"]

with open(os.path.join(VERSION, f"{LIST}.yml"), "w+") as fp:
    fp.write(yaml.dump(data))
