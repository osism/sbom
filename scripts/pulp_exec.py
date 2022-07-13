import subprocess


def cmd_wrapper(commands: list) -> None:
    print("*" * 42)
    for command in commands:
        print(f"COMMAND: {command}")
        process = subprocess.run(
            command.split(" "),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        print(process.stdout)


def ansible(mirror_list: list) -> None:
    # Pull-through cache is not possible yet, so we need to mirror only special namespaces. No auto-publication.

    for role in mirror_list["roles"]:
        print(role)
        name = role["name"]
        url = ["src"]
        commands = []
        commands.append(f"pulp ansible repository create --name {name}")
        commands.append(f"pulp ansible remote -t role create --name {name} --url {url}")
        commands.append(f"pulp ansible repository sync --name {name} --remote role:{name}")
        commands.append(f"pulp ansible distribution create --name {name} --base-path {name} --repository {name}")
        cmd_wrapper(commands)

    for collection in mirror_list["collections"]:
        name = collection["name"]
        url = collection["source"]
        commands = []
        commands.append(f"pulp ansible repository create --name {name}")
        commands.append(f"pulp ansible remote -t collection create --name {name} --url {url}")
        commands.append(f"pulp ansible repository sync --name {name} --remote collection:{name}")
        commands.append(f"pulp ansible distribution create --name {name} --base-path {name} --repository {name}")
        #cmd_wrapper(commands)


def container(mirror_list: list) -> None:
    # Pull-through cache is not possible yet, so we need to mirror only special namespaces. No auto-publication.

    for mirror in mirror_list:
        name = mirror['name']
        url = mirror['url']
        path = mirror['path']
        commands = []
        commands.append(f"pulp container repository create --name {name}")
        commands.append(f"pulp container remote create --name {name} --url {url} --upstream-name {path}")
        commands.append(f"pulp container repository sync --name {name} --remote {name}")
        commands.append(f"pulp container distribution create --name {name} --base-path {name} --repository {name}")
        if path.endswith("osism"):
            print(commands)
        
        #cmd_wrapper(commands)


def debian(mirror_list: list) -> None:
    # Pull-through cache is available. No auto-publication.

    for mirror in mirror_list:
        commands = []
        name = mirror["name"]
        url = mirror["url"]

        commands.append(f"pulp deb repository create --name {name}")

        args = "--architecture amd64"
        for distribution in mirror["distributions"]:
            args = f"{args} --distribution {distribution}"

        if "components" in mirror:
            for component in mirror["components"]:
                args = f"{args} --component {component}"

        commands.append(f"pulp deb remote create --name {name} --url {url} {args}")
        commands.append(f"pulp deb repository sync --name {name} --mirror --remote {name}")
        commands.append(f"pulp deb distribution create --name {name} --base-path {name} --repository {name}")
        commands.append(f"pulp deb publication create --repository {name} --structured True")
        cmd_wrapper(commands)


def pypi():
    # Pull-through cache is available. Auto-publication active.
    commands = []
    commands.append("pulp python repository create --name 'pypi-mirror' --autopublish")
    commands.append("pulp python remote create --name 'pypi-mirror' --url https://pypi.org/ --includes '[\"shelf-reader\", \"pip-tools>=1.12,<=2.0\"]' --excludes '[\"django~=1.0\", \"scipy\"]'")
    commands.append("pulp python repository sync --name 'pypi-mirror' --remote 'pypi-mirror'")
    commands.append("pulp python distribution create --name 'pypi-mirror-latest' --base-path 'pypi-mirror' --repository 'pypi-mirror' --remote 'pypi-mirror'")
    cmd_wrapper(commands)


# Do this if  a mirror has no auto-publish feature
# (...) repository sync (...)
# (...) distribution create (...)
# (...) publication create (...)
# One repository can only have one remote related
