import glob


def find_requirements_files(file: str) -> list:
    return glob.glob(f"repos/**/{file}", recursive=True)


def get_requirements() -> list:
    package_list = []
    for file in find_requirements_files("requirements.txt"):
        with open(file) as stream:
            content = stream.read().splitlines()

        for line in content:
            # strip away version pinnings
            package = line.split("=")[0].split("<")[0].split(">")[0]
            # ignore comments
            if package.startswith("#"):
                continue
            # ignore empty lines
            if package == "":
                continue

            if package not in package_list:
                package_list.append(package)

    return sorted(package_list)
