# (c) 2019, Ansible Inc,
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import yaml
import copy
import re

from ansible import constants as C
from ansible.module_utils._text import to_text
from ansible.playbook.role.requirement import RoleRequirement
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display


display = Display()


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(task_vars=task_vars)
        self.META_MAIN = os.path.join('meta', 'main.yml')
        self.META_INSTALL = os.path.join('meta', '.galaxy_install_info')

        try:
            role_path = self._task.args.get('role_path')
            role_root_dir = os.path.split(role_path)[0]
        except KeyError as exc:
            return {'failed': True, 'msg': 'missing required argument: %s' % exc}

        # Get dependancy version dict if not encoded in meta
        depends_dict = self._task.args.get('depends_map')

        try:
            self._depends = self._get_role_dependencies(role_path)
            # check if we know min_version for each dependant role
            # from meta file or through user input to this plugin
            (rc, msg) = self._check_depends(self._depends, depends_dict)
            if not rc:
                result['failed'] = True
                result['msg'] = msg
                return result
            default_roles_path = copy.copy(C.DEFAULT_ROLES_PATH)
            default_roles_path.append(role_root_dir)
            (rc, msg) = self._find_dependant_role_version(
                self._depends, default_roles_path)

            if rc == 'Error':
                result['failed'] = True
                result['msg'] = msg
            elif rc == 'Warning':
                result['changed'] = True
                result['Warning'] = True
                result['msg'] = msg
            elif rc == 'Success':
                result['changed'] = False
                result['msg'] = msg
        except Exception as exc:
            result['failed'] = True
            result['msg'] = ('Exception received : %s' % exc)

        return result

    def _get_role_dependencies(self, role_path):
        role_dependencies = []
        dep_info = None
        meta_path = os.path.join(role_path, self.META_MAIN)
        if os.path.isfile(meta_path):
            try:
                f = open(meta_path, 'r')
                metadata = yaml.safe_load(f)
                role_dependencies = metadata.get('dependencies') or []
            except (OSError, IOError):
                display.vvv("Unable to load metadata for %s" % role_path)
                return False
            finally:
                f.close()
        if role_dependencies:
            for dep in role_dependencies:
                dep_req = RoleRequirement()
                dep_info = dep_req.role_yaml_parse(dep)

        return dep_info

    def _find_dependant_role_version(self, dep_role, search_role_path):
        found = False
        dep_role_list = []
        if isinstance(dep_role, dict):
            # single role dependancy
            dep_role_list.append(dep_role)
        else:
            dep_role_list = dep_role

        # First preferrence is to find role in defined C.default_roles_path
        for roles in dep_role_list:
            for r_path in search_role_path:
                dep_role_path = os.path.join(r_path, roles['name'])
                if os.path.exists(dep_role_path):
                    found = True
                    install_ver = self._get_role_version(dep_role_path)
                    if install_ver == 'unknown':
                        msg = "WARNING! : role: %s installed version is unknown " \
                              "please check version if you downloded it from scm" % roles['name']
                        return ("Warning", msg)
                    if install_ver < roles['version']:
                        msg = "Error! : role: %s installed version :%s is less than " \
                              "required version: %s" % (roles['name'],
                                                        install_ver, roles['version'])
                        return ("Error", msg)
            if not found:
                msg = "role : %s is not installed in role search path: %s" \
                      % (roles['name'], search_role_path)
                return ("Error", msg)

        return ("Success", 'Success: All dependent roles meet min version requirements')

    def _check_depends(self, depends, depends_dict):
        depends_list = []
        if isinstance(depends, dict):
            # single role dependancy
            depends_list.append(depends)
        else:
            depends_list = depends
        for dep in depends_list:
            if dep['version'] and depends_dict is None:
                # Nothing to be done. Use version from meta
                return (True, '')
            if dep['version'] is None and depends_dict is None:
                msg = "could not find min version from meta for dependent role : %s" \
                      " you can pass this info as depends_map arg e.g." \
                      "depends_map: - name: %s \n version: 2.6.5" \
                      % (dep['name'], dep['name'])
                return (False, msg)
            # Galaxy might return empty string when meta does not have version
            # specified
            if dep['version'] == '' and depends_dict is None:
                msg = "could not find min version from meta for dependent role : %s" \
                      " you can pass this info as depends_map arg e.g." \
                      "depends_map: - name: %s \n version: 2.6.5" \
                      % (dep['name'], dep['name'])
                return (False, msg)
            for in_depends in depends_dict:
                if in_depends['name'] == dep['name']:
                    if in_depends['version'] is None:
                        msg = 'min_version for role_name: %s is Unknown' % dep['name']
                        return (False, msg)
                    else:
                        ver = to_text(in_depends['version'])
                        # if version is defined without 'v<>' add 'v' for
                        # compliance with galaxy versioning
                        galaxy_compliant_ver = re.sub(r'^(\d+\..*)', r'v\1', ver)
                        dep['version'] = galaxy_compliant_ver
        return (True, '')

    def _get_role_version(self, role_path):
        version = "unknown"
        install_info = None
        info_path = os.path.join(role_path, self.META_INSTALL)
        if os.path.isfile(info_path):
            try:
                f = open(info_path, 'r')
                install_info = yaml.safe_load(f)
            except (OSError, IOError):
                display.vvv(
                    "Unable to load galaxy install info for %s" % role_path)
                return "unknown"
            finally:
                f.close()
        if install_info:
            version = install_info.get("version", None)
        return version
