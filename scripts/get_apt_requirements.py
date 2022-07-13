import glob
import yaml


def find_requirements_files(file: str) -> list:
    return glob.glob(f"repos/**/{file}", recursive=True)


def deep_analyse_yaml(package_list: list, file: str) -> list:
    # load file content
    with open(file, "r") as stream:
        try:
            content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    if type(content) is not list:
        print(f"not a valid yaml file: {file}")

    # if playbook-file
    if "hosts" in content[0]:
        #print("playbook")
        pass
    # else we try to read it as a task-file
    else:
        for item in content:
            # filter out all apt_ tasks like apt_cache
            if "ansible.builtin.apt_" in item:
                continue
            # filter out all other tasks
            if "ansible.builtin.apt" not in item:
                continue

            # filter out all apt tasks without a name key
            if "name" not in item["ansible.builtin.apt"]:
                continue

            package_value = item["ansible.builtin.apt"]["name"]

            # check if name is from loop:
            if "item" in package_value and "loop" in item:
                # with_items should not be used any more, therefore ignoring it.
                for package in item['loop']:
                    if package not in package_list:
                        package_list.append(package)
            else:
                # create a fake-list to produce less code
                if type(package_value) is str:
                    package_value = [package_value]

                # now treat everything as a list:
                for package in package_value:
                    foo = package.split("=")[0]
                    # if it's a variable, try to find the value of it
                    if foo.startswith("{{"):
                        bar = foo.split(" ")[1]
                        for file in find_requirements_files("*.yml") + find_requirements_files("*.yaml"):
                            with open(file) as stream:
                                content = stream.read().splitlines()

                            for line in content:
                                if f"{bar}:" not in line:
                                    continue

                                if len(line.split(" ")) < 2:
                                    continue

                                baz = line[line.index(":") + 1:].lstrip()
                                if "{{" not in baz:
                                    if baz not in package_list:
                                        package_list.append(baz)
                                else:
                                    if "docker-ce" in baz:
                                        continue

                                    print(baz) 
                    else:
                        if foo not in package_list:
                            package_list.append(foo)

    return package_list


def get_yaml() -> list:
    result = []
    for file in find_requirements_files("*.yml") + find_requirements_files("*.yaml"):
        with open(file) as stream:
            content = stream.read().splitlines()

        for line in content:
            if "apt" in line:
                if "- name:" in line:
                    continue
                if "apt_" in line:
                    continue
                if "_apt" in line:
                    continue
                if "aptly" in line:
                    continue
                if "url" in line:
                    continue
                if "deb" in line:
                    continue
                if "ANXS" in line:
                    continue
                if "/apt" in line:
                    continue
                if "_password" in line:
                    continue

                foo = line.lstrip()

                if foo.startswith("#"):
                    continue
                if foo.startswith("src"):
                    continue
                if "apt-daily" in foo:
                    continue

                if "builtin.apt" in foo:
                    result = deep_analyse_yaml(result, file)

                if foo.startswith("name: "):
                    if foo.split(" ")[1] not in result:
                        result.append(foo.split(" ")[1])
                if "ansible.builtin.raw" in foo:
                    bar = foo.split(" ")[-1].split(")")[0]
                    if bar not in result:
                        result.append(bar)

    return result


def get_requirements() -> list:
    package_list = []

    # WATCH OUT - THIS LIST STILL CONTAINS VARIABLES
    package_list = package_list + get_yaml()
    # package_list = package_list + get_j2()
    # package_list = package_list + get_sh()
    # package_list = package_list + get_mako()
    # package_list = package_list + get_userdata()
    # package_list = package_list + get_containerfile()

    # remove duplicate entries
    result = []
    for item in package_list:
        if item not in result:
            #print(item)
            result.append(item)

    return sorted(result)


# file types:
# - *.yml
# - *.yaml
# - *.j2
# - Containerfile
# - *.sh
# - *.mako
# - user-data
