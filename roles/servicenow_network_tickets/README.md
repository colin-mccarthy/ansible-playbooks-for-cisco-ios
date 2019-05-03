# servicenow_network_tickets
Ansible role for ServiceNow network tickets

Currently supports network devices that are running on Cisco IOS.


Example Playbook:

```

- hosts: ios
  gather_facts: no


  vars:

    snmp_server:
      - snmp-server community ansibull RO 99
      - snmp-server trap-source Loopback0
      - snmp-server contact noc@yourcompany.com
      - snmp-server enable traps ospf state-change
      - snmp-server enable traps ospf errors
      - snmp-server enable traps ospf retransmit
      - snmp-server enable traps ospf lsa
      - snmp-server host 192.168.161.110 version 2c public udp-port 161



  tasks:

  - name: get the current snmp-server config
    ios_command:
      commands:
        - "show running-config full | include snmp-server"
    register: get_config

  - debug: var=get_config.stdout_lines

  - name: set snmp commands
    with_items: "{{ snmp_server }}"
    ios_config:
      lines:
        - "{{ item }}"
    register: set_snmp

  - name: remove snmp commands
    when: "(get_config.stdout_lines[0] != '') and (item not in snmp_server)"
    with_items: "{{ get_config.stdout_lines[0] }}"
    register: remove_snmp
    ios_config:
      lines:
        - "no {{ item }}"

  - name: servicenow_network_tickets
    when: set_snmp.changed or remove_snmp.changed
    import_role:
      name: servicenow_network_tickets

```

Example Inventory:


```
[ios]
192.168.161.9  ansible_ssh_host=192.168.161.9  

[ios:vars]

ansible_network_os=ios
ansible_connection=network_cli
```





Make sure you create the `device uptime` & `ios version` fields in your ServiceNow incident template.
 This is exaplained in the blog post below.

The `hostname` parameter has now also been added in the data section of the API call. Make sure to create that field in your incident template in SNOW.

https://www.thenetwork.engineer/blog/utilize-ansible-for-opening-and-closing-tickets-with-servicenow-part3
