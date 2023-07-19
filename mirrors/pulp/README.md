# Pulp

* https://pulpproject.org

## Start service

* https://pulpproject.org/pulp-in-one-container/

Prepare the following directories. It should be on a block device which
provides enough storage capacity (> 1 TByte).

```
mkdir settings pulp_storage pgsql containers
```

Create ``settings/settings.py`` with the following content.

```
CONTENT_ORIGIN='http://osism.pulp.regio.digital:8080'
ANSIBLE_API_HOSTNAME='http://osism.pulp.regio.digital:8080'
ANSIBLE_CONTENT_HOSTNAME='http://osism.pulp.regio.digital:8080/pulp/content'
CACHE_ENABLED=True
FORCE_IGNORE_MISSING_PACKAGE_INDICES=True
```

Install required packages.

```
sudo apt-get install -y podman python3-pip
```

Start the service.

```
podman run --detach \
  --publish 8080:80 \
  --name pulp \
  --volume "$(pwd)/settings":/etc/pulp \
  --volume "$(pwd)/pulp_storage":/var/lib/pulp \
  --volume "$(pwd)/pgsql":/var/lib/pgsql \
  --volume "$(pwd)/containers":/var/lib/containers \
  --device /dev/fuse \
  quay.io/pulp/pulp
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
```

Check/Edit the content of ``.config/pulp/cli.toml``.

```
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

## Ansible collections & roles

Run the ``ansible.sh`` script to prepare and sync all defined roles and
collections.

### Ansible configuration

```
# Mirrored content on Pulp can be viewed and extended in the following
# repository: https://github.com/osism/sbom/tree/main/mirrors/pulp

[galaxy]
server_list = osism,galaxy

[galaxy_server.osism]
url = http://osism.pulp.regio.digital:8080/pulp/content/ansible/

[galaxy_server.galaxy]
url = https://galaxy.ansible.com/
```

## Ubuntu/Debian packages

### Ubuntu 22.04 (Focal)

Run ``ubuntu.py`` to prepare and sync all defined roles and collections.
The sync takes some time because a lot of data has to be transferred.

```
python3 ubuntu.py
```
