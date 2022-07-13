import yaml


def get_requirements() -> list:
    container_list = []

    with open("./container-mirror-manuals.yaml", "r") as stream:
        try:
            content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    for mirror in content['mirrors']:
        for path in mirror["paths"]:
            item = {
                "name": f"{mirror['url'].replace('https://', '').replace('.', '-')}-{path.replace('/', '-')}",
                "url": mirror["url"],
                "path": path
            }
            container_list.append(item)

    return container_list
