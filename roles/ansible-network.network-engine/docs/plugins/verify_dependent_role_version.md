# Plugin verify_dependent_role_version


The `verify_dependent_role_version` plugin checks for required minimum version of dependant roles.
The plugin works only inside a role. It verifies the required minimum version of all roles are
installed as defined under dependancies in meta/main.yml of the role.

## How to Use

meta/main.yml

```yaml
dependencies:
  - src: ansible-network.network-engine
    version: v2.7.2
```

tasks/main.yml

```yaml
- name: Validate we have required minimum version of dependent roles installed
  verify_dependent_role_version:
    role_path: "{{ role_path }}"
```
