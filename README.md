# Pulp

## Client configuration

In order to use your pulp installation, the individual clients have to point to them. Below you'll find a list of how to configure the clients to use your pulp installation.

For convenience we'll use `pulp.services.osism.tech` as the hostname for the example pulp service.

### Ansible

Use the following to pull roles and collections from your pulp-host:

```sh
ansible-galaxy install elasticsearch,6.2.4 -s https://pulp.services.osism.tech/pulp_ansible/galaxy/my_content/
```

If your pulp installation is not secured with SSL you have to allow this within the command:

```sh
ansible-galaxy install elasticsearch,6.2.4 -c -s http://pulp.services.osism.tech/pulp_ansible/galaxy/my_content/
```

Alternatively you can configure this in the various locations of your `ansible.cfg` file (`~/.ansible.cfg`, `/etc/ansible/ansible.cfg`, `./ansible.cfg`):

```ini
[galaxy]
server_list = my_server, my_second_server

[galaxy_server.my_server]
url=http://pulp.example.com/pulp_ansible/galaxy/my_content/
username=foo
password=bar

[galaxy_server.my_second_server]
url=http://pulp.example.com/pulp_ansible/galaxy/my_content/
token=foobar
#and some more parameters if required
```

### DEB

Use the following to fetch deb packages from your pulp-host by configuring `/etc/apt/sources.list` or similar:

```list
deb [trusted=yes arch=amd64,arm64 arch-=i386,armel,armhf] https://pulp.services.osism.tech/pulp/content/nginx/ default  all
```

### Container

Use the following to pull containers from your pulp-host:

```sh
docker pull pulp.services.osism.tech/my-image:latest
docker run -d pulp.services.osism.tech/my-image:latest bash
```

If your pulp installation is not secured with SSL you have to allow this to your container engine. For docker modify (or create first) `/etc/docker/daemon.json`:

```json
{
  "insecure-registries" : ["pulp.services.osism.tech"]
}
```

### PyPI

Use the following to fetch python packages from your pulp-host:

```sh
pip install localhost -i https://pulp.services.osism.tech/pypi/foo/simple/ shelf-reader
```

If your pulp installation is not secured with SSL you have to allow this within the command:

```sh
pip install --trusted-host pulp.services.osism.tech -i https://pulp.services.osism.tech/pypi/foo/simple/ shelf-reader
```

Alternatively you can configure your `pip.conf` file:

```ini
[global]
index-url = https://pulp.services.osism.tech/pypi/foo/simple/
#trusted-host = pulp.services.osism.tech  # if no SSL is available
```

## Server configuration

## Server updating
