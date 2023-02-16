import yaml


def get_deb_list() -> list:
    deb_list = []

    with open("./apt-mirror-manuals.yaml", "r") as stream:
        try:
            content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    for mirror in content['mirrors']:
        if mirror not in deb_list:
            deb_list.append(mirror)

    return sorted(deb_list)
