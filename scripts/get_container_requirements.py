import glob


def find_requirements_files(file: str) -> list:
    return glob.glob(f"repos/**/{file}", recursive=True)


def get_containerfiles() -> list:
    image_list = []
    for file in find_requirements_files("Containerfile*"):
        with open(file) as stream:
            content = stream.read().splitlines()

        for line in content:
            if line.startswith("FROM"):
                image = line.removeprefix("FROM ").split(":")[0]

                if image not in image_list:
                    image_list.append(image)

    return sorted(image_list)


def get_ansible_files() -> list:
    image_list = []
    for file in find_requirements_files("*.yml") + find_requirements_files("*.yaml"):
        with open(file) as stream:
            content = stream.read().splitlines()

        for line in content:
            if "_image:" not in line:
                continue
            if ":" not in line:
                continue
            if line.split(":")[1] == "":
                continue
            if line.startswith(" "):
                continue

            foo = line[line.index(":") + 1:].lstrip()
            foo = foo.lstrip('"')
            foo = foo.rstrip('"')
            foo = foo.split("/")[-1]
            foo = foo.split(":")[0]

            if "images[" in foo:
                continue

            if "{" in foo:
                manual_images = [
                    "mariadb-server",
                    "mariadb",
                    "prometheus-server",
                    "prometheus-v2-server",
                    "debian-source-panko-api",
                    "debian-binary-panko-api",
                    "ubuntu-source-panko-api",
                    "ubuntu-binary-panko-api",
                    "centos-source-panko-api",
                    "centos-binary-panko-api",
                ]

                for item in manual_images:
                    if item not in image_list:
                        image_list.append(item)
                continue

            if foo not in image_list:
                image_list.append(foo)

    return sorted(image_list)


def get_requirements() -> list:
    container_files = []
    for i in get_containerfiles():
        if i not in container_files:
            container_files.append(i)
    for i in get_ansible_files():
        if i not in container_files:
            container_files.append(i)
    return sorted(container_files)
