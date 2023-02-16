import get_ansible_requirements
import get_apt_requirements
import get_apt_deb_list
import get_container_requirements
import get_pypi_requirements
# import repo_manager

# repo_manager.clone_repos(user="osism")

ansible_requirements = get_ansible_requirements.get_requirements()
apt_requirements = get_apt_requirements.get_requirements()
apt_deb_list = get_apt_deb_list.get_deb_list()
container_requirements = get_container_requirements.get_requirements()
pypi_requirements = get_pypi_requirements.get_requirements()

# repo_manager.delete_repos()
