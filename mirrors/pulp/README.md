# Pulp

* https://pulpproject.org

## Start service

* https://pulpproject.org/pulp-in-one-container/

```
mkdir settings pulp_storage pgsql containers
```

```
CONTENT_ORIGIN='http://osism.pulp.regio.digital:8080'
ANSIBLE_API_HOSTNAME='http://osism.pulp.regio.digital:8080'
ANSIBLE_CONTENT_HOSTNAME='http://osism.pulp.regio.digital:8080/pulp/content'
CACHE_ENABLED=True
FORCE_IGNORE_MISSING_PACKAGE_INDICES=True
```

```
podman run --detach \
  --publish 8080:80 \
  --name pulp \
  --volume "$(pwd)/settings":/etc/pulp \
  --volume "$(pwd)/pulp_storage":/var/lib/pulp \
  --volume "$(pwd)/pgsql":/var/lib/pgsql \
  --volume "$(pwd)/containers":/var/lib/containers \
  --device /dev/fuse \
  pulp/pulp
```

The start of the service will take some minutes. Check with ``pulp logs``.

```
Calling /etc/init/pulpcore-worker
[2023-07-18 15:21:55 +0000] [12650] [INFO] Starting gunicorn 20.1.0
[2023-07-18 15:21:55 +0000] [12650] [INFO] Listening at: http://127.0.0.1:24817 (12650)
[2023-07-18 15:21:55 +0000] [12650] [INFO] Using worker: sync
[2023-07-18 15:21:55 +0000] [12697] [INFO] Booting worker with pid: 12697
[2023-07-18 15:21:55 +0000] [12698] [INFO] Booting worker with pid: 12698
[2023-07-18 15:21:55 +0000] [12646] [INFO] Starting gunicorn 20.1.0
[2023-07-18 15:21:55 +0000] [12646] [INFO] Listening at: http://127.0.0.1:24816 (12646)
[2023-07-18 15:21:55 +0000] [12646] [INFO] Using worker: aiohttp.GunicornWebWorker
[2023-07-18 15:21:55 +0000] [12700] [INFO] Booting worker with pid: 12700
[2023-07-18 15:21:55 +0000] [12701] [INFO] Booting worker with pid: 12701
```

Reset the admin password.

```
podman exec -it pulp bash -c 'pulpcore-manager reset-admin-password'
Please enter new password for user "admin":
Please enter new password for user "admin" again:
Successfully set password for "admin" user.
```

Check the status.

```
curl localhost:8080/pulp/api/v3/status/
```

## Prepare usage

Install and configure the CLI.

```
pip3 install pulp-cli pulp-cli-deb
pulp config create -e
cat .config/pulp/cli.toml
[cli]
base_url = "http://localhost:8080"
api_root = "/pulp/"
domain = "default"
username = "admin"
password = "password"
cert = ""
key = ""
verify_ssl = true
format = "json"
dry_run = false
timeout = 0
verbose = 0
```

Create a mirror user.

```
pulp user create --username mirror --password password
```

## Ansible collections & roles

```
pulp user role-assignment add \
    --role ansible.ansibledistribution_viewer \
    --username mirror  \
    --object ""
```

Prepare the mirror repository.

```
pulp ansible repository create --name "mirror"
pulp ansible remote -t "collection" create \
    --name "ansible-galaxy" \
    --url "https://galaxy.ansible.com/" \
    --requirements @ansible-galaxy.yml
```

Start the synchronization (this will take some time).

```
pulp ansible repository sync \
    --name "mirror" \
    --remote "ansible-galaxy"
Started background task /pulp/api/v3/tasks/018969bd-cb4a-7601-8bfc-714ea4b657b1/
..........a lot of more points here.....Done.
```

Publish the mirror repository after the sync finished.

```
pulp ansible distribution create \
    --name "mirror" \
    --base-path "mirror" \
    --repository "mirror"
Started background task /pulp/api/v3/tasks/018969ca-899f-7cf5-9a97-b36570057350/
.......Done.
{
  "pulp_href": "/pulp/api/v3/distributions/ansible/ansible/018969ca-8a37-7e69-b478-82511c5a0ec6/",
  "pulp_created": "2023-07-18T16:17:08.664512Z",
  "base_path": "mirror",
  "content_guard": null,
  "name": "mirror",
  "repository": "/pulp/api/v3/repositories/ansible/ansible/018969bc-2f92-7c5d-909c-43d50b952b2f/",
  "repository_version": null,
  "client_url": "http://osism.pulp.regio.digital:8080/pulp_ansible/galaxy/mirror/",
  "pulp_labels": {}
}
```

### Add new collections

```
pulp ansible remote -t "collection" update \
    --name "ansible-galaxy" \
    --url "https://galaxy.ansible.com/" \
    --requirements @ansible-galaxy.yml
```

### Sync repository

```
pulp ansible repository sync \
    --name "mirror" \
    --remote "ansible-galaxy"
pulp ansible distribution destroy --name mirror
pulp ansible distribution create \
    --name "mirror" \
    --base-path "mirror" \
    --repository "mirror"
```

### Ansible configuration

```
# Mirrored content on Pulp can be viewed and extended in the following
# repository: https://github.com/osism/sbom/tree/main/mirrors/pulp
#
# The used account is only assigned viewer rights and we use this to
# provide access not completely public.

[galaxy]
server_list = mirror,galaxy

[galaxy_server.mirror]
url = http://osism.pulp.regio.digital:8080/pulp_ansible/galaxy/mirror/
username = mirror
password = password

[galaxy_server.galaxy]
url = https://galaxy.ansible.com/
```

## Ubuntu/Debian packages

### Ubuntu 22.04 (Focal)

```
python3 ubuntu.py
```
