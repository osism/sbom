import glob
import yaml


def find_requirements_files(file: str) -> list:
    return glob.glob(f"repos/**/{file}", recursive=True)


def get_galaxy_installs() -> dict:
    result = {
        "collections": [],
        "roles": [],
    }
    for file in find_requirements_files("*"):
        try:
            with open(file) as stream:
                content = stream.read().splitlines()
        except (UnicodeDecodeError, IsADirectoryError):
            continue

        for line in content:
            if "ansible-galaxy" in line and " install " in line:
                # skip if requirements file is presented
                if " -r " in line:
                    continue

                # remove leading spaces, trailing spaces and trailing backslashes
                foo = line.lstrip()
                foo = line.rstrip(" \\")

                # remove prefixes like RUN from Containerfiles
                foo = foo[foo.find('ansible-galaxy'):]

                # remove additional command parameters
                if " -v " in foo:
                    foo = foo.replace("-v ", "")
                if " -f " in foo:
                    foo = foo.replace("-f ", "")

                # remove -p parameter
                if " -p " in foo:
                    skip_p_value = False
                    new_foo = ""

                    # split string by " " and loop trough entries to build new string
                    for item in foo.split(" "):
                        # if -p is found, continue the loop without adding it and
                        # also set skip_p_value to True. This will trigger the below
                        # if statement to also skip the value of -p
                        if item == "-p":
                            skip_p_value = True
                            continue
                        # see explanation above
                        if skip_p_value:
                            skip_p_value = False
                            continue

                        # check if new_foo has a value. if so, add a space again
                        if new_foo != "":
                            new_foo = new_foo + " "
                        new_foo = new_foo + item
                    # write new_foo to foo. (foo without -p parameter)
                    foo = new_foo

                # remove --collections-path parameter
                if " --collections-path " in foo:
                    skip_p_value = False
                    new_foo = ""

                    # split string by " " and loop trough entries to build new string
                    for item in foo.split(" "):
                        # if --collections-path is found, continue the loop without adding it and
                        # also set skip_p_value to True. This will trigger the below
                        # if statement to also skip the value of --collections-path
                        if item == "--collections-path":
                            skip_p_value = True
                            continue
                        # see explanation above
                        if skip_p_value:
                            skip_p_value = False
                            continue

                        # check if new_foo has a value. if so, add a space again
                        if new_foo != "":
                            new_foo = new_foo + " "
                        new_foo = new_foo + item
                    # write new_foo to foo. (foo without --collections-path parameter)
                    foo = new_foo

                if " collection " in foo:
                    key = "collections"
                elif " role " in foo:
                    key = "roles"

                foo = foo.split(" ")[-1]

                if foo.startswith("git"):
                    if "osism" in foo:
                        version = "main"
                    elif "openstack" in foo:
                        version = "master"
                    elif "netbox" in foo:
                        version = "devel"
                    elif "stackhpc" in foo:
                        version = "master"
                    elif "ansible-collections" in foo:
                        version = "main"
                    item = {
                        "name": foo.split("+")[1].split(",")[0],
                        "source": foo.split("+")[1].split(",")[0],
                        "type": "git",
                        "version": version,
                    }
                else:
                    item = {
                        "name": foo.split(",")[0],
                        "source": "https://galaxy.ansible.com",
                    }
                result[key].append(item)

    return result


def get_requirements_files() -> list:
    result = {
        "collections": [],
        "roles": [],
    }
    for file in find_requirements_files("*.yml") + find_requirements_files("*.yaml"):
        if "requirement" not in file:
            continue

        try:
            with open(file) as stream:
                content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

        if "collections" in content:
            for collection in content["collections"]:
                if "source" not in collection:
                    content["collections"][content["collections"].index(collection)]["source"] = content["collections"][content["collections"].index(collection)]["name"]
                    content["collections"][content["collections"].index(collection)]["name"] = content["collections"][content["collections"].index(collection)]["name"].split(".")[-2].replace("/", "-")
            result["collections"] = result["collections"] + content["collections"]

        if "roles" in content:
            result["roles"] = result["roles"] + content["roles"]

    return result


def get_requirements() -> dict:
    requirements = {
        "collections": [],
        "roles": [],
    }

    # get lists
    foo = get_requirements_files()
    bar = get_galaxy_installs()

    # concat both lists
    collections = foo["collections"] + bar["collections"]
    roles = foo["roles"] + bar["roles"]

    # remove duplicates
    roles = [dict(t) for t in {tuple(d.items()) for d in roles}]
    collections = [dict(t) for t in {tuple(d.items()) for d in collections}]

    requirements["roles"] = roles
    requirements["collections"] = collections

    return requirements
