import re
import os
import sys
from os.path import isdir, isfile, join, expanduser

def find_subcommands(app_name, extra_dirs=None, include_others=True):
    """
    Shamelessly modified from conda.

    Get the list of subcommands for a given application. Currently, this
    searches the bin directory of the python installation and extra passed
    in directores. These will be scripts named starting with app_name-cmd_name
    """
    # TODO: make sure system paths are being searched
    # TODO: the path may need to be passed back as if the command is not on the
    #       system path, executing it will be hard...
    if include_others:
        if sys.platform == 'win32':
            dir_paths = [join(sys.prefix, 'Scripts'),
                         'C:\\cygwin\\bin']
        else:
            dir_paths = [join(sys.prefix, 'bin')]
    else:
        dir_paths = []

    if extra_dirs:
        dir_paths += extra_dirs

    if sys.platform == 'win32':
        pat = re.compile(r'%s-([\w\-]+)\.(exe|bat)$' % (app_name))
    else:
        pat = re.compile(r'%s-([\w\-]+)$' % (app_name))

    res = set()
    for dir_path in dir_paths:
        if not isdir(dir_path):
            continue
        for fn in os.listdir(dir_path):
            if not isfile(join(dir_path, fn)):
                continue
            m = pat.match(fn)
            if m:
                res.add(m.group(1))
    return sorted(res)
