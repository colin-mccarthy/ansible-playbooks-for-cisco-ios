# (c) 2018, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
import os

from itertools import chain

from ansible.module_utils.six import iteritems
from ansible.module_utils._text import to_bytes, to_text
from ansible.module_utils.network.common.utils import sort_list
from ansible.utils.display import Display
from ansible.utils.path import unfrackpath


display = Display()


def dict_merge(base, other):
    """ Return a new dict object that combines base and other

    This will create a new dict object that is a combination of the key/value
    pairs from base and other.  When both keys exist, the value will be
    selected from other.  If the value is a list object, the two lists will
    be combined and duplicate entries removed.

    :param base: dict object to serve as base
    :param other: dict object to combine with base

    :returns: new combined dict object
    """
    if not isinstance(base, dict):
        raise AssertionError("`base` must be of type <dict>")
    if not isinstance(other, dict):
        raise AssertionError("`other` must be of type <dict>")

    combined = dict()

    for key, value in iteritems(base):
        if isinstance(value, dict):
            if key in other:
                item = other.get(key)
                if item is not None:
                    if isinstance(other[key], dict):
                        combined[key] = dict_merge(value, other[key])
                    else:
                        combined[key] = other[key]
                else:
                    combined[key] = item
            else:
                combined[key] = value
        elif isinstance(value, list):
            if key in other:
                item = other.get(key)
                if item is not None:
                    try:
                        combined[key] = list(set(chain(value, item)))
                    except TypeError:
                        value.extend([i for i in item if i not in value])
                        combined[key] = value
                else:
                    combined[key] = item
            else:
                combined[key] = value
        else:
            if key in other:
                other_value = other.get(key)
                if other_value is not None:
                    if sort_list(base[key]) != sort_list(other_value):
                        combined[key] = other_value
                    else:
                        combined[key] = value
                else:
                    combined[key] = other_value
            else:
                combined[key] = value

    for key in set(other.keys()).difference(base.keys()):
        combined[key] = other.get(key)

    return combined


def generate_source_path(paths, source):
    """
    Find file in first path in stack.

    :param paths: A list of text strings which are the path to look for the filename in.
    :param src: A text string which is the filename to search for.
    :rtype: A text string.
    :returns: An absolute path to the filename ``src`` if found.
    """

    b_source = to_bytes(source)

    result = None
    search = []

    if source.startswith('~') or source.startswith(os.path.sep):
        # path is absolute, no relative needed, check existence and return source
        test_path = unfrackpath(b_source, follow=False)
        if os.path.exists(to_bytes(test_path, errors='surrogate_or_strict')):
            result = test_path

    else:
        for path in paths:
            upath = unfrackpath(path, follow=False)
            b_upath = to_bytes(upath, errors='surrogate_or_strict')
            search.append(os.path.join(b_upath, b_source))

        for candidate in search:
            display.vvvvv(u'looking for "%s" at "%s"' % (source, to_text(candidate)))
            if os.path.exists(candidate) and os.path.isfile(candidate):
                result = to_text(candidate)
                break

    return result
