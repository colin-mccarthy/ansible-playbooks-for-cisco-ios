# Ansible-Playbooks-for-Cisco-IOS


Mission

Ansible-Playbooks-for-Cisco-IOS is a repository of Ansible Playbooks for Cisco IOS devices.

To use, download the .zip and extract the contents or clone the repository by typing

```git clone https://github.com/colin-mccarthy/Ansible-Playbooks-for-Cisco-IOS.git```



With the network changes in Ansible 2.5 you need to set up your group vars for your ios group like this.

```
ansible_ssh_pass=foo
ansible_become_pass=foo
remote_user=foo
ansible_network_os=ios
ansible_connection=network_cli
```







