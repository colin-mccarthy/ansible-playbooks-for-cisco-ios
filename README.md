# Ansible-Playbooks-for-Cisco-IOS


Mission:

Ansible-Playbooks-for-Cisco-IOS is a repository of Ansible Playbooks for Cisco IOS devices.

To use, download the .zip and extract the contents or clone the repository by typing

```git clone https://github.com/colin-mccarthy/ansible-playbooks-for-cisco-ios.git```



Your host vars should look something like this if you're using Ansible >= 2.5

```yaml


ansible_pass=foo
ansible_user=foo
ansible_network_os=ios
ansible_connection=network_cli

# If using an enable password add these

ansible_become_pass=foo
ansible_become=yes
ansible_become_method=enable


```

Here is a link to a blog explaining the changes that took place for Ansible 2.5

https://www.ansible.com/blog/coming-soon-networking-features-in-ansible-2.5





