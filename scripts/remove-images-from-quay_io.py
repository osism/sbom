import yaml
import typer
import sys
from typing_extensions import Annotated
from typing import Any, Dict, List
import requests
from loguru import logger
import time
import os

level = "INFO"
log_fmt = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
    "<level>{message}</level>"
)

logger.remove()
logger.add(sys.stderr, format=log_fmt, level=level, colorize=True)


def warning_or_error(message: str, force: bool) -> None:
    """
    Shows a warning or exits with an error depending on --force flag
    """
    f = logger.warning if force else logger.error
    f(message)
    if not force:
        logger.info("Use --force to suppress this error")
        sys.exit(1)


def error_and_fail(message: str) -> None:
    logger.error(message)
    exit(1)


IMAGE_PREFIX = "osism.harbor.regio.digital/kolla/release/"
QUAY_PREFIX = "quay.io/osism"
QUAY_BASE_API = "https://quay.io/api/v1/repository/osism"
ADDITIONAL_REPOS = [
    "inventory-reconciler",
    "osism-ansible",
    "ceph-ansible",
    "osism-kolla-ansible",
]


def main(
    version: Annotated[str, typer.Option("--version", "-v", help="Version to remove")],
    force: Annotated[
        bool,
        typer.Option(
            "--force", "-f", help="Force even if script would error otherwise"
        ),
    ] = False,
    no_confirm: Annotated[
        bool,
        typer.Option(
            "--no-confirm", "-c", help="Disable explicit confirmation of every removal"
        ),
    ] = False,
    token: Annotated[
        str,
        typer.Option(
            "--token",
            "-t",
            help="Provide Quay.io bearer token via CLI. If not specified, use $QUAY_BEARER_TOKEN environment variable.",
        ),
    ] = None,
) -> None:

    logger.info(f"Specified version is '{version}'")

    token = processToken(token)

    precheck(version, force)

    if not no_confirm:
        logger.info(f"Running WITH confirmation!")
    else:
        logger.warning(f"Running WITHOUT confirmation! (wait 5 seconds)")
        time.sleep(5)

    imageList = getImageList(version)

    logger.info(f"Found {len(imageList)} image(s) for version '{version}'")

    for imageObject in imageList:
        imageName, imageVersion = getImageMeta(imageObject, force)
        imageRemoveURL = f"{QUAY_PREFIX}/{imageName}:{imageVersion}"

        if not getImageDecision(imageRemoveURL, no_confirm):
            logger.info(f"Skipping removal of '{imageRemoveURL}'")
            continue

        logger.info(f"Removing '{imageRemoveURL}'...")
        removeImage(token, imageName, imageVersion)

    logger.info("Done removing images")

    logger.info("Removing meta images...")

    for imageName in ADDITIONAL_REPOS:
        imageRemoveURL = f"{QUAY_PREFIX}/{imageName}:{version}"

        if not getImageDecision(imageRemoveURL, no_confirm):
            logger.info(f"Skipping removal of '{imageRemoveURL}'")
            continue

        logger.info(f"Removing '{imageRemoveURL}'...")
        removeImage(token, imageName, imageVersion)

    logger.info("Done removing meta images")


def processToken(token: str) -> str:
    """
    Parses the quay.io bearer token either via CLI or ENV
    """
    if token is not None:
        logger.info(f"Using bearer token provided via CLI")
    else:
        logger.info(
            f"Using bearer token provided via environment variable $QUAY_BEARER_TOKEN"
        )
        token = os.environ.get("QUAY_BEARER_TOKEN", "")

    if token is None or token == "":
        error_and_fail("Bearer token not provided or empty!")

    return token


def precheck(version: str, force: bool) -> None:
    """
    Pre check the version string for known good patterns
    """
    versionComponents = version.split(".")

    if len(versionComponents) != 3:
        warning_or_error(
            "Version does not have 3 expected components [major].[minor].[build]", force
        )

    lastComponent = versionComponents[-1]
    lastCharacter = lastComponent[-1]

    if not lastCharacter.islower():
        warning_or_error(
            f"Pre-releases are expected to have a letter at the end of the last version component. Got '{lastComponent}'",
            force,
        )


def getImageList(version: str) -> List[Dict[str, Any]]:
    """
    Returns the yaml file containing image definitions for the given version
    """
    requestURL = (
        f"https://raw.githubusercontent.com/osism/sbom/main/{version}/openstack.yml"
    )
    response = requests.get(requestURL)

    if response.status_code != 200:
        error_and_fail(
            f"Request {requestURL} returned with status code {response.status_code}"
        )

    y = yaml.load(response.text, Loader=yaml.SafeLoader)

    if not isinstance(y, dict):
        error_and_fail("Response yaml is not a dictionary")

    if not "images" in y:
        error_and_fail("Response yaml is missing the 'images' list")

    return y["images"]


def getImageMeta(imageObject: Dict[str, Any], force: bool) -> str:
    """
    Parses the image meta data
    """
    if not "image" in imageObject:
        error_and_fail("Image object has no attribute 'image'")

    image = imageObject["image"]

    if not image.startswith(IMAGE_PREFIX):
        warning_or_error(
            f"Image '{image}' does not start with known image prefix '{IMAGE_PREFIX}'",
            force,
        )

    imageMeta = image.split("/")[-1]

    if not ":" in imageMeta:
        error_and_fail(f"{imageMeta} does not contain a version string")

    return imageMeta.split(":")


def getImageDecision(imageRemoveURL: str, no_confirm: bool) -> bool:
    """
    Gets a user confirmation (yes) depending on --confirm flag
    """
    if no_confirm:
        return True

    decision = None

    while decision == None:
        i = input(f"Confirm removal of image '{imageRemoveURL}': [yes/no] ")
        if i == "yes":
            decision = True
        elif i == "no":
            decision = False
        else:
            decision = None

    return decision


def removeImage(token: str, imageName: str, imageVersion: str) -> None:
    """
    Uses an API call to quay.io to remove the given image tag
    """
    apiURL = f"{QUAY_BASE_API}/{imageName}/tag/{imageVersion}"
    headers = {"content-type": "application/json", "Authorization": f"Bearer {token}"}

    response = requests.delete(apiURL, headers=headers)

    if response.status_code not in {204, 404}:
        error_and_fail(
            f"Removal request failed with: {response.status_code} '{response.text}'"
        )

    if response.status_code == 404:
        logger.warning("Image already gone...")
    else:
        logger.info("Removal completed")


if __name__ == "__main__":
    typer.run(main)
